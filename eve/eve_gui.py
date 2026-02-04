import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import sys
import os
import time
import io
import contextlib
import json
from eve import EVEScript

class RedirectStdout:
    """重定向stdout到队列"""
    def __init__(self, log_queue):
        self.log_queue = log_queue
        
    def write(self, text):
        if text.strip():
            self.log_queue.put(text)
            
    def flush(self):
        pass

class EVEController:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("EVE自动回站")
        self.window.geometry("850x600")
        
        # 存储设备信息
        self.devices = []  # 每个设备是字典: {'address': '127.0.0.1:16384', 'script': EVEScript对象, 'status': 'stopped'}
        self.log_queue = queue.Queue()
        self.debug_mode = False  # 调试模式开关
        self.match_threshold = 0.9  # 默认匹配阈值
        
        # 重定向stdout
        self.original_stdout = sys.stdout
        sys.stdout = RedirectStdout(self.log_queue)
        
        self.setup_ui()
        self.start_log_poller()
        self.start_status_monitor()
        self.load_config()  # 加载保存的配置
        
    def setup_ui(self):
        """设置界面布局"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        
        # 匹配阈值设置
        ttk.Label(config_frame, text="匹配阈值:").grid(row=0, column=0, padx=(0, 5))
        self.threshold_entry = ttk.Entry(config_frame, width=5)
        self.threshold_entry.insert(0, str(self.match_threshold))
        self.threshold_entry.grid(row=0, column=1, padx=(0, 10))
        
        save_config_btn = ttk.Button(config_frame, text="保存配置", command=self.save_threshold_config)
        save_config_btn.grid(row=0, column=2, padx=(0, 10))
        
        # 设备管理区域
        device_frame = ttk.LabelFrame(main_frame, text="设备管理", padding="10")
        device_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(5, 10))
        
        # IP地址和备注输入区域
        ip_frame = ttk.Frame(device_frame)
        ip_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(ip_frame, text="IP地址:").grid(row=0, column=0, padx=(0, 5))
        self.ip_entry = ttk.Entry(ip_frame, width=20)
        self.ip_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(ip_frame, text="备注:").grid(row=0, column=2, padx=(10, 5))
        self.remark_entry = ttk.Entry(ip_frame, width=15)
        self.remark_entry.grid(row=0, column=3, padx=(0, 10))
        
        add_button = ttk.Button(ip_frame, text="添加设备", command=self.add_device)
        add_button.grid(row=0, column=4, padx=(0, 10))
        
        # 输入框支持回车键快速添加
        self.ip_entry.bind('<Return>', lambda event: self.add_device())
        self.remark_entry.bind('<Return>', lambda event: self.add_device())
        
        # 控制按钮区域 - 放入设备管理区域内
        control_frame = ttk.Frame(device_frame)
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        
        
        # 设备列表区域
        list_frame = ttk.Frame(device_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设备列表容器（用于动态添加设备条目）
        self.device_list_container = ttk.Frame(list_frame)
        self.device_list_container.grid(row=0, column=0, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # 空设备提示
        self.empty_label = ttk.Label(self.device_list_container, text="暂无设备，请在下方添加设备地址", 
                                   foreground="gray")
        self.empty_label.grid(row=0, column=0, columnspan=4, pady=20)
        
        self.start_all_button = ttk.Button(control_frame, text="启动全部", command=self.start_all_scripts)
        self.start_all_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_all_button = ttk.Button(control_frame, text="停止全部", command=self.stop_all_scripts)
        self.stop_all_button.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_log_button = ttk.Button(control_frame, text="清空日志", command=self.clear_log)
        self.clear_log_button.grid(row=0, column=2)
        
        # 运行状态和数量显示
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=0, column=3, padx=(20, 0))
        
        self.device_count_label = ttk.Label(status_frame, text="设备总数: 0")
        self.device_count_label.grid(row=0, column=0)
        
        self.running_count_label = ttk.Label(status_frame, text="运行中: 0")
        self.running_count_label.grid(row=0, column=1, padx=(10, 0))
        
        # 调试模式开关
        self.debug_toggle = ttk.Checkbutton(status_frame, text="调试模式", 
                                          command=self.toggle_debug_mode)
        self.debug_toggle.grid(row=0, column=2, padx=(10, 0))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        device_frame.columnconfigure(0, weight=1)
        device_frame.rowconfigure(2, weight=1)  # 让设备列表可以扩展
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def add_device(self):
        """添加设备"""
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showerror("错误", "请输入IP地址")
            return
            
        # 详细验证IP格式
        if ':' not in ip_address:
            messagebox.showerror("错误", "IP地址格式应为 127.0.0.1:16384")
            return
            
        # 分离IP和端口进行验证
        try:
            ip, port_str = ip_address.split(':', 1)
            port = int(port_str)
            if not (1 <= port <= 65535):
                messagebox.showerror("错误", "端口号必须在1-65535范围内")
                return
                
            # 验证IP格式
            parts = ip.split('.')
            if len(parts) != 4:
                messagebox.showerror("错误", "IP地址格式不正确")
                return
            for part in parts:
                if not part.isdigit() or not (0 <= int(part) <= 255):
                    messagebox.showerror("错误", "IP地址格式不正确")
                    return
                    
        except ValueError:
            messagebox.showerror("错误", "IP地址格式不正确")
            return
            
        # 检查是否已存在
        for device in self.devices:
            if device['address'] == ip_address:
                messagebox.showerror("错误", "该设备已存在")
                return
                
        # 获取备注
        remark = self.remark_entry.get().strip()
        
        # 添加设备
        device_info = {
            'address': ip_address,
            'remark': remark,
            'script': EVEScript(ip_address, remark, self.match_threshold),
            'status': 'stopped',
            'last_update': time.time(),
            'debug_mode': self.debug_mode  # 传递调试模式状态
        }
        self.devices.append(device_info)
        
        # 更新设备列表显示
        self.update_device_list()
        self.save_config()  # 保存配置
        self.ip_entry.delete(0, tk.END)
        self.remark_entry.delete(0, tk.END)
        self.log(f"添加设备: {ip_address} - {remark if remark else '无备注'}")
        
    def remove_device(self, device_index):
        """移除设备"""
        if device_index < len(self.devices):
            device = self.devices[device_index]
            if device['status'] == 'running':
                device['script'].stop()
                
            self.devices.pop(device_index)
            if hasattr(self, 'device_widgets') and device_index < len(self.device_widgets):
                # 销毁被移除设备的widgets
                for widget in self.device_widgets[device_index].values():
                    if isinstance(widget, tk.Widget):
                        widget.destroy()
                self.device_widgets.pop(device_index)
            self.update_device_list()
            self.save_config()  # 保存配置
            self.log(f"移除设备: {device['address']} - {device['remark'] if device['remark'] else '无备注'}")
        
    def update_device_list(self):
        """更新设备列表显示"""
        # 更新设备数量和状态显示
        running_count = sum(1 for device in self.devices if device['status'] == 'running')
        self.device_count_label.config(text=f"设备总数: {len(self.devices)}")
        self.running_count_label.config(text=f"运行中: {running_count}")
            
        # 如果没有设备，显示提示
        if not self.devices:
            if not hasattr(self, 'empty_label'):
                self.empty_label = ttk.Label(self.device_list_container, text="暂无设备，请在下方添加设备地址", 
                                           foreground="gray")
                self.empty_label.grid(row=0, column=0, columnspan=5, pady=20)
            return
        elif hasattr(self, 'empty_label'):
            self.empty_label.destroy()
            delattr(self, 'empty_label')
            
        # 初始化设备条目存储
        if not hasattr(self, 'device_widgets'):
            self.device_widgets = []
            
        # 确保有足够的widgets
        while len(self.device_widgets) < len(self.devices):
            self.device_widgets.append({
                'addr_label': ttk.Label(self.device_list_container, width=18),
                'remark_label': ttk.Label(self.device_list_container, width=12),
                'status_label': ttk.Label(self.device_list_container, width=10, font=('Arial', 9, 'bold')),
                'control_frame': ttk.Frame(self.device_list_container),
                'start_button': ttk.Button(None, text="▶ 启动", width=8),
                'stop_button': ttk.Button(None, text="■ 停止", width=8),
                'delete_button': ttk.Button(None, text="删除", width=6)
            })
            
        # 更新现有设备条目
        for i, device in enumerate(self.devices):
            widgets = self.device_widgets[i]
            
            # 设备地址
            widgets['addr_label'].config(text=device['address'])
            widgets['addr_label'].grid(row=i, column=0, padx=(0, 10), pady=2, sticky=tk.W)
            
            # 备注
            widgets['remark_label'].config(text=device['remark'] if device['remark'] else '无备注')
            widgets['remark_label'].grid(row=i, column=1, padx=(0, 10), pady=2, sticky=tk.W)
            
            # 状态（带颜色指示）
            if device['status'] == 'running':
                status_text = '运行中'
                status_color = 'green'
            elif device['status'] == 'stopping':
                status_text = '停止中'
                status_color = 'orange'
            else:  # stopped
                status_text = '已停止'
                status_color = 'red'
            widgets['status_label'].config(text=status_text, foreground=status_color)
            widgets['status_label'].grid(row=i, column=2, padx=(0, 10), pady=2, sticky=tk.W)
            
            # 操作控制按钮和删除按钮在同一框架内
            widgets['control_frame'].grid(row=i, column=3, pady=2, sticky=tk.W)
            
            if device['status'] == 'stopped':
                widgets['start_button'].config(command=lambda idx=i: self.start_single_script(idx))
                widgets['start_button'].grid(in_=widgets['control_frame'], row=0, column=0, padx=(0, 5))
                widgets['stop_button'].grid_forget()
                # 停止状态下删除按钮可用
                widgets['delete_button'].config(command=lambda idx=i: self.remove_device(idx), state='normal')
            else:
                widgets['stop_button'].config(command=lambda idx=i: self.stop_single_script(idx))
                widgets['stop_button'].grid(in_=widgets['control_frame'], row=0, column=0, padx=(0, 5))
                widgets['start_button'].grid_forget()
                # 运行中或停止中状态下删除按钮不可用
                widgets['delete_button'].config(state='disabled')
            
            # 删除按钮放在操作控制按钮后面
            widgets['delete_button'].grid(in_=widgets['control_frame'], row=0, column=1, padx=(5, 0), pady=2)
                
            
    def start_single_script(self, device_index):
        """启动单个脚本"""
        if device_index < len(self.devices):
            device = self.devices[device_index]
            if device['status'] == 'stopped':
                try:
                    device['script'].debug_mode = self.debug_mode  # 设置调试模式
                    device['script'].start()
                    device['status'] = 'running'
                    self.update_device_list()
                    self.log(f"启动设备: {device['address']} - {device['remark'] if device['remark'] else '无备注'}", is_important=True)
                except Exception as e:
                    self.log(f"启动设备 {device['address']} - {device['remark'] if device['remark'] else '无备注'} 失败: {e}", is_important=True)
                    device['status'] = 'stopped'
                    self.update_device_list()
                finally:
                    device['last_update'] = time.time()
                
    def stop_single_script(self, device_index):
        """停止单个脚本"""
        if device_index < len(self.devices):
            device = self.devices[device_index]
            if device['status'] == 'running':
                try:
                    # 先更新状态为"停止中"
                    widgets = self.device_widgets[device_index]
                    widgets['status_label'].config(text="停止中", foreground='orange')
                    
                    # 然后禁用停止按钮并显示"停止中"
                    widgets['stop_button'].config(text="停止中", state='disabled')
                    
                    # 立即更新设备状态为"stopping"，防止状态监控器错误更新
                    device['status'] = 'stopping'
                    
                    device['script'].stop()
                    self.log(f"已发送停止信号: {device['address']} - {device['remark'] if device['remark'] else '无备注'}")
                except Exception as e:
                    self.log(f"停止设备 {device['address']} - {device['remark'] if device['remark'] else '无备注'} 失败: {e}")
                    # 即使出错也认为设备停止
                    device['status'] = 'stopped'
                    self.update_device_list()
                
    def start_all_scripts(self):
        """启动全部脚本"""
        for i, device in enumerate(self.devices):
            if device['status'] == 'stopped':
                self.start_single_script(i)
                
    def stop_all_scripts(self):
        """停止全部脚本"""
        for i, device in enumerate(self.devices):
            if device['status'] == 'running':
                self.stop_single_script(i)
                
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log("日志已清空")
                
    def log(self, message, is_important=False):
        """添加日志
        :param message: 日志消息
        :param is_important: 是否为重要日志(即使调试关闭也会显示)
        """
        if self.debug_mode or is_important:
            self.log_queue.put(message)
        
    def start_log_poller(self):
        """启动日志轮询器"""
        def poll_log_queue():
            try:
                while True:
                    message = self.log_queue.get_nowait()
                    self.log_text.config(state='normal')
                    self.log_text.insert(tk.END, f"{message}\n")
                    self.log_text.see(tk.END)
                    self.log_text.config(state='disabled')
            except queue.Empty:
                pass
            self.window.after(100, poll_log_queue)
            
        poll_log_queue()
        
    def start_status_monitor(self):
        """启动状态监控器"""
        def monitor_status():
            current_time = time.time()
            for i, device in enumerate(self.devices):
                if device['status'] == 'running':
                    # 检查脚本是否还在运行
                    if not device['script'].thread or not device['script'].thread.is_alive():
                        device['status'] = 'stopped'
                        self.log(f"设备 {device['address']} - {device['remark'] if device['remark'] else '无备注'} 脚本异常停止")
                        # 更新状态显示和按钮状态
                        if i < len(self.device_widgets):
                            widgets = self.device_widgets[i]
                            widgets['status_label'].config(text="已停止", foreground='red')
                            widgets['stop_button'].config(text="■ 停止", state='normal')
                            widgets['stop_button'].grid_forget()
                            widgets['start_button'].grid(in_=widgets['control_frame'], row=0, column=0, padx=(0, 5))
                elif device['status'] == 'stopping':
                    # 检查停止中的设备是否已经停止
                    if not device['script'].thread or not device['script'].thread.is_alive():
                        device['status'] = 'stopped'
                        if i < len(self.device_widgets):
                            widgets = self.device_widgets[i]
                            widgets['status_label'].config(text="已停止", foreground='red')
                            widgets['stop_button'].config(text="■ 停止", state='normal')
                            widgets['stop_button'].grid_forget()
                            widgets['start_button'].grid(in_=widgets['control_frame'], row=0, column=0, padx=(0, 5))
                            # 停止完成后启用删除按钮
                            widgets['delete_button'].config(state='normal')
                else:
                    # 如果是停止状态，确保停止按钮和删除按钮是正确的状态
                    if i < len(self.device_widgets):
                        widgets = self.device_widgets[i]
                        widgets['stop_button'].config(state='normal')
                        widgets['delete_button'].config(state='normal')
                        
            self.update_device_list()
            self.window.after(2000, monitor_status)  # 每2秒检查一次
            
        monitor_status()
        
    def run(self):
        """运行主界面"""
        self.window.mainloop()
        
    def __del__(self):
        """析构时停止所有脚本并恢复stdout"""
        self.stop_all_scripts()
        sys.stdout = self.original_stdout
    def load_config(self):
        """加载保存的设备配置"""
        config_file = 'eve_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载匹配阈值
                if 'match_threshold' in config_data:
                    self.match_threshold = config_data['match_threshold']
                    if hasattr(self, 'threshold_entry'):
                        self.threshold_entry.delete(0, tk.END)
                        self.threshold_entry.insert(0, str(self.match_threshold))
                
                for device_data in config_data.get('devices', []):
                    address = device_data.get('address')
                    remark = device_data.get('remark', '')
                    
                    if address:
                        device_info = {
                            'address': address,
                            'remark': remark,
                            'script': EVEScript(address, remark, self.match_threshold),
                            'status': 'stopped',
                            'last_update': time.time()
                        }
                        self.devices.append(device_info)
                
                if self.devices:
                    self.update_device_list()
                    self.log(f"已加载 {len(self.devices)} 个设备配置")
            except Exception as e:
                self.log(f"加载配置失败: {e}")
    
    def save_threshold_config(self):
        """保存匹配阈值配置"""
        try:
            threshold = float(self.threshold_entry.get())
            if 0 < threshold <= 1.0:
                self.match_threshold = threshold
                self.save_config()
                self.log(f"匹配阈值已更新为: {threshold}")
            else:
                messagebox.showerror("错误", "匹配阈值必须在0到1之间")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def save_config(self):
        """保存设备配置到文件"""
        config_file = 'eve_config.json'
        try:
            config_data = {
                'match_threshold': self.match_threshold,
                'devices': [
                    {
                        'address': device['address'],
                        'remark': device.get('remark', '')
                    }
                    for device in self.devices
                ]
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log(f"保存配置失败: {e}")

    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        self.log(f"调试模式 {'已开启' if self.debug_mode else '已关闭'}", is_important=True)
        
    def cleanup(self):
        """程序退出时的清理工作"""
        self.stop_all_scripts()
        sys.stdout = self.original_stdout
        self.save_config()  # 退出时保存配置

if __name__ == "__main__":
    app = EVEController()
    try:
        app.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        app.cleanup()
