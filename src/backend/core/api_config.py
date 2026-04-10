# API 配置

# 东方财富 API 参数
API_PARAMS = {
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fields1": "f1,f2,f3,f4,f5,f6",
    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
    "klt": "101",
    "fqt": "1",
    "end": "20500101",
    "lmt": "1000000",
}

# 请求头配置
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://quote.eastmoney.com/",
}

# API 端点配置
API_ENDPOINTS = {
    "stock_kline": "https://push2his.eastmoney.com/api/qt/stock/kline/get",
}
