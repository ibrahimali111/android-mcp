#!/usr/bin/env python3
"""
Entrypoint script for running android-mcp server directly.
"""

from android_mcp.server import run_stdio_server

if __name__ == "__main__":
    run_stdio_server()
