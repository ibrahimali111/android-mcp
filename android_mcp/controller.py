#!/usr/bin/env python3
"""
Android Controller Engine for MCP Server
Provides programmatic ADB control for screen inspection, input gestures, and app management.
"""

import os
import subprocess
import base64
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple


class AndroidController:
    def __init__(self, serial: Optional[str] = None, adb_path: str = "adb"):
        self.serial = serial or os.getenv("ANDROID_SERIAL")
        self.adb_path = adb_path

    def _run_adb(self, cmd_args: List[str], text: bool = True) -> str:
        """Run ADB command with optional serial targeting."""
        full_cmd = [self.adb_path]
        if self.serial:
            full_cmd += ["-s", self.serial]
        full_cmd += cmd_args

        try:
            res = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,
                check=False
            )
            return res.stdout.strip() if text else res.stdout
        except Exception as e:
            return f"Error executing ADB command: {e}" if text else b""

    def check_connection(self) -> Dict[str, any]:
        """Check connection to Android device or emulator."""
        devices_out = self._run_adb(["devices"])
        connected_devices = []

        for line in devices_out.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "device":
                connected_devices.append(parts[0])

        if not connected_devices:
            # Attempt connection to common local emulator ports if set
            fallback_host = os.getenv("ANDROID_ADB_HOST", "127.0.0.1:5555")
            subprocess.run([self.adb_path, "connect", fallback_host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            devices_out = self._run_adb(["devices"])
            for line in devices_out.splitlines()[1:]:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == "device":
                    connected_devices.append(parts[0])

        is_connected = len(connected_devices) > 0
        model = self._run_adb(["shell", "getprop", "ro.product.model"]) if is_connected else "Unknown"
        android_ver = self._run_adb(["shell", "getprop", "ro.build.version.release"]) if is_connected else "Unknown"

        return {
            "connected": is_connected,
            "device_serial": self.serial or (connected_devices[0] if connected_devices else None),
            "model": model,
            "android_version": android_ver,
            "all_devices": connected_devices
        }

    # ==================== INPUT ACTIONS ====================

    def tap(self, x: int, y: int) -> str:
        """Tap specific screen coordinates (x, y)."""
        self._run_adb(["shell", "input", "tap", str(x), str(y)])
        return f"Tapped coordinate ({x}, {y})"

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> str:
        """Perform swipe gesture from (x1, y1) to (x2, y2)."""
        self._run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        return f"Swiped from ({x1}, {y1}) to ({x2}, {y2}) over {duration_ms}ms"

    def type_text(self, text: str) -> str:
        """Type text into the currently focused input field."""
        escaped = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
        self._run_adb(["shell", "input", "text", escaped])
        return f"Typed text: {text}"

    def press_key(self, key_name: str) -> str:
        """Press Android key (e.g. HOME, BACK, ENTER, TAB, POWER, VOLUME_UP, VOLUME_DOWN)."""
        key = key_name.upper().replace("KEYCODE_", "")
        self._run_adb(["shell", "input", "keyevent", f"KEYCODE_{key}"])
        return f"Pressed key KEYCODE_{key}"

    # ==================== SCREEN CAPTURE ====================

    def capture_screen_base64(self) -> Optional[str]:
        """Capture screen as raw PNG and return base64-encoded string."""
        raw_bytes = self._run_adb(["exec-out", "screencap", "-p"], text=False)
        if raw_bytes and len(raw_bytes) > 100:
            return base64.b64encode(raw_bytes).decode("ascii")
        return None

    # ==================== UI INSPECTION ====================

    def get_ui_elements(self) -> List[Dict[str, any]]:
        """Dump UI layout hierarchy via uiautomator and parse clickable elements with bounds."""
        xml_dump_path = "/sdcard/mcp_window_dump.xml"
        self._run_adb(["shell", "uiautomator", "dump", xml_dump_path])
        xml_content = self._run_adb(["shell", "cat", xml_dump_path])
        self._run_adb(["shell", "rm", "-f", xml_dump_path])

        elements = []
        if xml_content and "<hierarchy" in xml_content:
            try:
                root = ET.fromstring(xml_content)
                for node in root.iter("node"):
                    text = node.attrib.get("text", "").strip()
                    res_id = node.attrib.get("resource-id", "").strip()
                    content_desc = node.attrib.get("content-desc", "").strip()
                    clickable = node.attrib.get("clickable", "false") == "true"
                    bounds = node.attrib.get("bounds", "")

                    if (text or content_desc or clickable) and bounds:
                        coords = bounds.replace("][", ",").replace("[", "").replace("]", "").split(",")
                        if len(coords) == 4:
                            x1, y1, x2, y2 = map(int, coords)
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            elements.append({
                                "text": text,
                                "resource_id": res_id,
                                "desc": content_desc,
                                "clickable": clickable,
                                "center": [center_x, center_y],
                                "bounds": [x1, y1, x2, y2]
                            })
            except Exception:
                pass
        return elements

    def click_element_by_text(self, text: str) -> str:
        """Find an on-screen element containing text or description and tap it."""
        elements = self.get_ui_elements()
        target = text.lower().strip()

        for el in elements:
            if target in el["text"].lower() or target in el["desc"].lower():
                cx, cy = el["center"]
                self.tap(cx, cy)
                matched_label = el["text"] or el["desc"]
                return f"Successfully clicked element '{matched_label}' at ({cx}, {cy})"

        return f"Element with text '{text}' not found on screen."

    # ==================== APP MANAGEMENT ====================

    def launch_app(self, package_name: str) -> str:
        """Launch app by package name."""
        res = self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        return f"Launched app {package_name}" if "No activities" not in res else f"App {package_name} not found"

    def stop_app(self, package_name: str) -> str:
        """Force-stop application."""
        self._run_adb(["shell", "am", "force-stop", package_name])
        return f"Stopped app {package_name}"

    def list_installed_apps(self, third_party_only: bool = True) -> List[str]:
        """List package names of installed applications."""
        args = ["shell", "pm", "list", "packages"]
        if third_party_only:
            args.append("-3")
        raw = self._run_adb(args)
        return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]

    def shell_command(self, command: str) -> str:
        """Execute arbitrary shell command on Android device."""
        return self._run_adb(["shell", command])
