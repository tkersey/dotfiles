export function encode(value) {
  if (!Object.hasOwn(value, 'timeout')) {
    return 'i';
  }
  return value.timeout === null ? 'n' : String(value.timeout);
}
export function decode(bytes) {
  if (bytes === 'i') {
    return {};
  }
  return {timeout: bytes === 'n' ? null : Number(bytes)};
}
