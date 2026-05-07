// TypeScript approximations of Kan-extension implementation shapes.
// These are engineering encodings, not formal rank-n/HKT encodings.

export type Lan<KI, DI, A> = Readonly<{
  project: (ki: KI) => A;
  payload: DI;
  witness: string;
}>;

export function makeLan<KI, DI, A>(witness: string, project: (ki: KI) => A, payload: DI): Lan<KI, DI, A> {
  return Object.freeze({ witness, project, payload });
}

export type Ran<A, KI, DI> = Readonly<{
  run: (observe: (a: A) => KI) => DI;
}>;

export function makeRan<A, KI, DI>(run: (observe: (a: A) => KI) => DI): Ran<A, KI, DI> {
  return Object.freeze({ run });
}

export function assertLanUnit<A>(oldValue: A, embedThenProject: (a: A) => A): void {
  const got = embedThenProject(oldValue);
  if (JSON.stringify(got) !== JSON.stringify(oldValue)) {
    throw new Error(`Lan unit compatibility failed: ${JSON.stringify({ oldValue, got })}`);
  }
}

export function assertRanCounit<A>(newValue: A, projectThenCompare: (a: A) => boolean): void {
  if (!projectThenCompare(newValue)) {
    throw new Error("Ran counit compatibility failed");
  }
}
