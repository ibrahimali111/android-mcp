# 🤖 android-mcp

<p align="center">
  <a href="https://github.com/ibrahimali111/android-mcp/actions/workflows/ci.yml">
    <img src="https://github.com/ibrahimali111/android-mcp/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://github.com/ibrahimali111/android-mcp/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" />
  </a>
  <img src="https://img.shields.io/badge/protocol-MCP%202024--11--05-8A2BE2" alt="MCP Compatible" />
  <img src="https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/target-Android%20%7C%20Waydroid-3DDC84?logo=android&logoColor=white" alt="Android" />
</p>

A standard **Model Context Protocol (MCP)** server that enables AI agents (Claude Desktop, Cursor, Antigravity, and autonomous LLMs) to directly control, inspect, and automate **Android devices**, **Waydroid**, and **AVD emulators** over ADB.

---

## 🏗️ Architecture

```
┌───────────────────────────────┐
│ AI Client (Claude / Cursor)   │
└──────────────┬────────────────┘
               │ JSON-RPC (stdio)
               ▼
┌───────────────────────────────┐
│         android-mcp           │
│   (Model Context Protocol)    │
└──────────────┬────────────────┘
               │ ADB (Android Debug Bridge)
               ▼
┌───────────────────────────────┐
│ Android Device / Waydroid     │
└───────────────────────────────┘
```

---

## ✨ Features

- 👁️ **Vision Support**: Captures instant PNG screenshots directly into the LLM's context window.
- 🎯 **Smart UI Click**: Parse on-screen XML hierarchy (`uiautomator`) and click buttons by human label or text (e.g. `android_click_by_text("Sign In")`).
- 👆 **Gestures & Input**: Full support for precise taps, multi-point swipes/drags, and text typing.
- ⌨️ **Hardware Keys**: Send system keys (`BACK`, `HOME`, `ENTER`, `POWER`, `VOLUME`).
- 📱 **App Management**: Launch, stop, and inspect installed third-party apps.
- ⚡ **Zero External Pip Dependencies**: Built entirely on Python standard library and ADB.

---

## 🚀 Quick Setup

### 1. Prerequisites
Ensure `adb` is installed and your device or Waydroid container is connected:
```bash
# Verify ADB sees your device or emulator
adb devices
```

### 2. Connect to Claude Desktop

Open your Claude Desktop configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add `android-mcp` to your `mcpServers`:

```json
{
  "mcpServers": {
    "android": {
      "command": "python3",
      "args": ["/path/to/android-mcp/run_server.py"]
    }
  }
}
```

### 3. Connect to Cursor / Other MCP Clients

Add an entry pointing to `python3 /path/to/android-mcp/run_server.py` in your client's MCP settings tab.

---

## 🛠️ Available MCP Tools

| Tool Name | Description |
|---|---|
| `android_check_connection` | Verify device connection, model, and OS version |
| `android_screenshot` | Capture screen as base64 PNG for AI visual analysis |
| `android_click_by_text` | Find button or label by text and tap its center |
| `android_tap` | Tap exact screen coordinate `(x, y)` |
| `android_swipe` | Drag / swipe from `(x1, y1)` to `(x2, y2)` |
| `android_type_text` | Type string into the active focused input field |
| `android_press_key` | Press system key (`HOME`, `BACK`, `ENTER`, `POWER`) |
| `android_get_ui_tree` | Get list of all visible text elements and bounds |
| `android_launch_app` | Launch app by package name (e.g. `com.android.settings`) |
| `android_stop_app` | Force-stop an app package |
| `android_list_apps` | List installed application package names |
| `android_shell` | Run raw ADB shell command on device |

---

## 💬 Example Prompts for Your AI

Once connected in Claude or Cursor, you can ask your AI naturally:

- *"Check if my Android device is connected."*
- *"Take a screenshot of Android and tell me what screen is currently open."*
- *"Tap the Settings button on screen."*
- *"Type 'hello world' into the active search bar and press Enter."*
- *"Go back to the Home screen."*

---

## ⚙️ Environment Variables (Optional)

| Variable | Description |
|---|---|
| `ANDROID_SERIAL` | Specific device serial number to target (if multiple devices are connected) |
| `ANDROID_ADB_HOST` | Fallback TCP host:port to auto-connect (default: `127.0.0.1:5555`) |

---

## 🛡️ License

Distributed under the [MIT License](LICENSE). Free for personal and commercial use.
