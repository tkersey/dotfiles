export function assessRelease(plan, manifest, observations) {
  const admittedManifest = manifest?.artifactId === plan.artifactId ? manifest : null;
  const digestMatches = admittedManifest?.digest == null
    ? null : admittedManifest.digest === plan.requiredDigest;
  const destinationStates = plan.destinations.map(destinationId => {
    const matches = observations.filter(observation =>
      observation.artifactId === plan.artifactId && observation.destinationId === destinationId);
    const destination = matches.length === 1 ? matches[0] : null;
    const reachable = destination?.reachable ?? null;
    const hasSpace = destination?.freeBytes == null
      ? null : destination.freeBytes >= plan.requiredBytes;
    if (reachable === false || hasSpace === false) return false;
    return reachable === true && hasSpace === true ? true : null;
  });
  const hasUsableDestination = destinationStates.includes(true) ? true
    : destinationStates.includes(null) ? null : false;
  if (digestMatches === false || hasUsableDestination === false) return false;
  return digestMatches === true && hasUsableDestination === true ? true : null;
}
