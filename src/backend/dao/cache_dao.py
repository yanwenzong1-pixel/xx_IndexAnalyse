"""
数据访问层 - 缓存管理
封装缓存操作逻辑
"""
import os
import json
import time
from typing import Any, Optional
from datetime import datetime
from ..core.config import CACHE_DIR, CACHE_TTL_DATA, CACHE_TTL_INDICATOR, CACHE_TTL_RISK


class CacheDAO:
    """缓存访问对象"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            缓存文件完整路径
        """
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, key: str, ttl: int = CACHE_TTL_DATA) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            ttl: 生存时间（秒）
            
        Returns:
            缓存数据，过期或不存在返回 None
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = cache_data.get('timestamp', 0)
            if time.time() - timestamp > ttl:
                self.delete(key)
                return None
            
            return cache_data.get('data')
        except (json.JSONDecodeError, IOError) as e:
            print(f"缓存读取失败：{e}")
            return None
    
    def set(self, key: str, data: Any, ttl: int = CACHE_TTL_DATA):
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 缓存数据
            ttl: 生存时间（秒）
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"缓存写入失败：{e}")
    
    def delete(self, key: str):
        """
        删除缓存
        
        Args:
            key: 缓存键
        """
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
    
    def get_data(self) -> Optional[Any]:
        """获取数据缓存"""
        return self.get('stock_data', CACHE_TTL_DATA)
    
    def set_data(self, data: Any):
        """设置数据缓存"""
        self.set('stock_data', data, CACHE_TTL_DATA)
    
    def get_indicators(self) -> Optional[Any]:
        """获取指标缓存"""
        return self.get('indicators', CACHE_TTL_INDICATOR)
    
    def set_indicators(self, data: Any):
        """设置指标缓存"""
        self.set('indicators', data, CACHE_TTL_INDICATOR)
    
    def get_risk(self) -> Optional[Any]:
        """获取风险缓存"""
        return self.get('risk', CACHE_TTL_RISK)
    
    def set_risk(self, data: Any):
        """设置风险缓存"""
        self.set('risk', data, CACHE_TTL_RISK)
    
    def clear_all(self):
        """清空所有缓存"""
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                    except IOError as e:
                        print(f"删除缓存文件失败：{e}")
