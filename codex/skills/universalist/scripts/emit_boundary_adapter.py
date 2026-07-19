#!/usr/bin/env python3
"""Emit a fail-closed boundary adapter scaffold.

Usage:
    emit_boundary_adapter.py <kind> <language>
"""

from __future__ import annotations

import argparse


def typescript_decoder() -> str:
    return """// Fail-closed boundary adapter scaffold
export type LegacyShape = unknown;

export interface CoreShape {
  readonly __brand: \"CoreShape\";
}

export type DecodeError = {
  readonly code: \"VALIDATION_NOT_IMPLEMENTED\" | \"INVALID_LEGACY_SHAPE\";
  readonly message: string;
};

export type DecodeResult<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: DecodeError };

export function decodeLegacy(input: LegacyShape): DecodeResult<CoreShape> {
  void input;
  return {
    ok: false,
    error: {
      code: \"VALIDATION_NOT_IMPLEMENTED\",
      message: \"Define validation and normalization at the owning boundary.\",
    },
  };
}

export function encodeLegacy(_core: CoreShape): LegacyShape {
  throw new Error(\"Define the stable external projection before use.\");
}
"""


def typescript_serializer() -> str:
    return """// Stable public projection scaffold
export type PublicShape = unknown;

export interface CoreShape {
  readonly __brand: \"CoreShape\";
}

export function projectPublic(_core: CoreShape): PublicShape {
  throw new Error(\"Define the observation-preserving public projection before use.\");
}

// Required law: decodePublic(projectPublic(core)) preserves every declared public invariant.
// Required falsifier: a core value whose required public evidence would be lost is rejected or reported.
"""


def python_decoder() -> str:
    return '''# Fail-closed boundary adapter scaffold
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CoreShape:
    """Replace with the validated internal representation."""


@dataclass(frozen=True)
class DecodeError:
    code: str
    message: str


VALIDATION_NOT_IMPLEMENTED: Final = "VALIDATION_NOT_IMPLEMENTED"


def decode_legacy(value: object) -> CoreShape | DecodeError:
    del value
    return DecodeError(
        code=VALIDATION_NOT_IMPLEMENTED,
        message="Define validation and normalization at the owning boundary.",
    )


def encode_legacy(core: CoreShape) -> object:
    del core
    raise NotImplementedError("Define the stable external projection before use.")
'''


def python_serializer() -> str:
    return '''# Stable public projection scaffold
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoreShape:
    """Replace with the validated internal representation."""


def project_public(core: CoreShape) -> object:
    del core
    raise NotImplementedError(
        "Define the observation-preserving public projection before use."
    )


# Required law: decode_public(project_public(core)) preserves declared public invariants.
# Required falsifier: required public evidence is never silently discarded.
'''


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("decoder", "serializer"))
    parser.add_argument("language", choices=("typescript", "ts", "python"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    language = "typescript" if args.language == "ts" else args.language
    emitters = {
        ("decoder", "typescript"): typescript_decoder,
        ("serializer", "typescript"): typescript_serializer,
        ("decoder", "python"): python_decoder,
        ("serializer", "python"): python_serializer,
    }
    print(emitters[(args.kind, language)](), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
