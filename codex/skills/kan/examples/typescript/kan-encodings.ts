export type Observation<A, B> = { tag: "Observation"; run: (a: A) => B };
export type Generated<S, A> = { tag: "Generated"; source: S; lower: (s: S) => A };
