# -*- coding: utf-8 -*-
"""
Pytest 配置文件

为 E2E 测试提供 fixtures
"""

import pytest
import requests
import time
import subprocess
import os
import signal
from typing import Generator, Optional


BASE_URL = "http://127.0.0.1:8000"
SERVER_STARTUP_TIMEOUT = 60  # 等待服务器启动的最大时间（秒）


@pytest.fixture(scope="session")
def web_server() -> Generator[str, None, None]:
    """
    启动 Web 服务器并返回 URL，测试结束后关闭服务器
    
    如果服务器已经在运行，会复用现有服务器
    """
    server_process: Optional[subprocess.Popen] = None
    server_was_running = False
    
    # 检查服务器是否已运行
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                server_was_running = True
                print(f"\n✓ 复用已运行的服务器: {BASE_URL}")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    if not server_was_running:
        # 启动服务器
        print(f"\n🚀 启动 Web 服务器: {BASE_URL}")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        server_process = subprocess.Popen(
            ["python", "main.py", "--webui-only"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # 等待服务器启动
        for i in range(SERVER_STARTUP_TIMEOUT // 2):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✓ 服务器启动成功: {BASE_URL}")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        else:
            if server_process:
                server_process.kill()
            pytest.fail(f"服务器启动超时（{SERVER_STARTUP_TIMEOUT}秒）")
    
    yield BASE_URL
    
    # 清理：关闭我们启动的服务器
    if server_process and not server_was_running:
        print("\n🛑 关闭 Web 服务器")
        server_process.terminate()
        try:
            server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server_process.kill()


@pytest.fixture
def base_url(web_server: str) -> str:
    """返回基础 URL"""
    return web_server


def pytest_configure(config):
    """Pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 为集成测试添加标记
        if "e2e" in item.nodeid or "test_pages" in item.nodeid:
            item.add_marker(pytest.mark.integration)
