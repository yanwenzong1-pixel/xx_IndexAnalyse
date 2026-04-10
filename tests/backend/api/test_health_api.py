"""
后端 API 测试 - 健康检查测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.main import create_app


class TestHealthCheck:
    """健康检查测试类"""

    @pytest.fixture
    def client(self):
        """测试客户端夹具"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
