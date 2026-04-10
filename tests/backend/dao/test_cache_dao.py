"""
后端 DAO 测试 - 缓存测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.dao.cache_dao import CacheDAO


class TestCacheDAO:
    """缓存 DAO 测试类"""

    @pytest.fixture
    def cache(self):
        """测试夹具"""
        cache = CacheDAO()
        cache.clear_all()
        yield cache
        cache.clear_all()

    def test_set_and_get(self, cache):
        """测试设置和获取缓存"""
        cache.set('test_key', {'data': 'test'}, ttl=60)
        result = cache.get('test_key', ttl=60)
        assert result == {'data': 'test'}

    def test_get_expired(self, cache):
        """测试过期缓存"""
        cache.set('test_key', {'data': 'test'}, ttl=0)
        import time
        time.sleep(0.1)
        result = cache.get('test_key', ttl=0)
        assert result is None

    def test_delete(self, cache):
        """测试删除缓存"""
        cache.set('test_key', {'data': 'test'}, ttl=60)
        cache.delete('test_key')
        result = cache.get('test_key', ttl=60)
        assert result is None

    def test_clear_all(self, cache):
        """测试清空缓存"""
        cache.set('key1', 'value1', ttl=60)
        cache.set('key2', 'value2', ttl=60)
        cache.clear_all()
        assert cache.get('key1', ttl=60) is None
        assert cache.get('key2', ttl=60) is None
