/**
 * 缓存工具
 * 封装 localStorage 操作
 */

const CACHE_PREFIX = 'microcap_';

const cache = {
  set(key, value, ttl = 30 * 60 * 1000) {
    const item = {
      data: value,
      timestamp: Date.now(),
      ttl,
    };
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(item));
  },

  get(key) {
    const itemStr = localStorage.getItem(CACHE_PREFIX + key);
    if (!itemStr) return null;

    try {
      const item = JSON.parse(itemStr);
      if (Date.now() - item.timestamp > item.ttl) {
        this.remove(key);
        return null;
      }
      return item.data;
    } catch (e) {
      return null;
    }
  },

  remove(key) {
    localStorage.removeItem(CACHE_PREFIX + key);
  },

  clear() {
    Object.keys(localStorage).forEach((key) => {
      if (key.startsWith(CACHE_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
  },
};

export default cache;
