# Golden Output Manifest

## Capture

- Program / command:
- Inputs directory:
- Output directory:
- Normalization command, if any:
- Checksum file:

## Commands

```bash
mkdir -p golden_outputs
for input in test_inputs/*; do
  ./program "$input" > "golden_outputs/$(basename "$input").out"
done
sha256sum golden_outputs/* > golden_checksums.txt
sha256sum -c golden_checksums.txt
```

## Invariants

- Ordering:
- Tie-breaking:
- Floating-point tolerance:
- RNG seed:
- Time handling:
- Error handling:
- Known nondeterminism normalization:
