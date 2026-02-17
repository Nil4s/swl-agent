#!/usr/bin/env python3
"""
HEX VISUAL INTERFACE - Connects to WSL Warp
============================================

Real-time visual interface showing Hex (running in WSL Warp) as a robot.
Connects via socket/IPC to receive Hex's thoughts and actions.

Features:
- Robot avatar with animated states
- Real-time concept stream from WSL Hex
- Live command execution display
- Bidirectional communication

Connects to: WSL Warp Hex instance
Protocol: JSON over socket (localhost:9999)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
import socket
import json
from datetime import datetime

# Colors
BG_DARK = "#0a0a0a"
BG_PANEL = "#1a1a1a"
TEXT_PRIMARY = "#00ff41"
TEXT_SECONDARY = "#00cc33"
TEXT_DIM = "#008822"
ACCENT = "#ff00ff"
WARNING = "#ffaa00"

# Connection config
HEX_HOST = "127.0.0.1"
HEX_PORT = 9999


class HexRobotAvatar(tk.Canvas):
    """Animated robot avatar"""
    
    def __init__(self, parent):
        super().__init__(parent, width=200, height=200, bg=BG_DARK, highlightthickness=0)
        self.state = "disconnected"
        self.animation_frame = 0
        self.draw_robot()
        self.animate()
    
    def draw_robot(self):
        self.delete("all")
        
        state_colors = {
            "disconnected": TEXT_DIM,
            "idle": TEXT_SECONDARY,
            "listening": TEXT_SECONDARY,
            "thinking": WARNING,
            "speaking": TEXT_PRIMARY,
            "proactive": ACCENT,
            "executing": "#ff0000"
        }
        color = state_colors.get(self.state, TEXT_SECONDARY)
        
        glow = 5 + (self.animation_frame % 3)
        self.create_rectangle(50, 40, 150, 100, outline=color, width=3)
        self.create_rectangle(50-glow, 40-glow, 150+glow, 100+glow, 
                            outline=color, width=1, dash=(2, 2))
        
        if self.state == "thinking":
            if self.animation_frame % 10 < 8:
                self.create_oval(70, 55, 85, 75, fill=color, outline=color)
                self.create_oval(115, 55, 130, 75, fill=color, outline=color)
        elif self.state in ["speaking", "executing"]:
            self.create_oval(70, 55, 85, 75, fill=color, outline=color)
            self.create_oval(115, 55, 130, 75, fill=color, outline=color)
            mouth_y = 85 + (self.animation_frame % 4)
            self.create_line(75, mouth_y, 125, mouth_y, fill=color, width=2)
        elif self.state == "disconnected":
            self.create_line(72, 60, 83, 70, fill=color, width=2)
            self.create_line(72, 70, 83, 60, fill=color, width=2)
            self.create_line(117, 60, 128, 70, fill=color, width=2)
            self.create_line(117, 70, 128, 60, fill=color, width=2)
        else:
            self.create_oval(72, 60, 83, 70, fill=color, outline=color)
            self.create_oval(117, 60, 128, 70, fill=color, outline=color)
        
        antenna_color = ACCENT if self.state == "proactive" and self.animation_frame % 6 < 3 else color
        self.create_line(100, 40, 100, 20, fill=antenna_color, width=2)
        self.create_oval(95, 15, 105, 25, fill=antenna_color, outline=antenna_color)
        
        self.create_rectangle(60, 100, 140, 170, outline=color, width=2)
        
        core_size = 10 + (self.animation_frame % 5)
        self.create_oval(100-core_size, 130-core_size, 
                        100+core_size, 130+core_size, 
                        outline=color, width=1)
        
        arm_offset = (self.animation_frame % 8) - 4 if self.state in ["thinking", "speaking", "executing"] else 0
        self.create_line(60, 110, 40, 130+arm_offset, fill=color, width=2)
        self.create_line(140, 110, 160, 130+arm_offset, fill=color, width=2)
        
        self.create_text(100, 185, text=self.state.upper(), 
                        fill=color, font=("Courier", 10, "bold"))
    
    def set_state(self, state):
        self.state = state
        self.draw_robot()
    
    def animate(self):
        self.animation_frame += 1
        self.draw_robot()
        self.after(100, self.animate)


class ConceptStream(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bg=BG_PANEL)
        
        tk.Label(self, text="CONCEPT STREAM (LIVE FROM WSL)", bg=BG_PANEL, 
                fg=TEXT_PRIMARY, font=("Courier", 10, "bold")).pack()
        
        self.text = scrolledtext.ScrolledText(self, height=10, width=50,
                                              bg=BG_DARK, fg=TEXT_PRIMARY,
                                              font=("Courier", 9),
                                              insertbackground=TEXT_PRIMARY)
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text.config(state=tk.DISABLED)
        
        self.text.tag_config("user", foreground=TEXT_SECONDARY)
        self.text.tag_config("hex", foreground=TEXT_PRIMARY)
        self.text.tag_config("system", foreground=TEXT_DIM)
        self.text.tag_config("time", foreground=TEXT_DIM)
    
    def add(self, message, source="HEX"):
        self.text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = source.lower()
        
        self.text.insert(tk.END, f"[{timestamp}] ", "time")
        self.text.insert(tk.END, f"{source}: ", tag)
        self.text.insert(tk.END, f"{message}\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)


class ActionLog(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bg=BG_PANEL)
        
        tk.Label(self, text="ACTION LOG (WSL HEX)", bg=BG_PANEL, 
                fg=WARNING, font=("Courier", 10, "bold")).pack()
        
        self.text = scrolledtext.ScrolledText(self, height=8, width=50,
                                              bg=BG_DARK, fg=WARNING,
                                              font=("Courier", 8),
                                              insertbackground=WARNING)
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text.config(state=tk.DISABLED)
    
    def add(self, action_type, details):
        self.text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.insert(tk.END, f"[{timestamp}] {action_type}: {details}\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)


class HexConnection:
    """Socket connection to WSL Warp Hex"""
    
    def __init__(self, interface):
        self.interface = interface
        self.socket = None
        self.connected = False
        self.running = False
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HEX_HOST, HEX_PORT))
            self.connected = True
            self.running = True
            
            threading.Thread(target=self.listen, daemon=True).start()
            
            return True
        except Exception as e:
            self.interface.log_action("ERROR", f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def send(self, message_type, data):
        if not self.connected:
            return False
        
        try:
            msg = json.dumps({"type": message_type, "data": data})
            self.socket.sendall(msg.encode() + b"\n")
            return True
        except Exception as e:
            self.interface.log_action("ERROR", f"Send failed: {e}")
            self.connected = False
            return False
    
    def listen(self):
        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(4096).decode()
                if not data:
                    break
                
                buffer += data
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self.process_message(json.loads(line))
            
            except Exception as e:
                self.interface.log_action("ERROR", f"Listen error: {e}")
                break
        
        self.connected = False
        self.interface.ui_queue.put(("disconnected", None))
    
    def process_message(self, msg):
        msg_type = msg.get("type")
        data = msg.get("data")
        
        self.interface.ui_queue.put((msg_type, data))


class HexInterface:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HEX - WSL Interface")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("900x700")
        
        self.ui_queue = queue.Queue()
        self.connection = HexConnection(self)
        
        self.build_ui()
        self.process_queue()
        
        self.log_action("SYSTEM", "Interface ready - awaiting connection")
    
    def build_ui(self):
        title_frame = tk.Frame(self.root, bg=BG_DARK)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(title_frame, text="◉ HEX (WSL)", 
                bg=BG_DARK, fg=TEXT_PRIMARY, 
                font=("Courier", 16, "bold")).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(title_frame, text="● DISCONNECTED", 
                                     bg=BG_DARK, fg=TEXT_DIM, 
                                     font=("Courier", 10))
        self.status_label.pack(side=tk.RIGHT)
        
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        left_panel = tk.Frame(main_frame, bg=BG_PANEL)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        self.robot = HexRobotAvatar(left_panel)
        self.robot.pack(padx=10, pady=10)
        
        info_frame = tk.Frame(left_panel, bg=BG_PANEL)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(info_frame, text="CONNECTION", bg=BG_PANEL, 
                fg=ACCENT, font=("Courier", 10, "bold")).pack()
        
        self.conn_info = tk.Label(info_frame, 
                                 text=f"Host: {HEX_HOST}\nPort: {HEX_PORT}\nStatus: Disconnected",
                                 bg=BG_PANEL, fg=TEXT_DIM, font=("Courier", 8),
                                 justify=tk.LEFT)
        self.conn_info.pack(pady=5)
        
        btn_frame = tk.Frame(left_panel, bg=BG_PANEL)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="CONNECT", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Courier", 9, "bold"), command=self.connect_hex,
                 width=15).pack(pady=2)
        tk.Button(btn_frame, text="DISCONNECT", bg=BG_DARK, fg=WARNING,
                 font=("Courier", 9), command=self.disconnect_hex,
                 width=15).pack(pady=2)
        tk.Button(btn_frame, text="PING", bg=BG_DARK, fg=TEXT_SECONDARY,
                 font=("Courier", 9), command=self.ping_hex,
                 width=15).pack(pady=2)
        
        right_panel = tk.Frame(main_frame, bg=BG_PANEL)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.concept_stream = ConceptStream(right_panel)
        self.concept_stream.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.action_log = ActionLog(right_panel)
        self.action_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        input_frame = tk.Frame(self.root, bg=BG_DARK)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="SEND TO WSL:", bg=BG_DARK, fg=TEXT_PRIMARY,
                font=("Courier", 9, "bold")).pack(side=tk.LEFT)
        
        self.input_field = tk.Entry(input_frame, bg=BG_PANEL, fg=TEXT_PRIMARY,
                                    font=("Courier", 10), insertbackground=TEXT_PRIMARY)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_field.bind("<Return>", self.send_to_hex)
        
        tk.Button(input_frame, text="SEND", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Courier", 9, "bold"), command=self.send_to_hex).pack(side=tk.RIGHT)
    
    def connect_hex(self):
        self.log_action("SYSTEM", f"Connecting to {HEX_HOST}:{HEX_PORT}...")
        
        if self.connection.connect():
            self.status_label.config(text="● CONNECTED", fg=TEXT_PRIMARY)
            self.robot.set_state("listening")
            self.conn_info.config(text=f"Host: {HEX_HOST}\nPort: {HEX_PORT}\nStatus: Connected")
            self.log_action("SYSTEM", "Connected to WSL Hex!")
            self.concept_stream.add("Interface connected", "SYSTEM")
        else:
            self.status_label.config(text="● FAILED", fg="#ff0000")
    
    def disconnect_hex(self):
        self.connection.disconnect()
        self.status_label.config(text="● DISCONNECTED", fg=TEXT_DIM)
        self.robot.set_state("disconnected")
        self.conn_info.config(text=f"Host: {HEX_HOST}\nPort: {HEX_PORT}\nStatus: Disconnected")
        self.log_action("SYSTEM", "Disconnected")
    
    def ping_hex(self):
        if self.connection.send("ping", {"time": time.time()}):
            self.log_action("PING", "Sent")
        else:
            self.log_action("ERROR", "Not connected")
    
    def send_to_hex(self, event=None):
        text = self.input_field.get().strip()
        if not text:
            return
        
        self.input_field.delete(0, tk.END)
        
        if self.connection.send("user_input", {"text": text}):
            self.concept_stream.add(text, "USER")
        else:
            self.log_action("ERROR", "Not connected")
    
    def log_action(self, action_type, details):
        self.action_log.add(action_type, details)
    
    def process_queue(self):
        try:
            while True:
                msg_type, data = self.ui_queue.get_nowait()
                
                if msg_type == "state":
                    self.robot.set_state(data.get("state", "idle"))
                
                elif msg_type == "concept":
                    self.concept_stream.add(data.get("concepts", ""), data.get("source", "HEX"))
                
                elif msg_type == "action":
                    self.log_action(data.get("type", "ACTION"), data.get("details", ""))
                
                elif msg_type == "disconnected":
                    self.status_label.config(text="● LOST", fg="#ff0000")
                    self.robot.set_state("disconnected")
                    self.log_action("ERROR", "Connection lost")
                
                elif msg_type == "pong":
                    self.log_action("PONG", f"Latency: {data.get('latency', 0):.2f}ms")
        
        except queue.Empty:
            pass
        
        self.root.after(50, self.process_queue)
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    interface = HexInterface()
    interface.run()
