export function createDispatcher() {
  const active = new Map();
  const issued = new WeakMap();
  let continuations = [];
  const locate = token => {
    const operation = token && typeof token === 'object' ? issued.get(token) : undefined;
    return operation && active.get(operation.key) === operation ? operation : undefined;
  };
  return {
    start(key, callback, {multiShot = false} = {}) {
      const previous = active.get(key);
      continuations = continuations.filter(operation => operation !== previous);
      const token = Object.freeze({});
      const operation = {key, callback, multiShot};
      issued.set(token, operation);
      active.set(key, operation);
      continuations.push(operation);
      return token;
    },
    deliver(token, value) {
      const operation = locate(token);
      if (!operation) return false;
      if (!operation.multiShot) active.delete(operation.key);
      const continuation = continuations[0];
      if (!continuation.multiShot) continuations.shift();
      continuation.callback(value);
      return true;
    },
    cancel(token) {
      const operation = locate(token);
      if (!operation) return false;
      active.delete(operation.key);
      continuations = continuations.filter(item => item !== operation);
      return true;
    }
  };
}
