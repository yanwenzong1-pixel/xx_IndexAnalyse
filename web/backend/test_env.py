print("Testing Python environment...")

try:
    import flask
    print("Flask imported successfully")
except ImportError as e:
    print(f"Error importing Flask: {e}")

try:
    import flask_cors
    print("Flask-CORS imported successfully")
except ImportError as e:
    print(f"Error importing Flask-CORS: {e}")

try:
    import pandas
    print("Pandas imported successfully")
except ImportError as e:
    print(f"Error importing Pandas: {e}")

try:
    import numpy
    print("NumPy imported successfully")
except ImportError as e:
    print(f"Error importing NumPy: {e}")

try:
    import requests
    print("Requests imported successfully")
except ImportError as e:
    print(f"Error importing Requests: {e}")

try:
    import apscheduler
    print("APScheduler imported successfully")
except ImportError as e:
    print(f"Error importing APScheduler: {e}")

print("Test completed")
