#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import dataclasses
import math
import os
import pathlib
import re
import shutil
import statistics
import sys
from typing import Iterable, Iterator, Sequence

THIS_DIR = pathlib.Path(__file__).resolve().parent
VENDOR_DIRS = [
    THIS_DIR / 'vendor' / 'python',
    THIS_DIR / 'scripts' / 'vendor' / 'python',
    THIS_DIR / 'vendor',
]
for vendor_dir in VENDOR_DIRS:
    if vendor_dir.exists() and str(vendor_dir) not in sys.path:
        sys.path.insert(0, str(vendor_dir))

try:
    from pypdf import PdfReader  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(f'Unable to import vendored pypdf: {exc}')


BULLET_RE = re.compile(r"^\s*([\-•–◦▪‣])\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*(\(?\d+[.)]|[A-Za-z][.)])\s+(.*)$")
PAGE_NUMBER_RE = re.compile(r"^\s*(page\s+)?\d+(\s*/\s*\d+|\s+of\s+\d+)?\s*$", re.IGNORECASE)
MULTISPACE_RE = re.compile(r"\s+")
MONO_FONT_RE = re.compile(r"(courier|mono|consolas|menlo|code)", re.IGNORECASE)
BOLD_FONT_RE = re.compile(r"(bold|black|semibold|demi)", re.IGNORECASE)
ITALIC_FONT_RE = re.compile(r"(italic|oblique)", re.IGNORECASE)
TRAILING_TOC_NUMBER_RE = re.compile(r"^(.*?)(?:\s|\.{2,}|\u2024{2,}|\u00b7{2,})(\d+)\s*$")
URL_RE = re.compile(r"^(https?://\S+|www\.\S+)$", re.IGNORECASE)
SENTENCE_END_RE = re.compile(r"[.!?;:]$")
PUNCT_ONLY_RE = re.compile(r"^[\.,;:!?\)\]\}]+$")


class ConverterError(RuntimeError):
    pass


@dataclasses.dataclass(slots=True)
class Span:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    size: float
    font: str

    @property
    def is_bold(self) -> bool:
        return bool(BOLD_FONT_RE.search(self.font))

    @property
    def is_mono(self) -> bool:
        return bool(MONO_FONT_RE.search(self.font))

    @property
    def is_italic(self) -> bool:
        return bool(ITALIC_FONT_RE.search(self.font))


@dataclasses.dataclass(slots=True)
class TocEntry:
    title: str
    page_number: int
    level: int
    source_page: int


@dataclasses.dataclass(slots=True)
class Line:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    spans: list[Span]
    page_width: float
    page_height: float
    text: str
    removed: bool = False
    kind: str | None = None
    heading_level: int | None = None
    toc_entry: TocEntry | None = None

    @property
    def avg_font_size(self) -> float:
        weighted: list[float] = []
        for span in self.spans:
            weight = max(1, min(40, len(span.text.strip())))
            weighted.extend([span.size] * weight)
        return statistics.median(weighted) if weighted else 0.0

    @property
    def max_font_size(self) -> float:
        return max((span.size for span in self.spans), default=0.0)

    @property
    def font(self) -> str:
        fonts: collections.Counter[str] = collections.Counter()
        for span in self.spans:
            fonts[span.font] += max(1, len(span.text.strip()))
        return fonts.most_common(1)[0][0] if fonts else ''

    @property
    def char_count(self) -> int:
        return len(self.text.strip())

    @property
    def is_bold(self) -> bool:
        total = sum(max(1, len(span.text.strip())) for span in self.spans)
        if total == 0:
            return False
        bold = sum(max(1, len(span.text.strip())) for span in self.spans if span.is_bold)
        return bold / total >= 0.55

    @property
    def is_italic(self) -> bool:
        total = sum(max(1, len(span.text.strip())) for span in self.spans)
        if total == 0:
            return False
        italic = sum(max(1, len(span.text.strip())) for span in self.spans if span.is_italic)
        return italic / total >= 0.55

    @property
    def is_mono(self) -> bool:
        total = sum(max(1, len(span.text.strip())) for span in self.spans)
        if total == 0:
            return False
        mono = sum(max(1, len(span.text.strip())) for span in self.spans if span.is_mono)
        return mono / total >= 0.55

    @property
    def normalized_text(self) -> str:
        return normalize_spaces(self.text).upper()

    @property
    def is_short(self) -> bool:
        return len(self.text.strip()) <= 120

    @property
    def indent(self) -> float:
        return self.x0


@dataclasses.dataclass(slots=True)
class Block:
    page: int
    page_width: float
    page_height: float
    lines: list[Line]
    kind: str | None = None
    heading_level: int | None = None

    @property
    def text(self) -> str:
        return "\n".join(line.text.rstrip() for line in self.lines).strip()

    @property
    def x0(self) -> float:
        return min((line.x0 for line in self.lines), default=0.0)

    @property
    def y0(self) -> float:
        return min((line.y0 for line in self.lines), default=0.0)

    @property
    def x1(self) -> float:
        return max((line.x1 for line in self.lines), default=0.0)

    @property
    def y1(self) -> float:
        return max((line.y1 for line in self.lines), default=0.0)

    @property
    def avg_font_size(self) -> float:
        weighted: list[float] = []
        for line in self.lines:
            weight = max(1, min(120, line.char_count))
            weighted.extend([line.avg_font_size] * weight)
        return statistics.median(weighted) if weighted else 0.0

    @property
    def max_font_size(self) -> float:
        return max((line.max_font_size for line in self.lines), default=0.0)

    @property
    def is_bold(self) -> bool:
        total = sum(line.char_count for line in self.lines)
        if total == 0:
            return False
        bold = sum(line.char_count for line in self.lines if line.is_bold)
        return bold / total >= 0.55

    @property
    def is_italic(self) -> bool:
        total = sum(line.char_count for line in self.lines)
        if total == 0:
            return False
        italic = sum(line.char_count for line in self.lines if line.is_italic)
        return italic / total >= 0.55

    @property
    def is_mono(self) -> bool:
        total = sum(line.char_count for line in self.lines)
        if total == 0:
            return False
        mono = sum(line.char_count for line in self.lines if line.is_mono)
        return mono / total >= 0.55

    @property
    def line_indents(self) -> list[float]:
        return [line.indent for line in self.lines]


@dataclasses.dataclass(slots=True)
class DocumentStats:
    body_font_size: float
    body_font_name: str
    left_margin: float
    most_used_distance: float
    max_font_size: float
    page_count: int
    toc_pages: set[int]


@dataclasses.dataclass(slots=True)
class ConversionResult:
    markdown: str
    parser: str
    pages_seen: int
    lines_seen: int
    blocks_written: int


@dataclasses.dataclass(slots=True)
class InlineSegment:
    text: str
    bold: bool = False
    italic: bool = False
    plain: bool = False


# ---------- Utility helpers ----------

def normalize_spaces(text: str) -> str:
    return MULTISPACE_RE.sub(' ', text.replace('\xa0', ' ')).strip()


def normalize_for_headline_matching(text: str) -> str:
    return ''.join(ch for ch in text.upper() if not ch.isspace() and ch not in '.\t')


def normalize_for_hash(text: str) -> str:
    cleaned = []
    for ch in text.upper().replace('\xa0', ' '):
        if ch.isspace() or ch.isdigit():
            continue
        cleaned.append(ch)
    return ''.join(cleaned)


def word_match(string1: str, string2: str) -> float:
    words1 = {w for w in normalize_spaces(string1).upper().split(' ') if w}
    words2 = {w for w in normalize_spaces(string2).upper().split(' ') if w}
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / max(len(words1), len(words2))


def iter_pdf_paths(root: pathlib.Path, recursive: bool) -> Iterator[pathlib.Path]:
    if root.is_file():
        if root.suffix.lower() != '.pdf':
            raise ConverterError(f'Input file is not a PDF: {root}')
        yield root
        return

    if not root.is_dir():
        raise ConverterError(f'Input path does not exist: {root}')

    iterator: Iterable[pathlib.Path]
    iterator = root.rglob('*.pdf') if recursive else root.glob('*.pdf')
    found = False
    for path in sorted(iterator):
        if path.is_file():
            found = True
            yield path
    if not found:
        raise ConverterError(f'No PDF files found under {root}')


def resolve_output_path(input_path: pathlib.Path, output: pathlib.Path | None) -> tuple[pathlib.Path, bool]:
    if input_path.is_file():
        if output is None:
            return input_path.with_suffix('.md'), False
        if output.exists() and output.is_dir():
            return output / f'{input_path.stem}.md', False
        if output.suffix.lower() == '.md':
            return output, False
        return output / f'{input_path.stem}.md', False

    if output is None:
        return input_path.parent / f'{input_path.name}_markdown', True
    return output, True


def safe_write_text(path: pathlib.Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f'Output already exists: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def sanitize_font_name(font_name: object | None) -> str:
    if font_name is None:
        return ''
    value = str(font_name)
    if value.startswith('/'):
        value = value[1:]
    return value


def estimate_text_width(text: str, font_size: float) -> float:
    width_units = 0.0
    for ch in text:
        if ch.isspace():
            width_units += 0.28
        elif ch in 'ilI|\'`.,:;![](){}':
            width_units += 0.22
        elif ch in 'mwMW@#%&':
            width_units += 0.78
        else:
            width_units += 0.49
    return max(font_size * width_units, font_size * 0.35)


def should_insert_soft_space(previous_text: str, current_text: str, gap: float, font_size: float) -> bool:
    prev = previous_text.rstrip()
    curr = current_text.lstrip()
    if not prev or not curr:
        return False
    if prev.endswith('-'):
        return False
    prev_char = prev[-1]
    curr_char = curr[0]
    if PUNCT_ONLY_RE.match(curr_char):
        return False
    if prev_char in '([{/':
        return False
    if prev_char.isalnum() and curr_char.isalnum():
        return gap >= -font_size * 0.35
    if prev_char in ',;:)]}' and curr_char.isalnum():
        return gap >= -font_size * 0.35
    return False


def is_titleish(text: str) -> bool:
    stripped = normalize_spaces(text)
    if not stripped:
        return False
    words = stripped.split()
    if len(words) > 14:
        return False
    if stripped.isupper():
        return True
    upper_words = sum(1 for word in words if word[:1].isupper())
    return upper_words >= max(1, len(words) - 2)


def build_line_text(spans: Sequence[Span]) -> str:
    pieces: list[str] = []
    prev_x1: float | None = None
    prev_size = spans[0].size if spans else 12.0
    prev_text = ''
    for span in spans:
        text = span.text.replace('\u00ad', '').replace('\xa0', ' ')
        if not text.strip():
            prev_x1 = span.x1
            prev_size = span.size
            continue
        current_text = text.strip()
        if prev_x1 is None:
            pieces.append(current_text)
        else:
            gap = span.x0 - prev_x1
            if gap > max(prev_size * 2.4, 22.0):
                pieces.append('\t')
            elif gap > max(prev_size * 0.45, 2.0) or should_insert_soft_space(prev_text, current_text, gap, prev_size):
                pieces.append(' ')
            pieces.append(current_text)
        prev_text = current_text
        prev_x1 = span.x1
        prev_size = span.size
    joined = ''.join(pieces)
    joined = re.sub(r'\s*\t\s*', '\t', joined)
    joined = re.sub(r' {2,}', ' ', joined)
    return joined.strip()


def line_gap(prev_line: Line, line: Line) -> float:
    return line.y0 - prev_line.y0


def block_has_tabular_row(block: Block) -> bool:
    if not block.lines:
        return False
    row_scores = 0
    for line in block.lines:
        if '\t' in line.text:
            row_scores += 1
            continue
        parts = [part for part in re.split(r'\s{2,}|\t+', line.text.strip()) if part]
        if len(parts) >= 2:
            row_scores += 1
    return row_scores >= max(1, math.ceil(len(block.lines) * 0.6))


# ---------- Extraction ----------

def extract_lines(pdf_path: pathlib.Path) -> list[Line]:
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:  # pragma: no cover
        raise ConverterError(f'Unable to open PDF with vendored pypdf: {pdf_path}') from exc

    lines: list[Line] = []
    for page_index, page in enumerate(reader.pages, start=1):
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        spans = extract_page_spans(page, page_index, page_width, page_height)
        page_lines = group_spans_into_lines(spans, page_index, page_width, page_height)
        lines.extend(page_lines)
    return lines


def extract_page_spans(page: object, page_index: int, page_width: float, page_height: float) -> list[Span]:
    spans: list[Span] = []
    seen: set[tuple[str, int, int, str, int]] = set()

    def visitor_text(text: str, _cm: object, tm: object, font_dict: object, font_size: float) -> None:
        if not text or not text.replace('\u0000', '').strip():
            return
        try:
            x = float(tm[4])
            y_pdf = float(tm[5])
        except Exception:
            x = 0.0
            y_pdf = 0.0
        y_top = page_height - y_pdf
        font_name = ''
        try:
            if font_dict:
                font_name = sanitize_font_name(font_dict.get('/BaseFont'))
        except Exception:
            font_name = sanitize_font_name(font_dict)
        cleaned = text.replace('\u0000', '').replace('\r', '').replace('\u00ad', '')
        parts = [part for part in cleaned.split('\n') if part and part.strip()]
        for part in parts:
            part = part.replace('\xa0', ' ')
            key = (part, int(round(x * 10)), int(round(y_top * 10)), font_name, int(round(font_size * 10)))
            if key in seen:
                continue
            seen.add(key)
            width = estimate_text_width(part, font_size)
            spans.append(
                Span(
                    text=part,
                    x0=x,
                    y0=y_top,
                    x1=x + width,
                    y1=y_top + font_size,
                    size=float(font_size),
                    font=font_name,
                )
            )

    try:
        page.extract_text(visitor_text=visitor_text, extraction_mode='plain')
    except Exception as exc:  # pragma: no cover
        raise ConverterError(f'pypdf text extraction failed on page {page_index}') from exc
    return spans


def group_spans_into_lines(spans: list[Span], page_index: int, page_width: float, page_height: float) -> list[Line]:
    if not spans:
        return []
    spans = sorted(spans, key=lambda span: (round(span.y0, 1), span.x0, span.x1))
    groups: list[list[Span]] = []
    current: list[Span] = []
    current_baseline = 0.0
    for span in spans:
        if not current:
            current = [span]
            current_baseline = span.y0
            continue
        tolerance = max(2.2, min(span.size, statistics.median(s.size for s in current)) * 0.35)
        if abs(span.y0 - current_baseline) <= tolerance:
            current.append(span)
            current_baseline = statistics.median(s.y0 for s in current)
        else:
            groups.append(current)
            current = [span]
            current_baseline = span.y0
    if current:
        groups.append(current)

    lines: list[Line] = []
    for group in groups:
        ordered = sorted(group, key=lambda span: (span.x0, span.x1))
        text = build_line_text(ordered)
        if not normalize_spaces(text):
            continue
        x0 = min(span.x0 for span in ordered)
        y0 = min(span.y0 for span in ordered)
        x1 = max(span.x1 for span in ordered)
        y1 = max(span.y1 for span in ordered)
        lines.append(
            Line(
                page=page_index,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                spans=ordered,
                page_width=page_width,
                page_height=page_height,
                text=text,
            )
        )
    return sorted(lines, key=lambda line: (line.page, line.y0, line.x0))


# ---------- Global stats / classification ----------

def calculate_global_stats(lines: list[Line]) -> DocumentStats:
    if not lines:
        return DocumentStats(body_font_size=12.0, body_font_name='', left_margin=0.0, most_used_distance=14.0, max_font_size=12.0, page_count=1, toc_pages=set())

    size_counter: collections.Counter[float] = collections.Counter()
    font_counter: collections.Counter[str] = collections.Counter()
    max_font_size = 0.0
    for line in lines:
        size = round(line.avg_font_size * 2) / 2.0
        weight = max(1, min(160, line.char_count))
        size_counter[size] += weight
        if line.font:
            font_counter[line.font] += weight
        max_font_size = max(max_font_size, line.max_font_size)

    body_font_size = size_counter.most_common(1)[0][0] if size_counter else 12.0
    body_font_name = font_counter.most_common(1)[0][0] if font_counter else ''

    distance_counter: collections.Counter[float] = collections.Counter()
    left_margins: list[float] = []
    by_page = group_lines_by_page(lines)
    for page_lines in by_page.values():
        page_lines = [line for line in page_lines if not line.removed]
        last_body: Line | None = None
        for line in page_lines:
            if round(line.avg_font_size * 2) / 2.0 == body_font_size and line.char_count > 0:
                if last_body is not None and line.y0 > last_body.y0:
                    distance = round(line.y0 - last_body.y0)
                    if distance > 0:
                        distance_counter[distance] += 1
                last_body = line
            else:
                last_body = None
            if line.char_count > 20:
                left_margins.append(line.x0)
    most_used_distance = float(distance_counter.most_common(1)[0][0]) if distance_counter else max(12.0, body_font_size * 1.35)
    left_margin = statistics.median(left_margins) if left_margins else min(line.x0 for line in lines)
    page_count = max(line.page for line in lines)
    return DocumentStats(
        body_font_size=float(body_font_size),
        body_font_name=body_font_name,
        left_margin=float(left_margin),
        most_used_distance=float(most_used_distance),
        max_font_size=float(max_font_size),
        page_count=page_count,
        toc_pages=set(),
    )


def group_lines_by_page(lines: list[Line]) -> dict[int, list[Line]]:
    pages: dict[int, list[Line]] = collections.defaultdict(list)
    for line in lines:
        pages[line.page].append(line)
    for page in pages.values():
        page.sort(key=lambda item: (item.y0, item.x0))
    return dict(sorted(pages.items()))


def remove_repetitive_elements(lines: list[Line], stats: DocumentStats) -> None:
    by_page = group_lines_by_page(lines)
    if len(by_page) < 2:
        return
    top_counts: collections.Counter[str] = collections.Counter()
    bottom_counts: collections.Counter[str] = collections.Counter()
    page_store: dict[int, tuple[list[Line], list[Line], str, str]] = {}
    for page_number, page_lines in by_page.items():
        live = [line for line in page_lines if line.char_count > 0]
        if not live:
            continue
        min_y = min(line.y0 for line in live)
        max_y = max(line.y0 for line in live)
        top_lines = [line for line in live if abs(line.y0 - min_y) <= 1.5]
        bottom_lines = [line for line in live if abs(line.y0 - max_y) <= 1.5]
        top_hash = normalize_for_hash(''.join(line.text for line in top_lines))
        bottom_hash = normalize_for_hash(''.join(line.text for line in bottom_lines))
        page_store[page_number] = (top_lines, bottom_lines, top_hash, bottom_hash)
        if top_hash:
            top_counts[top_hash] += 1
        if bottom_hash:
            bottom_counts[bottom_hash] += 1

    threshold = max(3, math.ceil(len(by_page) * 2 / 3))
    for page_number, (top_lines, bottom_lines, top_hash, bottom_hash) in page_store.items():
        if top_hash and top_counts[top_hash] >= threshold:
            for line in top_lines:
                line.removed = True
        if bottom_hash and bottom_counts[bottom_hash] >= threshold:
            for line in bottom_lines:
                line.removed = True
        for line in top_lines + bottom_lines:
            if PAGE_NUMBER_RE.match(line.text):
                line.removed = True


# ---------- TOC and heading heuristics ----------

def parse_toc_title_and_page(line_text: str) -> tuple[str, int] | None:
    text = normalize_spaces(line_text.replace('\t', ' '))
    if not text:
        return None
    match = TRAILING_TOC_NUMBER_RE.match(text)
    if match:
        title = normalize_spaces(match.group(1).replace('.', ' '))
        if title:
            return title, int(match.group(2))
    parts = text.split()
    if len(parts) >= 2 and parts[-1].isdigit():
        title = normalize_spaces(' '.join(parts[:-1]).replace('.', ' '))
        if title:
            return title, int(parts[-1])
    return None


def detect_toc(lines: list[Line], stats: DocumentStats) -> list[TocEntry]:
    by_page = group_lines_by_page(lines)
    toc_entries: list[TocEntry] = []
    max_pages = min(20, len(by_page))
    for page_number, page_lines in list(by_page.items())[:max_pages]:
        live = [line for line in page_lines if not line.removed and normalize_spaces(line.text)]
        if len(live) < 3:
            continue
        pending_title: list[str] = []
        page_entries: list[tuple[Line, TocEntry]] = []
        numeric_lines = 0
        first_non_numeric: Line | None = None
        for line in live:
            parsed = parse_toc_title_and_page(line.text)
            if parsed:
                title, page_ref = parsed
                if pending_title:
                    title = normalize_spaces(' '.join(pending_title + [title]))
                    pending_title = []
                numeric_lines += 1
                entry = TocEntry(title=title, page_number=page_ref, level=0, source_page=page_number)
                page_entries.append((line, entry))
                line.toc_entry = entry
                line.kind = 'toc'
            else:
                stripped = normalize_spaces(line.text.replace('.', ' '))
                if stripped and not first_non_numeric:
                    first_non_numeric = line
                    continue
                if stripped:
                    if pending_title:
                        pending_title.append(stripped)
                    else:
                        pending_title = [stripped]
        if numeric_lines * 100 / len(live) > 75:
            x_positions = sorted({round(line.x0, 1) for line, _ in page_entries})
            fonts = []
            for line, _ in page_entries:
                if line.font not in fonts:
                    fonts.append(line.font)
            for line, entry in page_entries:
                if len(x_positions) > 1:
                    entry.level = x_positions.index(round(line.x0, 1))
                elif len(fonts) > 1:
                    entry.level = fonts.index(line.font)
                else:
                    entry.level = 0
                line.toc_entry = entry
                line.kind = 'toc'
            if first_non_numeric and first_non_numeric.kind is None:
                first_non_numeric.kind = 'heading'
                first_non_numeric.heading_level = 2
            toc_entries.extend(entry for _, entry in page_entries)
        else:
            for line, _ in page_entries:
                line.toc_entry = None
                if line.kind == 'toc':
                    line.kind = None
    stats.toc_pages = {entry.source_page for entry in toc_entries}
    return toc_entries


def find_heading_sequence(page_lines: Sequence[Line], headline: str) -> list[int] | None:
    target = normalize_for_headline_matching(headline)
    if not target:
        return None
    stacked_indices: list[int] = []
    stacked = ''
    for index, line in enumerate(page_lines):
        if line.removed:
            continue
        normalized = normalize_for_headline_matching(line.text)
        if not normalized:
            continue
        candidate = stacked + normalized
        if target.startswith(candidate):
            stacked_indices.append(index)
            stacked = candidate
            if stacked == target:
                return stacked_indices
        else:
            stacked_indices = []
            stacked = ''
            if target.startswith(normalized):
                stacked_indices.append(index)
                stacked = normalized
                if stacked == target:
                    return stacked_indices
    return None


def detect_page_mapping(toc_entries: list[TocEntry], lines: list[Line]) -> int:
    by_page = group_lines_by_page(lines)
    last_toc_page = max((entry.source_page for entry in toc_entries), default=0)
    candidate_pages = {page: page_lines for page, page_lines in by_page.items() if page > last_toc_page}
    for entry in toc_entries:
        for page_number, page_lines in candidate_pages.items():
            if find_heading_sequence(page_lines, entry.title):
                return page_number - entry.page_number
    return 0


def detect_headings(lines: list[Line], stats: DocumentStats, toc_entries: list[TocEntry]) -> dict[int, tuple[float, float]]:
    by_page = group_lines_by_page(lines)
    heading_ranges: dict[int, tuple[float, float]] = {}
    max_font_pages = {
        page_number
        for page_number, page_lines in by_page.items()
        if any(abs(line.max_font_size - stats.max_font_size) < 0.2 for line in page_lines if not line.removed)
    }
    min_h2_on_max_page = stats.body_font_size + ((stats.max_font_size - stats.body_font_size) / 4.0)

    # Title page logic inspired by upstream DetectHeaders
    for page_number in sorted(max_font_pages):
        if page_number > 3:
            continue
        for line in by_page[page_number]:
            if line.removed or line.kind == 'toc':
                continue
            height = line.max_font_size
            if height > min_h2_on_max_page and line.is_short:
                line.kind = 'heading'
                line.heading_level = 1 if abs(height - stats.max_font_size) < 0.2 else 2

    if toc_entries:
        page_mapping = detect_page_mapping(toc_entries, lines)
        for entry in toc_entries:
            level = min(entry.level + 2, 6)
            candidate_pages = [entry.page_number + page_mapping, entry.page_number + page_mapping + 1, entry.page_number + page_mapping - 1]
            matched = False
            for candidate in candidate_pages:
                page_lines = by_page.get(candidate)
                if not page_lines:
                    continue
                indices = find_heading_sequence(page_lines, entry.title)
                if indices is None:
                    continue
                matched_lines = [page_lines[idx] for idx in indices]
                for line in matched_lines:
                    line.kind = 'heading'
                    line.heading_level = level
                height = max(line.max_font_size for line in matched_lines)
                current = heading_ranges.get(level)
                if current:
                    heading_ranges[level] = (min(current[0], height), max(current[1], height))
                else:
                    heading_ranges[level] = (height, height)
                matched = True
                break
            if not matched and level in heading_ranges:
                min_h, max_h = heading_ranges[level]
                for candidate in candidate_pages:
                    page_lines = by_page.get(candidate)
                    if not page_lines:
                        continue
                    for line in page_lines:
                        if line.removed or line.kind or not line.is_short:
                            continue
                        if min_h - 0.5 <= line.max_font_size <= max_h + 0.5 and word_match(entry.title, line.text) >= 0.5:
                            line.kind = 'heading'
                            line.heading_level = level
                            matched = True
                            break
                    if matched:
                        break

    # Size-based fallback when TOC is absent or incomplete.
    untyped_lines = [line for line in lines if not line.removed and line.kind is None and line.char_count > 0]
    heading_sizes = sorted(
        {
            round(line.max_font_size * 2) / 2.0
            for line in untyped_lines
            if line.max_font_size > stats.body_font_size * 1.14 and line.is_short and not blockish_list_line(line)
        },
        reverse=True,
    )
    size_to_level = {size: min(index + 2, 6) for index, size in enumerate(heading_sizes)}
    for line in untyped_lines:
        size = round(line.max_font_size * 2) / 2.0
        text = normalize_spaces(line.text)
        if size in size_to_level and len(text) <= 160:
            line.kind = 'heading'
            line.heading_level = size_to_level[size]
            level = size_to_level[size]
            current = heading_ranges.get(level)
            if current:
                heading_ranges[level] = (min(current[0], line.max_font_size), max(current[1], line.max_font_size))
            else:
                heading_ranges[level] = (line.max_font_size, line.max_font_size)
        elif (
            line.kind is None
            and line.max_font_size >= stats.body_font_size
            and line.font != stats.body_font_name
            and text == text.upper()
            and len(text) <= 100
            and is_titleish(text)
        ):
            line.kind = 'heading'
            line.heading_level = min(max(heading_ranges.keys(), default=1) + 1, 6)

    return heading_ranges


def blockish_list_line(line: Line) -> bool:
    return bool(BULLET_RE.match(line.text) or NUMBERED_RE.match(line.text) or line.kind == 'toc')


# ---------- Blocks ----------

def build_blocks(lines: list[Line], stats: DocumentStats) -> list[Block]:
    by_page = group_lines_by_page([line for line in lines if not line.removed])
    all_blocks: list[Block] = []
    for page_number, page_lines in by_page.items():
        page_min_x = min((line.x0 for line in page_lines), default=stats.left_margin)
        blocks: list[Block] = []
        current: Block | None = None
        for line in page_lines:
            classify_line_kind(line, stats)
            if current is None:
                current = Block(page=page_number, page_width=line.page_width, page_height=line.page_height, lines=[line], kind=line.kind, heading_level=line.heading_level)
                continue
            if should_flush_block(current, line, stats, page_min_x):
                blocks.append(current)
                current = Block(page=page_number, page_width=line.page_width, page_height=line.page_height, lines=[line], kind=line.kind, heading_level=line.heading_level)
            else:
                current.lines.append(line)
                if current.kind is None:
                    current.kind = line.kind
                if current.heading_level is None and line.heading_level is not None:
                    current.heading_level = line.heading_level
        if current is not None:
            blocks.append(current)
        for block in blocks:
            refine_block_kind(block, stats, page_min_x)
        all_blocks.extend(blocks)

    all_blocks = merge_page_break_blocks(all_blocks)
    return all_blocks


def classify_line_kind(line: Line, stats: DocumentStats) -> None:
    if line.kind == 'heading' or line.kind == 'toc':
        return
    text = normalize_spaces(line.text)
    if not text:
        return
    if BULLET_RE.match(line.text) or NUMBERED_RE.match(line.text):
        line.kind = 'list'
        return
    if PAGE_NUMBER_RE.match(text):
        line.removed = True
        return
    if line.is_mono and line.char_count > 0:
        line.kind = 'code'


def should_flush_block(current: Block, line: Line, stats: DocumentStats, page_min_x: float) -> bool:
    last = current.lines[-1]
    gap = line_gap(last, line)
    base_gap = max(8.0, stats.most_used_distance + 1)
    if last.x0 > page_min_x + 2 and line.x0 > page_min_x + 2:
        base_gap += stats.most_used_distance / 2.0

    current_kind = current.kind
    next_kind = line.kind

    if current_kind == 'heading':
        if next_kind == 'heading' and line.heading_level == current.heading_level and gap <= base_gap * 1.5:
            return False
        return True
    if next_kind == 'heading':
        return True

    if current_kind == 'toc':
        return next_kind != 'toc'
    if next_kind == 'toc':
        return True

    if current_kind == 'list':
        if next_kind == 'list':
            return gap > base_gap * 1.5 or gap < -base_gap / 2.0
        if next_kind is None and line.x0 >= last.x0 + 2 and gap <= base_gap * 1.5:
            return False
        return True
    if next_kind == 'list':
        return True

    if current_kind == 'code':
        return next_kind != 'code' or gap > base_gap * 1.5 or gap < -base_gap / 2.0
    if next_kind == 'code':
        return True

    if gap < -base_gap / 2.0:
        return True
    if gap > base_gap * 1.5:
        return True
    return False


def refine_block_kind(block: Block, stats: DocumentStats, page_min_x: float) -> None:
    if block.kind == 'heading':
        if block.heading_level is None:
            block.heading_level = min((line.heading_level for line in block.lines if line.heading_level), default=2)
        return
    if block.kind == 'toc':
        return
    if block.kind == 'list':
        return
    if block.kind == 'code':
        return
    if block_has_tabular_row(block) and len(block.lines) >= 2:
        block.kind = 'table'
        return
    if looks_like_code_block(block, stats, page_min_x):
        block.kind = 'code'
        return
    if looks_like_quote_block(block, stats):
        block.kind = 'quote'
        return
    block.kind = 'paragraph'


def looks_like_code_block(block: Block, stats: DocumentStats, page_min_x: float) -> bool:
    if not block.lines:
        return False
    if block.is_mono:
        return True
    if len(block.lines) == 1:
        line = block.lines[0]
        return line.x0 > page_min_x + max(8.0, stats.body_font_size * 0.8) and line.avg_font_size <= stats.body_font_size + 1.0
    if all(line.x0 > page_min_x + max(8.0, stats.body_font_size * 0.8) for line in block.lines):
        return True
    symbol_count = sum(block.text.count(ch) for ch in '{}[]();:=<>_/\\')
    return symbol_count >= 3 and len(block.lines) >= 2


def looks_like_quote_block(block: Block, stats: DocumentStats) -> bool:
    if not block.lines or block.kind in {'list', 'table', 'code'}:
        return False
    min_indent = min(block.line_indents) if block.line_indents else block.x0
    return min_indent > stats.left_margin + max(10.0, stats.body_font_size * 0.9) and block.is_italic


def merge_page_break_blocks(blocks: list[Block]) -> list[Block]:
    if not blocks:
        return []
    merged: list[Block] = [blocks[0]]
    for block in blocks[1:]:
        previous = merged[-1]
        if should_merge_across_page_break(previous, block):
            previous.lines.extend(block.lines)
            continue
        merged.append(block)
    return merged


def should_merge_across_page_break(previous: Block, current: Block) -> bool:
    if previous.kind != 'paragraph' or current.kind != 'paragraph':
        return False
    if current.page != previous.page + 1:
        return False
    if previous.y1 < previous.page_height * 0.72:
        return False
    if current.y0 > current.page_height * 0.28:
        return False
    if abs(previous.x0 - current.x0) > 10.0:
        return False
    prev_text = normalize_spaces(previous.text)
    curr_text = normalize_spaces(current.text)
    if not prev_text or not curr_text:
        return False
    if SENTENCE_END_RE.search(prev_text):
        return False
    return curr_text[:1].islower()


# ---------- Markdown rendering ----------

def escape_markdown_text(text: str) -> str:
    return text.replace('\\', '\\\\')


def span_style(span: Span) -> tuple[bool, bool]:
    return span.is_bold, span.is_italic


def line_to_segments(line: Line, preserve_tabs: bool = False) -> list[InlineSegment]:
    segments: list[InlineSegment] = []
    prev_x1: float | None = None
    prev_size = line.spans[0].size if line.spans else 12.0
    prev_text_for_segments = ''
    for span in sorted(line.spans, key=lambda item: (item.x0, item.x1)):
        text = span.text.replace('\xa0', ' ')
        if not text or not text.strip():
            prev_x1 = span.x1
            prev_size = span.size
            continue
        if prev_x1 is not None:
            gap = span.x0 - prev_x1
            clean_probe = text.strip()
            if gap > max(prev_size * 2.4, 22.0):
                segments.append(InlineSegment('\t' if preserve_tabs else ' ', plain=True))
            elif gap > max(prev_size * 0.45, 2.0) or should_insert_soft_space(prev_text_for_segments, clean_probe, gap, prev_size):
                segments.append(InlineSegment(' ', plain=True))
        clean = normalize_spaces(text) if not preserve_tabs else text.strip()
        if clean:
            bold, italic = span_style(span)
            segments.append(InlineSegment(clean, bold=bold, italic=italic))
            prev_text_for_segments = clean
        prev_x1 = span.x1
        prev_size = span.size

    merged: list[InlineSegment] = []
    for segment in segments:
        if merged and segment.plain == merged[-1].plain and segment.bold == merged[-1].bold and segment.italic == merged[-1].italic:
            merged[-1].text += segment.text
        else:
            merged.append(segment)
    return merged


def render_segment(segment: InlineSegment) -> str:
    text = escape_markdown_text(segment.text)
    if segment.plain:
        return text
    stripped = text
    if URL_RE.match(stripped):
        target = stripped if stripped.lower().startswith('http') else f'http://{stripped}'
        stripped = f'[{stripped}]({target})'
    if segment.bold and segment.italic:
        return f'***{stripped}***'
    if segment.bold:
        return f'**{stripped}**'
    if segment.italic:
        return f'*{stripped}*'
    return stripped


def render_inline_line(line: Line) -> str:
    text = ''.join(render_segment(segment) for segment in line_to_segments(line, preserve_tabs=False))
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def render_heading(block: Block) -> str:
    level = block.heading_level or 2
    text = ' '.join(normalize_spaces(line.text) for line in block.lines if normalize_spaces(line.text))
    return f"{'#' * max(1, min(level, 6))} {escape_markdown_text(text.strip())}"


def list_level_by_x(lines: Sequence[Line]) -> dict[int, int]:
    current_level = 0
    last_x: float | None = None
    x_by_level: dict[int, int] = {}
    result: dict[int, int] = {}
    for index, line in enumerate(lines):
        x_key = int(round(line.x0))
        if last_x is not None:
            if line.x0 > last_x + 2:
                current_level += 1
                x_by_level[x_key] = current_level
            elif line.x0 < last_x - 2:
                current_level = x_by_level.get(x_key, 0)
        else:
            x_by_level[x_key] = 0
        result[index] = current_level
        last_x = line.x0
    return result


def render_list(block: Block) -> str:
    levels = list_level_by_x(block.lines)
    rendered: list[str] = []
    for index, line in enumerate(block.lines):
        level = levels.get(index, 0)
        prefix = '  ' * max(0, level)
        bullet_match = BULLET_RE.match(line.text)
        numbered_match = NUMBERED_RE.match(line.text)
        if line.kind == 'toc' and line.toc_entry is not None:
            content = escape_markdown_text(line.toc_entry.title)
            rendered.append(f"{prefix}- {content}")
            continue
        if bullet_match:
            content = render_inline_text_from_plain_and_segments(line, bullet_match.group(2))
            rendered.append(f"{prefix}- {content}")
        elif numbered_match:
            content = render_inline_text_from_plain_and_segments(line, numbered_match.group(2))
            rendered.append(f"{prefix}1. {content}")
        else:
            content = render_inline_line(line)
            continuation_prefix = '  ' * max(0, level) + '  '
            rendered.append(f"{continuation_prefix}{content}")
    return '\n'.join(rendered)


def render_inline_text_from_plain_and_segments(line: Line, fallback_plain: str) -> str:
    full = render_inline_line(line)
    plain = normalize_spaces(line.text)
    fallback_plain = normalize_spaces(fallback_plain)
    if plain == fallback_plain:
        return full
    if full.endswith(plain):
        return full[: len(full) - len(plain)] + fallback_plain
    return escape_markdown_text(fallback_plain)


def render_code(block: Block) -> str:
    return '```\n' + '\n'.join(line.text.rstrip() for line in block.lines) + '\n```'


def render_quote(block: Block) -> str:
    return '\n'.join(f'> {render_inline_line(line)}' for line in block.lines)


def render_table(block: Block) -> str:
    rows: list[list[str]] = []
    for line in block.lines:
        parts = [escape_markdown_text(part.strip()) for part in re.split(r'\t+|\s{2,}', line.text.strip()) if part.strip()]
        if parts:
            rows.append(parts)
    if len(rows) < 2:
        return render_code(block)
    width = max(len(row) for row in rows)
    padded = [row + [''] * (width - len(row)) for row in rows]
    table_lines = [
        '| ' + ' | '.join(padded[0]) + ' |',
        '| ' + ' | '.join(['---'] * width) + ' |',
    ]
    for row in padded[1:]:
        table_lines.append('| ' + ' | '.join(row) + ' |')
    return '\n'.join(table_lines)


def render_paragraph(block: Block) -> str:
    pieces: list[str] = []
    previous_raw = ''
    for line in block.lines:
        raw = normalize_spaces(line.text)
        rendered = render_inline_line(line)
        if not rendered:
            continue
        if pieces and previous_raw.endswith('-') and raw[:1].islower():
            pieces[-1] = pieces[-1][:-1] + rendered
        else:
            pieces.append(rendered)
        previous_raw = raw
    return ' '.join(piece.strip() for piece in pieces if piece.strip())


def render_markdown(blocks: list[Block]) -> tuple[str, int]:
    rendered: list[str] = []
    rendered_kinds: list[str] = []
    written = 0
    for block in blocks:
        text = ''
        if block.kind == 'heading':
            text = render_heading(block)
        elif block.kind == 'list' or block.kind == 'toc':
            text = render_list(block)
        elif block.kind == 'code':
            text = render_code(block)
        elif block.kind == 'quote':
            text = render_quote(block)
        elif block.kind == 'table':
            text = render_table(block)
        else:
            text = render_paragraph(block)
        text = text.strip()
        if not text:
            continue
        if block.kind in {'list', 'toc'} and rendered and rendered_kinds[-1] in {'list', 'toc'}:
            rendered[-1] = rendered[-1] + '\n' + text
        else:
            rendered.append(text)
            rendered_kinds.append(block.kind or 'paragraph')
        written += 1
    markdown = '\n\n'.join(rendered).strip() + '\n'
    return markdown, written


# ---------- Conversion pipeline ----------

def convert_pdf(pdf_path: pathlib.Path) -> ConversionResult:
    lines = extract_lines(pdf_path)
    stats = calculate_global_stats(lines)
    remove_repetitive_elements(lines, stats)
    toc_entries = detect_toc(lines, stats)
    detect_headings(lines, stats, toc_entries)
    blocks = build_blocks(lines, stats)
    markdown, written = render_markdown(blocks)
    return ConversionResult(
        markdown=markdown,
        parser='vendored-pypdf',
        pages_seen=max((line.page for line in lines), default=0),
        lines_seen=len(lines),
        blocks_written=written,
    )


# ---------- CLI ----------

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Convert PDF files or folders of PDFs into Markdown using a fully bundled Python parser.')
    parser.add_argument('--input', '-i', required=True, help='PDF file or directory containing PDFs')
    parser.add_argument('--output', '-o', help='Output Markdown file or directory')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recurse through subdirectories when input is a directory')
    parser.add_argument('--overwrite', '-f', action='store_true', help='Overwrite existing Markdown outputs')
    return parser.parse_args(argv)


def convert_many(input_path: pathlib.Path, output_path: pathlib.Path | None, recursive: bool, overwrite: bool) -> int:
    resolved_output, is_dir_input = resolve_output_path(input_path, output_path)
    pdf_paths = list(iter_pdf_paths(input_path, recursive=recursive))
    failures = 0
    for pdf_path in pdf_paths:
        try:
            result = convert_pdf(pdf_path)
            if is_dir_input:
                relative = pdf_path.relative_to(input_path)
                md_path = resolved_output / relative.with_suffix('.md')
            else:
                md_path = resolved_output
            safe_write_text(md_path, result.markdown, overwrite=overwrite)
            print(f'OK   {pdf_path} -> {md_path} [parser={result.parser}, pages={result.pages_seen}, blocks={result.blocks_written}, lines={result.lines_seen}]')
        except Exception as exc:
            failures += 1
            print(f'FAIL {pdf_path}: {exc}', file=sys.stderr)
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    input_path = pathlib.Path(args.input).expanduser().resolve()
    output_path = pathlib.Path(args.output).expanduser().resolve() if args.output else None
    try:
        failures = convert_many(input_path=input_path, output_path=output_path, recursive=args.recursive, overwrite=args.overwrite)
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
