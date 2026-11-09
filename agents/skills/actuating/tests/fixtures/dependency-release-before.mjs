export function assessRelease(plan, manifest, observations) {
  const admittedManifest = manifest?.artifactId === plan.artifactId ? manifest : null;
  const destinations = plan.destinations.map(destinationId => {
    const matches = observations.filter(observation =>
      observation.artifactId === plan.artifactId && observation.destinationId === destinationId);
    return matches.length === 1 ? matches[0] : null;
  });
  if (!admittedManifest || typeof admittedManifest.digest !== 'string'
    || destinations.some(destination => !destination
      || typeof destination.reachable !== 'boolean'
      || !Number.isInteger(destination.freeBytes))) return null;
  return admittedManifest.digest === plan.requiredDigest
    && destinations.some(destination => destination.reachable
      && destination.freeBytes >= plan.requiredBytes);
}
