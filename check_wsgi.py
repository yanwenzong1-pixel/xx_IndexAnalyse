try:
    import waitress
    print("✅ waitress 已安装")
except ImportError:
    print("❌ waitress 未安装")

try:
    import gunicorn
    print("✅ gunicorn 已安装")
except ImportError:
    print("❌ gunicorn 未安装")
