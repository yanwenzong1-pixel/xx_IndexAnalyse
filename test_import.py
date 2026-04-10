import sys
sys.path.insert(0, 'web/backend')
from simple_app import app
print("✅ Import successful!")
print(f"App name: {app.name}")
