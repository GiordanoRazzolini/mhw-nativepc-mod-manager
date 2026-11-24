import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

CONFIG_FILE = "config.json"

class MHWModManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monster Hunter World - NativePC Mod Manager")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # UI Styling
        style = ttk.Style()
        style.theme_use("clam")

        # Load saved paths or fallback to defaults
        self.config = self.load_config()

        # Top Frame: Path Selectors
        path_frame = ttk.LabelFrame(root, text=" Directory Configuration ", padding=10)
        path_frame.pack(fill="x", padx=10, pady=5)

        # Mods Main Directory
        ttk.Label(path_frame, text="Mods Main Directory:").grid(row=0, column=0, sticky="w", pady=2)
        self.mods_dir_var = tk.StringVar(value=self.config.get("mods_dir", r"D:\1 - Downloads\Mods"))
        ttk.Entry(path_frame, textvariable=self.mods_dir_var, width=50).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(path_frame, text="Browse...", command=self.browse_mods_dir).grid(row=0, column=2, pady=2)

        # Game NativePC Directory
        ttk.Label(path_frame, text="Game nativePC Directory:").grid(row=1, column=0, sticky="w", pady=2)
        self.game_dir_var = tk.StringVar(value=self.config.get("game_dir", r"D:\SteamLibrary\steamapps\common\Monster Hunter World\nativePC"))
        ttk.Entry(path_frame, textvariable=self.game_dir_var, width=50).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(path_frame, text="Browse...", command=self.browse_game_dir).grid(row=1, column=2, pady=2)

        path_frame.columnconfigure(1, weight=1)

        # Notebook (Tabbed View)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Valid Mods
        tab_valid = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_valid, text="Valid Mods (nativePC)")

        columns = ("name", "status")
        self.tree_valid = ttk.Treeview(tab_valid, columns=columns, show="headings", selectmode="extended")
        self.tree_valid.heading("name", text="Mod Name")
        self.tree_valid.heading("status", text="Installation Status")
        self.tree_valid.column("name", width=450, anchor="w")
        self.tree_valid.column("status", width=200, anchor="center")

        scrollbar_v = ttk.Scrollbar(tab_valid, orient="vertical", command=self.tree_valid.yview)
        self.tree_valid.configure(yscrollcommand=scrollbar_v.set)
        self.tree_valid.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")

        self.tree_valid.tag_configure("installed", foreground="green")
        self.tree_valid.tag_configure("not_installed", foreground="gray")
        self.tree_valid.tag_configure("partial", foreground="orange")

        # Tab 2: Invalid / Ignored Folders
        tab_invalid = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_invalid, text="Folders Missing nativePC")

        self.tree_invalid = ttk.Treeview(tab_invalid, columns=("name", "reason"), show="headings", selectmode="browse")
        self.tree_invalid.heading("name", text="Folder Name")
        self.tree_invalid.heading("reason", text="Status / Issue")
        self.tree_invalid.column("name", width=450, anchor="w")
        self.tree_invalid.column("reason", width=200, anchor="center")

        scrollbar_inv = ttk.Scrollbar(tab_invalid, orient="vertical", command=self.tree_invalid.yview)
        self.tree_invalid.configure(yscrollcommand=scrollbar_inv.set)
        self.tree_invalid.pack(side="left", fill="both", expand=True)
        scrollbar_inv.pack(side="right", fill="y")

        # Bottom Controls
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="Scan / Refresh Mods", command=self.refresh_mods).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Install Selected", command=self.install_selected_mods).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Uninstall Selected", command=self.uninstall_selected_mods).pack(side="left", padx=5)

        self.mods_data = []
        self.refresh_mods()

    def load_config(self):
        """Loads saved folder paths from config.json if present."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        """Saves current folder paths to config.json."""
        config = {
            "mods_dir": self.mods_dir_var.get(),
            "game_dir": self.game_dir_var.get()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def browse_mods_dir(self):
        folder = filedialog.askdirectory(title="Select Mods Directory")
        if folder:
            self.mods_dir_var.set(folder)
            self.save_config()
            self.refresh_mods()

    def browse_game_dir(self):
        folder = filedialog.askdirectory(title="Select Game nativePC Directory")
        if folder:
            self.game_dir_var.set(folder)
            self.save_config()
            self.refresh_mods()

    def check_mod_status(self, mod_nativepc_path, game_nativepc_path):
        if not os.path.exists(game_nativepc_path):
            return "Game Folder Missing", "not_installed"

        total_files = 0
        existing_files = 0

        for root, _, files in os.walk(mod_nativepc_path):
            for file in files:
                total_files += 1
                mod_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(mod_file_path, mod_nativepc_path)
                target_file_path = os.path.join(game_nativepc_path, rel_path)

                if os.path.exists(target_file_path):
                    existing_files += 1

        if total_files == 0:
            return "Empty Mod", "not_installed"
        if existing_files == total_files:
            return "Installed", "installed"
        elif existing_files > 0:
            return f"Partially Installed ({existing_files}/{total_files})", "partial"
        else:
            return "Not Installed", "not_installed"

    def refresh_mods(self):
        """Scans the mods directory for valid mods and invalid folders."""
        for item in self.tree_valid.get_children():
            self.tree_valid.delete(item)
        for item in self.tree_invalid.get_children():
            self.tree_invalid.delete(item)

        self.mods_data.clear()

        mods_dir = self.mods_dir_var.get()
        game_dir = self.game_dir_var.get()

        if not os.path.exists(mods_dir):
            return

        for entry in os.listdir(mods_dir):
            full_path = os.path.join(mods_dir, entry)
            if os.path.isdir(full_path):
                nativepc_path = os.path.join(full_path, "nativePC")
                if os.path.exists(nativepc_path) and os.path.isdir(nativepc_path):
                    status_str, tag = self.check_mod_status(nativepc_path, game_dir)
                    item_id = self.tree_valid.insert("", "end", values=(entry, status_str), tags=(tag,))
                    self.mods_data.append({
                        "id": item_id,
                        "name": entry,
                        "mod_nativepc": nativepc_path
                    })
                else:
                    self.tree_invalid.insert("", "end", values=(entry, "Missing nativePC folder"))

    def get_selected_mods(self):
        selected_items = self.tree_valid.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select one or more mods from the list.")
            return []
        
        selected_mods = []
        for item_id in selected_items:
            for mod in self.mods_data:
                if mod["id"] == item_id:
                    selected_mods.append(mod)
                    break
        return selected_mods

    def install_selected_mods(self):
        mods = self.get_selected_mods()
        if not mods:
            return

        game_dir = self.game_dir_var.get()
        if not os.path.exists(game_dir):
            try:
                os.makedirs(game_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create game nativePC folder:\n{e}")
                return

        total_copied = 0
        for mod in mods:
            mod_nativepc = mod["mod_nativepc"]
            for root, _, files in os.walk(mod_nativepc):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, mod_nativepc)
                    dest_path = os.path.join(game_dir, rel_path)

                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    total_copied += 1

        messagebox.showinfo("Success", f"Installed {len(mods)} mod(s) ({total_copied} total files copied).")
        self.refresh_mods()

    def uninstall_selected_mods(self):
        mods = self.get_selected_mods()
        if not mods:
            return

        game_dir = self.game_dir_var.get()
        if not os.path.exists(game_dir):
            messagebox.showwarning("Warning", "Game nativePC folder does not exist.")
            return

        total_deleted = 0
        for mod in mods:
            mod_nativepc = mod["mod_nativepc"]
            for root, _, files in os.walk(mod_nativepc):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, mod_nativepc)
                    dest_path = os.path.join(game_dir, rel_path)

                    if os.path.exists(dest_path):
                        try:
                            os.remove(dest_path)
                            total_deleted += 1
                        except Exception as e:
                            print(f"Error deleting {dest_path}: {e}")

        # Clean up empty directories in game's nativePC
        for root_dir, dirs, _ in os.walk(game_dir, topdown=False):
            for d in dirs:
                dir_path = os.path.join(root_dir, d)
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                    except Exception:
                        pass

        messagebox.showinfo("Success", f"Uninstalled {len(mods)} mod(s) ({total_deleted} total files removed).")
        self.refresh_mods()

if __name__ == "__main__":
    root = tk.Tk()
    app = MHWModManagerGUI(root)
    root.mainloop()