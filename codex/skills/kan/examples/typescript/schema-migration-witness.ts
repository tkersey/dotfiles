type V1Customer = { id: string; email: string; name: string };
type V2Person = { personId: string; email: string; displayName?: string; provenance: string[] };

export function sigmaCustomers(customers: V1Customer[]): V2Person[] {
  return customers.map(c => ({
    personId: `person:${c.email}`,
    email: c.email,
    displayName: c.name,
    provenance: [`customer:${c.id}`],
  }));
}

export function deltaPersons(persons: V2Person[]): V1Customer[] {
  return persons
    .filter(p => p.displayName !== undefined)
    .map(p => ({ id: p.personId, email: p.email, name: p.displayName! }));
}

export function assertCompatibility(oldRows: V1Customer[]) {
  const migrated = sigmaCustomers(oldRows);
  const restricted = deltaPersons(migrated);
  for (const old of oldRows) {
    const got = restricted.find(r => r.email === old.email);
    if (!got || got.name !== old.name) throw new Error("migration compatibility failed");
  }
}
