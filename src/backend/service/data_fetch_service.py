"""
业务逻辑层 - 数据获取服务
封装数据获取业务逻辑
"""
import pandas as pd
from typing import Optional, List, Dict, Any
from ..dao.data_dao import DataDAO
from ..dao.cache_dao import CacheDAO
from ..model.stock_model import StockData


class DataFetchService:
    """数据获取服务"""
    
    def __init__(self):
        self.data_dao = DataDAO()
        self.cache_dao = CacheDAO()
        self.df: Optional[pd.DataFrame] = None
    
    def fetch_data(self, use_cache: bool = True) -> bool:
        """
        获取数据
        
        Args:
            use_cache: 是否使用缓存
            
        Returns:
            是否获取成功
        """
        if use_cache:
            cached_data = self.cache_dao.get_data()
            if cached_data:
                self._parse_data(cached_data)
                print("✅ 从缓存加载数据成功")
                return True
        
        raw_data = self.data_dao.fetch_stock_data()
        if raw_data:
            self.cache_dao.set_data(raw_data)
            self._parse_data(raw_data)
            print(f"✅ 数据获取成功，共 {len(self.df)} 条记录")
            return True
        
        print("❌ 数据获取失败")
        return False
    
    def _parse_data(self, data: Dict[str, Any]):
        """
        解析数据为 DataFrame
        
        Args:
            data: 原始数据
        """
        if 'data' not in data or 'klines' not in data['data']:
            raise ValueError("数据格式错误")
        
        klines = data['data']['klines']
        data_list = []
        
        for kline in klines:
            parts = kline.split(',')
            data_list.append({
                'date': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': float(parts[5]),
                'amount': float(parts[6]),
                'amplitude': float(parts[7]),
                'change_pct': float(parts[8]),
                'change': float(parts[9]),
                'turnover': float(parts[10])
            })
        
        self.df = pd.DataFrame(data_list)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date')
        self.df.reset_index(drop=True, inplace=True)
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """获取 DataFrame"""
        return self.df
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取最新数据"""
        if self.df is None or len(self.df) == 0:
            return None
        latest = self.df.iloc[-1]
        return latest.to_dict()
    
    def get_history_data(self, days: int = 60) -> List[Dict[str, Any]]:
        """
        获取历史数据
        
        Args:
            days: 天数
            
        Returns:
            历史数据列表
        """
        if self.df is None:
            return []
        
        history_df = self.df.tail(days)
        return history_df.to_dict('records')
