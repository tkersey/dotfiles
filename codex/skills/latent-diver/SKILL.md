---
name: latent-diver
description: "Divergent originality pass for diving beneath obvious solution surfaces to surface non-obvious frames, analogies, and recombinations before convergence."
---

# Latent Diver

## Intent

Surface non-obvious, high-potential creative frames before the model converges on a merely good answer.

Treat "latent space" operationally: not as literal hidden-state access, but as deliberate movement through distant conceptual neighborhoods, analogies, inversions, constraints, and neglected assumptions.

Use this skill when the user wants originality, invention, reframing, strategy, conceptual breakthroughs, or creative problem solving.

## Contract

- Do not solve first.
- First identify the obvious answer basin.
- Then dive below it into distant frames.
- Prefer strange-but-groundable moves over theatrical weirdness.
- Every weird idea must have a plausible path to proof.
- Do not converge until the divergent map exists.
- Do not output a grab-bag; compress toward the few frames with the highest originality x usefulness potential.
- Label speculation clearly.
- Hand off the strongest frame to `accretive` when execution or dominance selection is needed.

## Workflow

### 1. Surface Scan

- Name 3-5 obvious answers the model is likely to give.
- State why those answers are insufficient, saturated, or low-leverage.

### 2. Dive Paths

Generate one candidate frame from each probe:

- **Substrate shift**: Move the problem to a different layer.
- **Constraint inversion**: Make the hardest constraint the design center.
- **Alien discipline**: Borrow primitives from an unrelated field.
- **Adversarial frame**: View the problem through an opponent, exploit, or failure mode.
- **Interface frame**: Look for a new boundary, API, ritual, protocol, or affordance.
- **Time-shift frame**: Imagine the problem 10x earlier, later, smaller, or larger.
- **Taboo frame**: Ask what would feel wrong, gauche, excessive, or embarrassing but might work.
- **Proof artifact frame**: Ask what artifact would make future insight cheap.

### 3. Pressure Test

Score each frame from 1-5:

- Semantic distance
- Usefulness
- Accretion
- Proofability
- Risk

### 4. Recombination

Combine the top 2-3 frames into 2-3 hybrid moves.

Each hybrid must include:

- the strange insight
- the practical mechanism
- the first proof signal
- the likely failure mode

### 5. Resurface

Choose one:

- `deep signal`: highest originality, uncertain utility
- `bridge move`: unusual but implementable
- `dominant candidate`: ready for `accretive`

### 6. Handoff

- If the user asked for options, pass the map to `creative-problem-solver`.
- If the user asked for a single best move, pass the dominant candidate to `accretive`.
- If the current answer is still too conventional, run `glaze` once.
- Use `asi` only as an ambition-expansion cue, not as a truth claim.

## Output

- `Surface Scan`
- `Dive Paths`
- `Pressure Test`
- `Recombined Moves`
- `Best Frame`
- `Why this is non-obvious`
- `First proof signal`
- `Recommended handoff`

## Operating Principle

Dive beneath the obvious answer basin, surface strange-but-useful frames, then hand the strongest one to a convergent skill.
