#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Android Device Control
Enables LLMs (Claude Desktop, Cursor, Antigravity) to control Android over stdio.
"""

import sys
import json
import logging
from typing import Any, Dict, List
from .controller import AndroidController

# Setup logging to stderr (stdout is strictly reserved for JSON-RPC MCP messages)
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("android-mcp")

controller = AndroidController()

TOOLS_DEFINITIONS = [
    {
        "name": "android_check_connection",
        "description": "Check connection status with Android device or emulator, returning model and Android OS version.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "android_screenshot",
        "description": "Capture the current screen of the Android device and return it as a base64 PNG image for visual analysis.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "android_tap",
        "description": "Tap on specific screen coordinates (x, y).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate in pixels"},
                "y": {"type": "integer", "description": "Y coordinate in pixels"}
            },
            "required": ["x", "y"]
        }
    },
    {
        "name": "android_swipe",
        "description": "Perform a swipe or drag gesture from (x1, y1) to (x2, y2).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x1": {"type": "integer", "description": "Starting X coordinate"},
                "y1": {"type": "integer", "description": "Starting Y coordinate"},
                "x2": {"type": "integer", "description": "Ending X coordinate"},
                "y2": {"type": "integer", "description": "Ending Y coordinate"},
                "duration_ms": {"type": "integer", "description": "Swipe duration in milliseconds (default 300)", "default": 300}
            },
            "required": ["x1", "y1", "x2", "y2"]
        }
    },
    {
        "name": "android_type_text",
        "description": "Type a string of text into the currently active input field on Android.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text string to type"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "android_press_key",
        "description": "Press an Android hardware/system key (BACK, HOME, ENTER, TAB, POWER, VOLUME_UP, VOLUME_DOWN).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name: BACK, HOME, ENTER, TAB, POWER, VOLUME_UP, VOLUME_DOWN", "enum": ["BACK", "HOME", "ENTER", "TAB", "POWER", "VOLUME_UP", "VOLUME_DOWN"]}
            },
            "required": ["key"]
        }
    },
    {
        "name": "android_click_by_text",
        "description": "Smart-click: searches the screen UI hierarchy for an element with matching text or description and taps its center.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text or content description of the button/label to click"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "android_get_ui_tree",
        "description": "Inspect all visible UI elements on the current Android screen, returning text labels, resource IDs, and bounding coordinates.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "android_launch_app",
        "description": "Launch an Android app by its package name (e.g. com.android.settings).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "The app package name"}
            },
            "required": ["package_name"]
        }
    },
    {
        "name": "android_stop_app",
        "description": "Force-stop a running Android application.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "The app package name"}
            },
            "required": ["package_name"]
        }
    },
    {
        "name": "android_list_apps",
        "description": "List installed application package names on the device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "third_party_only": {"type": "boolean", "description": "Whether to list only user/third-party apps (default: true)", "default": True}
            },
            "required": []
        }
    },
    {
        "name": "android_shell",
        "description": "Execute an ADB shell command directly on the Android device.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    }
]


def handle_tool_call(tool_name: str, args: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute requested tool and format response."""
    if tool_name == "android_check_connection":
        info = controller.check_connection()
        return [{"type": "text", "text": json.dumps(info, indent=2)}]

    elif tool_name == "android_screenshot":
        b64_img = controller.capture_screen_base64()
        if b64_img:
            return [
                {"type": "image", "data": b64_img, "mimeType": "image/png"},
                {"type": "text", "text": "Screenshot captured successfully."}
            ]
        else:
            return [{"type": "text", "text": "Failed to capture screenshot. Ensure device is connected."}]

    elif tool_name == "android_tap":
        res = controller.tap(args["x"], args["y"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_swipe":
        duration = args.get("duration_ms", 300)
        res = controller.swipe(args["x1"], args["y1"], args["x2"], args["y2"], duration)
        return [{"type": "text", "text": res}]

    elif tool_name == "android_type_text":
        res = controller.type_text(args["text"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_press_key":
        res = controller.press_key(args["key"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_click_by_text":
        res = controller.click_element_by_text(args["text"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_get_ui_tree":
        elements = controller.get_ui_elements()
        return [{"type": "text", "text": json.dumps(elements, indent=2)}]

    elif tool_name == "android_launch_app":
        res = controller.launch_app(args["package_name"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_stop_app":
        res = controller.stop_app(args["package_name"])
        return [{"type": "text", "text": res}]

    elif tool_name == "android_list_apps":
        third_party = args.get("third_party_only", True)
        apps = controller.list_installed_apps(third_party)
        return [{"type": "text", "text": json.dumps(apps, indent=2)}]

    elif tool_name == "android_shell":
        res = controller.shell_command(args["command"])
        return [{"type": "text", "text": res}]

    else:
        return [{"type": "text", "text": f"Unknown tool: {tool_name}"}]


def send_response(response: Dict[str, Any]):
    """Write JSON-RPC response to stdout followed by newline and flush."""
    json_str = json.dumps(response)
    sys.stdout.write(json_str + "\n")
    sys.stdout.flush()


def run_stdio_server():
    """Main JSON-RPC stdio event loop."""
    logger.info("android-mcp server started listening on stdio.")

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception as e:
            logger.error(f"Failed to parse JSON request: {e}")
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # 1. Initialization
        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "android-mcp",
                        "version": "0.1.0"
                    }
                }
            })

        # 2. Client confirmed initialization
        elif method == "notifications/initialized":
            logger.info("Client completed MCP initialization handshake.")

        # 3. List available tools
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS_DEFINITIONS
                }
            })

        # 4. Call a tool
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                content = handle_tool_call(tool_name, tool_args)
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": content,
                        "isError": False
                    }
                })
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Tool execution error: {str(e)}"}],
                        "isError": True
                    }
                })

        # 5. Ping
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })

        # 6. Unknown method
        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                })


if __name__ == "__main__":
    run_stdio_server()
