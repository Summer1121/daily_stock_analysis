# -*- coding: utf-8 -*-
"""
Web 服务器模块（向后兼容）

实际实现位于 legacy_server.py，此处仅做 re-export 以满足 web.__init__ 等对 web.server 的引用。
"""
from web.legacy_server import WebServer, run_server_in_thread, run_server

__all__ = ["WebServer", "run_server_in_thread", "run_server"]
