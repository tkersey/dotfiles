#!/usr/bin/env python3
"""Emit a fail-closed boundary-adapter scaffold.

Usage:
    emit_boundary_adapter.py [decoder] [typescript|python]

For backward compatibility, ``emit_boundary_adapter.py typescript`` is treated as
``emit_boundary_adapter.py decoder typescript``.
"""
from __future__ import annotations

import argparse

LANGUAGES = {"typescript", "ts", "python", "py"}
KINDS = {"decoder", "migration", "serializer"}

TYPESCRIPT = r'''// Fail-closed boundary adapter scaffold.
// Replace CoreShape and the decoder rules with repository-specific domain logic.
export type LegacyShape = unknown;
export type CoreShape = Readonly<Record<string, unknown>>;

export type DecodeError = Readonly<{
  path: string;
  message: string;
}>;

export type DecodeResult<T> =
  | Readonly<{ ok: true; value: T }>
  | Readonly<{ ok: false; errors: readonly DecodeError[] }>;

export function decodeLegacy(input: LegacyShape): DecodeResult<CoreShape> {
  void input;
  return {
    ok: false,
    errors: [
      {
        path: "$",
        message: "Boundary decoder is not implemented; define validation and normalization rules.",
      },
    ],
  };
}

export function encodeLegacy(core: CoreShape): LegacyShape {
  return { ...core };
}

// Required tests:
// - valid external fixture decodes to the expected CoreShape;
// - invalid and mismatched fixtures fail with structured errors;
// - decode(encode(core)) preserves public/domain invariants;
// - no unchecked cast or alternate public constructor bypasses this owner.
'''

PYTHON = r'''# Fail-closed boundary adapter scaffold.
# Replace CoreShape and the decoder rules with repository-specific domain logic.
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, TypeAlias

LegacyShape: TypeAlias = object


@dataclass(frozen=True)
class CoreShape:
    values: Mapping[str, object]


@dataclass(frozen=True)
class DecodeError:
    path: str
    message: str


@dataclass(frozen=True)
class DecodeSuccess:
    value: CoreShape


@dataclass(frozen=True)
class DecodeFailure:
    errors: tuple[DecodeError, ...]


DecodeResult: TypeAlias = DecodeSuccess | DecodeFailure


def decode_legacy(value: LegacyShape) -> DecodeResult:
    del value
    return DecodeFailure(
        (
            DecodeError(
                path="$",
                message=(
                    "Boundary decoder is not implemented; define validation "
                    "and normalization rules."
                ),
            ),
        )
    )


def encode_legacy(core: CoreShape) -> LegacyShape:
    return dict(core.values)


# Required tests:
# - valid external fixture decodes to the expected CoreShape;
# - invalid and mismatched fixtures fail with structured errors;
# - decode_legacy(encode_legacy(core)) preserves public/domain invariants;
# - no alternate unchecked constructor bypasses this owner.
'''


def parse_args() -> tuple[str, str]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", nargs="?", default="decoder")
    parser.add_argument("language", nargs="?", default="typescript")
    args = parser.parse_args()

    kind = args.kind.lower()
    language = args.language.lower()
    if kind in LANGUAGES and args.language == "typescript":
        language = kind
        kind = "decoder"
    if kind not in KINDS:
        parser.error(f"unknown adapter kind {kind!r}; choose from {sorted(KINDS)}")
    if language not in LANGUAGES:
        parser.error(f"unknown language {language!r}; choose typescript or python")
    return kind, language


def main() -> int:
    _kind, language = parse_args()
    print(PYTHON if language in {"python", "py"} else TYPESCRIPT, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
