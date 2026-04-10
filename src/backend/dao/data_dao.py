"""
数据访问层 - 数据获取
封装数据获取逻辑，与业务逻辑分离
"""
import requests
import json
import time
from typing import Optional, Dict, Any
from ..core.api_config import API_ENDPOINTS, API_PARAMS, REQUEST_HEADERS
from ..core.config import REQUEST_TIMEOUT, MAX_RETRIES


class DataDAO:
    """数据访问对象"""
    
    def __init__(self):
        self.base_url = API_ENDPOINTS["stock_kline"]
        self.secid = "90.BK1158"
        self.headers = REQUEST_HEADERS
    
    def fetch_stock_data(self) -> Optional[Dict[str, Any]]:
        """
        获取股票数据
        
        Returns:
            包含股票数据的字典，失败返回 None
        """
        params = {
            **API_PARAMS,
            "secid": self.secid,
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=REQUEST_TIMEOUT,
                    proxies=None
                )
                
                if response.status_code == 200:
                    content = response.text
                    return self._parse_jsonp(content)
                else:
                    print(f"HTTP 错误：{response.status_code}")
                    
            except requests.exceptions.ProxyError as e:
                print(f"代理错误：{e}")
            except requests.exceptions.SSLError as e:
                print(f"SSL 错误：{e}")
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败：{e}")
            except requests.exceptions.Timeout as e:
                print(f"请求超时：{e}")
            except requests.exceptions.ConnectionError as e:
                print(f"连接错误：{e}")
            except Exception as e:
                print(f"数据获取失败：{e}")
            
            if attempt < MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 2
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        print("❌ 数据获取失败：超过最大重试次数")
        return None
    
    def _parse_jsonp(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析 JSONP 格式数据
        
        Args:
            content: JSONP 格式的响应内容
            
        Returns:
            解析后的字典数据
        """
        start_idx = content.find('(')
        end_idx = content.rfind(')')
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("无效的 JSONP 格式")
        
        json_str = content[start_idx + 1:end_idx].strip()
        return json.loads(json_str)
