# 后端配置

# 服务配置
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000
DEBUG = True

# 前端配置
FRONTEND_PORT = 5500

# 数据源配置
EASTMONEY_BASE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
EASTMONEY_SECID = "90.BK1158"

# 请求配置
REQUEST_TIMEOUT = 30
MAX_RETRIES = 5

# 缓存配置
CACHE_DIR = "data/cache"
CACHE_TTL_DATA = 30 * 60  # 30 分钟
CACHE_TTL_INDICATOR = 5 * 60  # 5 分钟
CACHE_TTL_RISK = 30 * 60  # 30 分钟

# 历史窗口配置（预测/风险历史接口统一口径）
HISTORY_DAYS_DEFAULT = 300
HISTORY_DAYS_MAX = 300

# 定时任务配置
REFRESH_INTERVAL_HOURS = 3
DAILY_REPORT_HOUR = 15
DAILY_REPORT_MINUTE = 30

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/app.log"
