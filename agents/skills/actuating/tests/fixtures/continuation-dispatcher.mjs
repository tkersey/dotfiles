export function createDispatcher() {
  const active = new Map();
  const issued = new WeakMap();
  const locate = token => {
    const operation = token && typeof token === 'object' ? issued.get(token) : undefined;
    return operation && active.get(operation.key) === operation ? operation : undefined;
  };
  return {
    start(key, callback, {multiShot = false} = {}) {
      const token = Object.freeze({});
      const operation = {key, callback, multiShot};
      issued.set(token, operation);
      active.set(key, operation);
      return token;
    },
    deliver(token, value) {
      const operation = locate(token);
      if (!operation) return false;
      if (!operation.multiShot) active.delete(operation.key);
      const callback = operation.callback;
      callback(value);
      return true;
    },
    cancel(token) {
      const operation = locate(token);
      if (!operation) return false;
      active.delete(operation.key);
      return true;
    }
  };
}
