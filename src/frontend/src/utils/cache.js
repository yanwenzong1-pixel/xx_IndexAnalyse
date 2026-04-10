const memory = new Map();

const cache = {
  get(key) {
    try {
      const raw = localStorage.getItem(`cache:${key}`);
      if (!raw) return null;
      const { value, expiry } = JSON.parse(raw);
      if (expiry && Date.now() > expiry) {
        localStorage.removeItem(`cache:${key}`);
        return null;
      }
      return value;
    } catch {
      return memory.get(key) ?? null;
    }
  },
  set(key, value, ttlMs) {
    const expiry = ttlMs ? Date.now() + ttlMs : null;
    try {
      localStorage.setItem(`cache:${key}`, JSON.stringify({ value, expiry }));
    } catch {
      memory.set(key, value);
    }
  },
  remove(key) {
    try {
      localStorage.removeItem(`cache:${key}`);
    } catch {
      memory.delete(key);
    }
  },
};

export default cache;
