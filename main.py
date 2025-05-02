import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
import ipaddress

LANGUAGES = {
    "en": {
        "title": "Whitelist & Log Analyzer",
        "whitelist_mgmt": "Whitelist Management",
        "log_analysis": "Log Analysis",
        "add": "Add",
        "delete": "Delete",
        "save": "Save",
        "save_as": "Save As",
        "new": "New",
        "import": "Import",
        "export": "Export",
        "load_logs": "Load Logs",
        "analyze": "Analyze",
        "type": "Type",
        "value": "Value",
        "time": "Time",
        "result": "Result",
        "user": "User",
        "uuid": "UUID",
        "ip": "IP",
        "select_lang": "Please select language",
        "lang_en": "English",
        "lang_zh": "中文",
        "save_success": "Whitelist saved successfully",
        "invalid_type": "Invalid type! Must be uuid/name/ip",
        "invalid_ip": "Invalid IP address",
        "invalid_uuid": "Invalid UUID format",
        "total_logs": "Total logs",
        "allowed": "Allowed",
        "denied": "Denied",
        "confirm_new": "Create new whitelist?\nUnsaved changes will be lost!",
        "file_type_json": "JSON files",
        "import_success": "Import successful",
        "export_success": "Export successful",
        "invalid_file": "Invalid file format",
        "overwrite_prompt": "Overwrite original file?\nCancel to save as new file",
        "new_file_prompt": "Select save location for new whitelist"
    },
    "zh": {
        "title": "白名单与日志分析工具",
        "whitelist_mgmt": "白名单管理",
        "log_analysis": "日志分析",
        "add": "添加",
        "delete": "删除",
        "save": "保存",
        "save_as": "另存为",
        "new": "新建",
        "import": "导入",
        "export": "导出",
        "load_logs": "加载日志",
        "analyze": "分析",
        "type": "类型",
        "value": "值",
        "time": "时间",
        "result": "结果",
        "user": "用户名",
        "uuid": "UUID",
        "ip": "IP地址",
        "select_lang": "请选择语言",
        "lang_en": "英文",
        "lang_zh": "中文",
        "save_success": "白名单保存成功",
        "invalid_type": "无效类型！必须是 uuid/name/ip",
        "invalid_ip": "无效的IP地址",
        "invalid_uuid": "无效的UUID格式",
        "total_logs": "总日志数",
        "allowed": "允许次数",
        "denied": "拒绝次数",
        "confirm_new": "确认新建白名单？\n未保存的修改将会丢失！",
        "file_type_json": "JSON文件",
        "import_success": "导入成功",
        "export_success": "导出成功",
        "invalid_file": "无效的文件格式",
        "overwrite_prompt": "覆盖原始文件？\n取消将另存为新文件",
        "new_file_prompt": "选择新白名单保存位置"
    }
}


class LanguageDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.result = None
        self.title(LANGUAGES["en"]["select_lang"])
        self.geometry("300x150")

        ttk.Label(self, text=LANGUAGES["en"]["select_lang"]).pack(pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="English", command=lambda: self.set_lang("en")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="中文", command=lambda: self.set_lang("zh")).pack(side=tk.LEFT, padx=5)

    def set_lang(self, lang):
        self.result = lang
        self.destroy()


class WhitelistManager:
    def __init__(self, master):
        self.master = master
        self.lang = self.load_config()
        self.apply_language()

        self.whitelist = []
        self.log_files = []
        self.log_data = []
        self.current_whitelist_path = None

        self.create_widgets()
        self.load_initial_whitelist()

    def load_config(self):
        config_path = "config.json"
        if not os.path.exists(config_path):
            lang_dialog = LanguageDialog(self.master)
            self.master.wait_window(lang_dialog)
            lang = lang_dialog.result or "en"
            with open(config_path, "w") as f:
                json.dump({"language": lang}, f)
            return lang

        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("language", "en")

    def apply_language(self):
        self.text = LANGUAGES.get(self.lang, LANGUAGES["en"])
        self.master.title(self.text["title"])

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 白名单管理区域
        whitelist_frame = ttk.LabelFrame(main_frame, text=self.text["whitelist_mgmt"])
        whitelist_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 日志分析区域
        log_frame = ttk.LabelFrame(main_frame, text=self.text["log_analysis"])
        log_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)

        # 白名单组件
        self.whitelist_tree = ttk.Treeview(whitelist_frame, columns=("type", "value"), show="headings")
        self.whitelist_tree.heading("type", text=self.text["type"])
        self.whitelist_tree.heading("value", text=self.text["value"])
        self.whitelist_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(whitelist_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text=self.text["new"], command=self.new_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["import"], command=self.import_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["add"], command=self.add_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["delete"], command=self.delete_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["export"], command=self.export_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["save"], command=self.save_whitelist).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=self.text["save_as"], command=self.save_as_whitelist).pack(side=tk.LEFT, padx=2)

        # 日志组件
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(log_control_frame, text=self.text["load_logs"], command=self.load_logs).pack(side=tk.LEFT)
        ttk.Button(log_control_frame, text=self.text["analyze"], command=self.analyze_logs).pack(side=tk.LEFT, padx=5)

        self.log_tree = ttk.Treeview(log_frame, columns=("time", "result", "user", "uuid", "ip"), show="headings")
        self.log_tree.heading("time", text=self.text["time"])
        self.log_tree.heading("result", text=self.text["result"])
        self.log_tree.heading("user", text=self.text["user"])
        self.log_tree.heading("uuid", text=self.text["uuid"])
        self.log_tree.heading("ip", text=self.text["ip"])
        self.log_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_initial_whitelist(self):
        try:
            if os.path.exists("cwhitelist_entries.json"):
                self.current_whitelist_path = "cwhitelist_entries.json"
                with open(self.current_whitelist_path, "r") as f:
                    self.whitelist = json.load(f)
                    self.update_whitelist_tree()
        except Exception as e:
            messagebox.showerror(self.text["title"], f"加载白名单失败: {str(e)}")

    def update_whitelist_tree(self):
        self.whitelist_tree.delete(*self.whitelist_tree.get_children())
        for item in self.whitelist:
            self.whitelist_tree.insert("", "end", values=(item["type"], item["value"]))

    def add_whitelist(self):
        def validate():
            w_type = type_var.get().lower()
            value = value_entry.get()

            if w_type not in ["uuid", "name", "ip"]:
                messagebox.showerror(self.text["title"], self.text["invalid_type"])
                return

            if w_type == "ip" and not self.validate_ip(value):
                messagebox.showerror(self.text["title"], self.text["invalid_ip"])
                return

            if w_type == "uuid" and not self.validate_uuid(value):
                messagebox.showerror(self.text["title"], self.text["invalid_uuid"])
                return

            self.whitelist.append({"type": w_type, "value": value})
            self.update_whitelist_tree()
            add_win.destroy()

        add_win = tk.Toplevel(self.master)
        add_win.title(self.text["add"])

        ttk.Label(add_win, text=f"{self.text['type']}:").grid(row=0, column=0, padx=5, pady=5)
        type_var = tk.StringVar()
        type_combobox = ttk.Combobox(add_win, textvariable=type_var, values=["UUID", "Name", "IP"])
        type_combobox.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_win, text=f"{self.text['value']}:").grid(row=1, column=0, padx=5, pady=5)
        value_entry = ttk.Entry(add_win)
        value_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(add_win, text=self.text["add"], command=validate).grid(row=2, columnspan=2, pady=5)

    def delete_whitelist(self):
        selected = self.whitelist_tree.selection()
        if not selected:
            return

        for item in reversed(selected):
            index = self.whitelist_tree.index(item)
            del self.whitelist[index]
        self.update_whitelist_tree()

    def validate_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def validate_uuid(self, uuid):
        pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
        return bool(pattern.match(uuid))

    # 文件操作方法
    def new_whitelist(self):
        if not messagebox.askyesno(self.text["title"], self.text["confirm_new"]):
            return

        file_path = filedialog.asksaveasfilename(
            title=self.text["new_file_prompt"],
            defaultextension=".json",
            filetypes=((self.text["file_type_json"], "*.json"), ("All files", "*.*")))

        if not file_path:
            return

        try:
            self.whitelist = []
            self.current_whitelist_path = file_path
            self.save_whitelist()
            self.update_whitelist_tree()
        except Exception as e:
            messagebox.showerror(self.text["title"], f"创建失败: {str(e)}")

    def import_whitelist(self):
        file_path = filedialog.askopenfilename(
            title=self.text["import"],
            filetypes=((self.text["file_type_json"], "*.json"), ("All files", "*.*")))

        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                new_data = json.load(f)
                if self.validate_whitelist_format(new_data):
                    self.whitelist = new_data
                    self.current_whitelist_path = file_path
                    self.update_whitelist_tree()
                    messagebox.showinfo(self.text["title"], self.text["import_success"])
                else:
                    messagebox.showerror(self.text["title"], self.text["invalid_file"])
        except Exception as e:
            messagebox.showerror(self.text["title"], f"{self.text['invalid_file']}: {str(e)}")

    def export_whitelist(self):
        file_path = filedialog.asksaveasfilename(
            title=self.text["export"],
            defaultextension=".json",
            filetypes=((self.text["file_type_json"], "*.json"), ("All files", "*.*")))

        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                json.dump(self.whitelist, f, indent=2)
            messagebox.showinfo(self.text["title"], self.text["export_success"])
        except Exception as e:
            messagebox.showerror(self.text["title"], f"导出失败: {str(e)}")

    def save_whitelist(self):
        if not self.current_whitelist_path:
            self.save_as_whitelist()
            return

        if os.path.exists(self.current_whitelist_path):
            if not messagebox.askyesno(self.text["title"], self.text["overwrite_prompt"]):
                self.save_as_whitelist()
                return

        try:
            with open(self.current_whitelist_path, "w") as f:
                json.dump(self.whitelist, f, indent=2)
            messagebox.showinfo(self.text["title"], self.text["save_success"])
        except Exception as e:
            messagebox.showerror(self.text["title"], f"保存失败: {str(e)}")

    def save_as_whitelist(self):
        file_path = filedialog.asksaveasfilename(
            title=self.text["save_as"],
            defaultextension=".json",
            filetypes=((self.text["file_type_json"], "*.json"), ("All files", "*.*")))

        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                json.dump(self.whitelist, f, indent=2)
            self.current_whitelist_path = file_path
            messagebox.showinfo(self.text["title"], self.text["save_success"])
        except Exception as e:
            messagebox.showerror(self.text["title"], f"另存失败: {str(e)}")

    def validate_whitelist_format(self, data):
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            if "type" not in item or "value" not in item:
                return False
            if item["type"] not in ["uuid", "name", "ip"]:
                return False
        return True

    # 日志分析方法（保持原有实现）
    def load_logs(self):
        files = filedialog.askopenfilenames(
            title=self.text["load_logs"],
            filetypes=(("Log files", "*.log"), ("All files", "*.*")))

        self.log_files = files
        self.log_data = []

        for file in files:
            with open(file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        self.log_data.append({
                            "time": parts[0][1:-1],
                            "result": parts[1][1:-1],
                            "user": parts[2],
                            "uuid": parts[3],
                            "ip": parts[4]
                        })

        self.update_log_tree()

    def analyze_logs(self):
        allow_count = sum(1 for log in self.log_data if log["result"] == "ALLOW")
        deny_count = len(self.log_data) - allow_count

        messagebox.showinfo(
            self.text["title"],
            f"{self.text['total_logs']}: {len(self.log_data)}\n"
            f"{self.text['allowed']}: {allow_count}\n"
            f"{self.text['denied']}: {deny_count}"
        )

    def update_log_tree(self):
        self.log_tree.delete(*self.log_tree.get_children())
        for log in self.log_data:
            self.log_tree.insert("", "end", values=(
                log["time"],
                log["result"],
                log["user"],
                log["uuid"],
                log["ip"]
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = WhitelistManager(root)
    root.mainloop()