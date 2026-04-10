"""
Pytest 配置文件
"""
import pytest


def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(scope='session')
def test_config():
    """测试配置夹具"""
    return {
        'backend_url': 'http://127.0.0.1:5000',
        'timeout': 30,
    }
