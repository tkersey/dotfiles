#!/usr/bin/env -S uv run python
"""Owner-controlled, source-preserving retired Learnings import (Ledger 1.3).

No storage discovery and no direct event writes. The caller supplies custody.
Inspect is read-only; apply validates every input and reconciles every ID before
its first native append. Unknown/malformed records never become skipped rows.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

MAX_SOURCE = 64 * 1024 * 1024
MAX_PACKET = 1024 * 1024
MAX_RECORDS = 100000
DEFINITION = Path(__file__).resolve().parents[1] / 'definitions/ledger/learnings-protocol.json'


class ImportErrorDetail(RuntimeError):
    pass


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ImportErrorDetail(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def invalid_constant(value: str) -> None:
    raise ImportErrorDetail(f'Non-JSON numeric constant: {value}')


def read_source(path: Path) -> bytes:
    # Check before resolve() can hide a link, and reject devices/FIFOs.
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ImportErrorDetail(f'Symlink source: {part}')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ImportErrorDetail(f'Not a regular source: {path}')
        raw = stream.read(MAX_SOURCE + 1)
    if len(raw) > MAX_SOURCE:
        raise ImportErrorDetail(f'Source exceeds {MAX_SOURCE} bytes: {path}')
    return raw


def frame(raw: bytes, control: dict | None = None) -> tuple[list[dict], dict]:
    """Parse consecutive JSON objects, retaining original byte-addressed provenance.

    Explicit source-digest-bound framing controls can insert ONLY the missing
    opening quote on a tags key, or retain a declared anonymous fragment. They
    cannot rewrite values. Never infer repairs from a parser error.
    """
    digest = hashlib.sha256(raw).hexdigest()
    controls = {'source_sha256': digest, 'spans': []} if control is None else control
    if not isinstance(controls, dict) or set(controls) != {'source_sha256', 'spans'} or controls['source_sha256'] != digest:
        raise ImportErrorDetail('Framing control does not identify this exact source')
    spans = controls['spans']
    if not isinstance(spans, list) or len(spans) > 128:
        raise ImportErrorDetail('Invalid framing control spans')
    edited = bytearray()
    cursor = 0
    offsets = []
    retained = []
    for span in spans:
        if not isinstance(span, dict) or set(span) != {'start', 'end', 'kind'}:
            raise ImportErrorDetail('Invalid framing span')
        start, end, kind = span['start'], span['end'], span['kind']
        if type(start) is not int or type(end) is not int or not cursor <= start < end <= len(raw):
            raise ImportErrorDetail('Overlapping, unordered, or out-of-range framing span')
        original = raw[start:end]
        edited.extend(raw[cursor:start])
        if kind == 'missing-tags-quote' and original == b'tags":':
            offsets.append((len(edited), 1))
            edited.extend(b'"' + original)
        elif kind == 'anonymous-fragment' and not any(
                json.loads(match.group(0)[:-1].strip()) == 'id'
                for match in re.finditer(rb'"(?:[^"\\]|\\.)*"\s*:', original)):
            # Same byte length makes original offsets unambiguous. Bytes remain
            # in the original source, caller archive, and this exact receipt.
            edited.extend(b' ' * len(original))
            retained.append({'start': start, 'end': end, 'base64': base64.b64encode(original).decode()})
        else:
            raise ImportErrorDetail('Unsupported repair or fragment containing an identified record')
        cursor = end
    edited.extend(raw[cursor:])
    text = bytes(edited).decode('utf-8')
    decoder = json.JSONDecoder(object_pairs_hook=unique, parse_constant=invalid_constant)
    position = 0
    byte_position = 0
    packets = []
    ids = set()
    framing_digest = hashlib.sha256(canonical(controls).encode()).hexdigest()
    while position < len(text):
        match = re.match(r'[ \t\r\n]*', text[position:])
        whitespace = match.group(0)
        position += len(whitespace)
        byte_position += len(whitespace.encode())
        if position == len(text):
            break
        start = byte_position
        try:
            record, end = decoder.raw_decode(text, position)
        except json.JSONDecodeError as exc:
            raise ImportErrorDetail(f'Unrecognized framing near original byte {start}; no records imported') from exc
        byte_position += len(text[position:end].encode())
        position = end
        if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not record['id'].strip():
            raise ImportErrorDetail(f'Expected an identified learning at byte {start}')
        if record['id'] in ids:
            raise ImportErrorDetail(f'Duplicate source ID: {record["id"]}')
        ids.add(record['id'])
        original_start = start - sum(length for offset, length in offsets if offset < start)
        original_end = byte_position - sum(length for offset, length in offsets if offset < byte_position)
        if any(fragment['start'] < original_end and fragment['end'] > original_start for fragment in retained):
            raise ImportErrorDetail('An anonymous fragment must be between records, never inside one')
        packet = {'v': 0, 'source': 'learnings', 'event': 'learning.import',
                  'learning_id': record['id'], 'status': record.get('status'), 'record': record,
                  'import_source': {'sha256': digest, 'record_index': str(len(packets)),
                                    'byte_start': str(original_start), 'byte_end': str(original_end),
                                    'framing_sha256': framing_digest}}
        if len(canonical(packet).encode()) > MAX_PACKET or len(packets) >= MAX_RECORDS:
            raise ImportErrorDetail('Historical packet/record bound exceeded')
        packets.append(packet)
    return packets, {'source_sha256': digest, 'framing_sha256': framing_digest,
                     'framing': controls, 'records': len(packets), 'retained_fragments': retained}


class Native:
    def __init__(self, binary: str, definition: Path, selector: list[str]):
        self.binary, self.definition, self.selector = binary, definition.resolve(strict=True), selector

    def run(self, command: str, *args: str, packet: dict | None = None, pure: bool = False) -> dict:
        argv = [self.binary, command, '--definition', str(self.definition),
                *([] if pure else self.selector), *args, '--format', 'json']
        if packet is not None:
            argv += ['--input', 'historical=-']
        proc = subprocess.run(argv, input=None if packet is None else canonical(packet).encode(), capture_output=True)
        try:
            result = json.loads(proc.stdout, object_pairs_hook=unique, parse_constant=invalid_constant)
        except (ValueError, UnicodeError) as exc:
            raise ImportErrorDetail(f'Invalid native {command} envelope') from exc
        if proc.returncode or not isinstance(result, dict):
            raise ImportErrorDetail(f'Native {command} failed: {proc.stdout.decode(errors="replace")[:8192]}')
        if result.get('authority_granted', result.get('semantic_authority_granted')) is not False:
            raise ImportErrorDetail(f'Missing native authority boundary: {command}')
        return result

    def records(self) -> tuple[dict[str, dict], str | None]:
        result = self.run('project', '--projection', 'import-records')
        if result.get('schema') != 'ledger-projection-result/v1' or not isinstance(result.get('data'), list):
            raise ImportErrorDetail('Unexpected full-record projection')
        index = {}
        for record in result['data']:
            if not isinstance(record, dict) or not isinstance(record.get('id'), str) or record['id'] in index:
                raise ImportErrorDetail('Ambiguous or duplicate canonical ID')
            index[record['id']] = record
        revision = result.get('store', {}).get('revision')
        if revision is not None and not isinstance(revision, str):
            raise ImportErrorDetail('Projection omitted witnessed store revision')
        if revision is None and index:
            raise ImportErrorDetail('Nonempty projection omitted witnessed revision')
        return index, revision


def import_sources(native: Native, sources: list[Path], *, apply: bool = False,
                   controls: dict[str, dict] | None = None, initialize_empty: bool = False) -> dict:
    if controls is not None and not isinstance(controls, dict):
        raise ImportErrorDetail('Framing controls must map source digests to declarations')
    packets = {}
    receipts = []
    snapshots = {}
    if len(sources) > 256:
        raise ImportErrorDetail('Source count bound exceeded')
    total_bytes = 0
    for source in sources:
        raw = read_source(source)
        total_bytes += len(raw)
        if total_bytes > MAX_SOURCE:
            raise ImportErrorDetail('Aggregate source byte bound exceeded')
        snapshots[source] = hashlib.sha256(raw).hexdigest()
        rows, receipt = frame(raw, (controls or {}).get(snapshots[source]))
        receipt['source'] = str(source)
        receipts.append(receipt)
        for row in rows:
            key = row['learning_id']
            previous = packets.get(key)
            if previous and canonical(previous['record']) != canonical(row['record']):
                raise ImportErrorDetail(f'Conflicting historical records: {key}')
            packets.setdefault(key, row)
            if len(packets) > MAX_RECORDS:
                raise ImportErrorDetail('Aggregate record bound exceeded')
    # Every packet, including already-present records, must satisfy the owner.
    for packet in packets.values():
        validated = native.run('validate', packet=packet, pure=True)
        if validated.get('schema') != 'ledger-validation-result/v1' or validated.get('valid') is not True:
            raise ImportErrorDetail(f'Invalid historical record: {packet["learning_id"]}')
    before, revision = native.records()
    for key, packet in packets.items():
        if key in before and canonical(before[key]) != canonical(packet['record']):
            raise ImportErrorDetail(f'Canonical ID conflict: {key}')
    missing = [packet for key, packet in packets.items() if key not in before]
    transactions = []
    if apply and missing and revision is None and not initialize_empty:
        raise ImportErrorDetail('Empty-store import requires separately authorized initialize_empty after writer quiescence')
    if apply:
        for source, digest in snapshots.items():
            if hashlib.sha256(read_source(source)).hexdigest() != digest:
                raise ImportErrorDetail(f'Source changed after preflight: {source}')
        for packet in missing:
            key = 'retired-' + hashlib.sha256(packet['learning_id'].encode()).hexdigest()
            operation = 'import-initialize' if revision is None else 'import-record'
            revision_args = [] if revision is None else ['--param', f'import_revision={revision}']
            result = native.run('transact', '--operation', operation, '--param', f'import_key={key}',
                                *revision_args, packet=packet)
            effects = result.get('effects')
            if (result.get('schema') != 'ledger-transaction-result/v1' or result.get('valid') is not True or not isinstance(effects, list)
                    or len(effects) != 1 or effects[0].get('result') not in ('appended', 'idempotent')
                    or not isinstance(effects[0].get('revision_after'), str)):
                raise ImportErrorDetail('Unrecognized import receipt; stop and reconcile before retrying')
            transactions.append(result)
            revision = effects[0]['revision_after']
        after, final_revision = native.records()
        for key, record in {**before, **{key: packet['record'] for key, packet in packets.items()}}.items():
            if key not in after or canonical(after[key]) != canonical(record):
                raise ImportErrorDetail(f'Full-record parity failed: {key}')
        for source, digest in snapshots.items():
            if hashlib.sha256(read_source(source)).hexdigest() != digest:
                raise ImportErrorDetail(f'Source changed during import: {source}; reconcile on retry')
        doctor = native.run('doctor')
        if (doctor.get('schema') != 'ledger-doctor-result/v1' or doctor.get('healthy') is not True
                or doctor.get('pending_transactions') != 0 or doctor.get('storage_mutated') is not False):
            raise ImportErrorDetail('Post-import custody is not healthy and quiescent')
    else:
        final_revision = revision
    return {'schema': 'learnings-retired-import/v1', 'status': 'verified' if apply else 'planned',
            'sources': receipts, 'source_records': len(packets), 'already_present': len(packets)-len(missing),
            'would_append': len(missing), 'appended': len(missing) if apply else 0,
            'revision': final_revision, 'transactions': transactions, 'storage_mutated': bool(apply and missing), 'authority_granted': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, action='append', required=True)
    parser.add_argument('--definition', type=Path, default=DEFINITION)
    parser.add_argument('--ledger-bin', default='ledger')
    parser.add_argument('--store-root', required=True)
    parser.add_argument('--store-id', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--framing-controls', type=Path)
    parser.add_argument('--initialize-empty', action='store_true')
    parser.add_argument('--confirm-no-writers', action='store_true')
    args = parser.parse_args()
    try:
        controls = json.loads(read_source(args.framing_controls), object_pairs_hook=unique) if args.framing_controls else {}
        native = Native(args.ledger_bin, args.definition, ['--store-root', args.store_root, '--store-id', args.store_id])
        if args.initialize_empty and not (args.apply and args.confirm_no_writers):
            raise ImportErrorDetail('--initialize-empty requires --apply --confirm-no-writers')
        result = import_sources(native, args.source, apply=args.apply, controls=controls, initialize_empty=args.initialize_empty)
    except (ImportErrorDetail, OSError, ValueError, RecursionError) as exc:
        print(json.dumps({'schema': 'learnings-retired-import-error/v1', 'status': 'blocked', 'error': str(exc),
                          'storage_mutated': None if args.apply else False, 'authority_granted': False}), file=sys.stderr)
        return 3
    print(canonical(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
