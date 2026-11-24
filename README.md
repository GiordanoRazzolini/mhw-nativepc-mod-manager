# Monster Hunter World - NativePC Mod Manager

A lightweight Windows GUI tool for managing `nativePC` mods in Monster Hunter: World without overwriting or losing track of files across multiple subfolders.

## Features
- **Batch Install & Uninstall:** Select multiple mods at once (`Ctrl+Click` or `Shift+Click`) to install or cleanly remove their exact files.
- **Live Status Detection:** Automatically checks if a mod is `Installed`, `Partially Installed`, or `Not Installed`.
- **Folder Validation:** Flags folders in your mods directory that are missing a `nativePC` subfolder.
- **Persistent Paths:** Remembers your configured directories between sessions.

## Download & Usage (No Python Required)
1. Go to the **[Releases](../../releases)** page and download `modmanager.exe`.
2. Run `modmanager.exe` (if Windows Defender SmartScreen appears, click *More info* -> *Run anyway*).
3. Select your **Mods Main Directory** and your game's **`nativePC` Directory**.
4. Select one or more mods from the list and click **Install Selected** or **Uninstall Selected**.

## Running from Source
Requires Python 3.x (uses built-in `tkinter`, no external packages needed):
```bash
python modmanager.py
