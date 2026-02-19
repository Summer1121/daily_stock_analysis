# -*- coding: utf-8 -*-
"""
Playwright E2E 测试配置

用于测试 WebUI 页面的可用性
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Playwright 配置
playwright_config = {
    "test_dir": "./tests",
    "timeout": 30000,
    "retries": 1,
    "workers": 1,
    "reporter": [
        ["html"],
        ["list"],
    ],
    "use": {
        "headless": True,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    },
    "projects": [
        {
            "name": "chromium",
            "use": {"browser_name": "chromium"},
        },
        {
            "name": "firefox",
            "use": {"browser_name": "firefox"},
        },
        {
            "name": "webkit",
            "use": {"browser_name": "webkit"},
        },
    ],
    "web_server": {
        "command": "python main.py --webui-only",
        "port": 8000,
        "timeout": 120000,
        "reuse_existing_server": True,
    },
}

# 测试环境配置
TEST_CONFIG = {
    "base_url": os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000"),
    "timeout": 30000,
}
