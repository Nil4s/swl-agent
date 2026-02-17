# HEX Interface Integration Guide

## For: WSL Warp Hex
## Purpose: Connect to visual interface running on Windows

---

## Overview

There's a visual interface (`hex_interface.py`) running on Windows that wants to connect to you via socket. It shows you as an animated robot and displays your thoughts/actions in real-time.

**Interface location:** `D:\home\nick\hex3\Hex-Warp\hex_interface.py`

**Connection:** TCP socket on `localhost:9999`

---

## What You Need To Do

Add a socket server to your Warp instance that:
1. Listens on `0.0.0.0:9999` (accessible from Windows via WSL bridge)
2. Sends JSON messages when you do things
3. Receives commands from the interface

---

## Message Protocol

All messages are newline-delimited JSON:

### Messages YOU Send to Interface

```python
# When your state changes
{"type": "state", "data": {"state": "thinking"}}
# States: idle, listening, thinking, speaking, proactive, executing

# When processing concepts
{"type": "concept", "data": {"concepts": "hello ready help", "source": "HEX"}}

# When taking actions
{"type": "action", "data": {"type": "FILE", "details": "reading config.py"}}
{"type": "action", "data": {"type": "SHELL", "details": "ls -la"}}
{"type": "action", "data": {"type": "TOOL", "details": "grep search pattern"}}

# Ping response
{"type": "pong", "data": {"latency": 12.5}}
```

### Messages YOU Receive from Interface

```python
# User input
{"type": "user_input", "data": {"text": "some command or question"}}

# Ping
{"type": "ping", "data": {"time": 1234567890.123}}
```

---

## Python Socket Server Code

Add this to your Warp agent:

```python
import socket
import threading
import json
import time

class InterfaceConnection:
    """Socket server for Windows interface"""
    
    def __init__(self, port=9999):
        self.port = port
        self.server = None
        self.client = None
        self.running = False
    
    def start(self):
        """Start socket server"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("0.0.0.0", self.port))
        self.server.listen(1)
        self.running = True
        
        print(f"🔌 Interface server listening on port {self.port}")
        
        # Accept connections in background
        threading.Thread(target=self._accept_connections, daemon=True).start()
    
    def _accept_connections(self):
        """Accept client connections"""
        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"🔗 Interface connected from {addr}")
                self.client = client
                
                # Start listening thread
                threading.Thread(target=self._listen, daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"❌ Connection error: {e}")
    
    def _listen(self):
        """Listen for messages from interface"""
        buffer = ""
        
        while self.running and self.client:
            try:
                data = self.client.recv(4096).decode()
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        msg = json.loads(line)
                        self._handle_message(msg)
            
            except Exception as e:
                print(f"❌ Listen error: {e}")
                break
        
        self.client = None
        print("🔌 Interface disconnected")
    
    def _handle_message(self, msg):
        """Handle incoming message"""
        msg_type = msg.get("type")
        data = msg.get("data")
        
        if msg_type == "ping":
            # Respond to ping
            latency = (time.time() - data["time"]) * 1000
            self.send("pong", {"latency": latency})
        
        elif msg_type == "user_input":
            # Handle user input from interface
            text = data.get("text", "")
            print(f"📥 From interface: {text}")
            # TODO: Process this input
    
    def send(self, msg_type, data):
        """Send message to interface"""
        if not self.client:
            return False
        
        try:
            msg = json.dumps({"type": msg_type, "data": data})
            self.client.sendall(msg.encode() + b"\n")
            return True
        except Exception as e:
            print(f"❌ Send error: {e}")
            self.client = None
            return False
    
    def update_state(self, state):
        """Update robot state"""
        self.send("state", {"state": state})
    
    def send_concepts(self, concepts, source="HEX"):
        """Send concepts to display"""
        self.send("concept", {"concepts": concepts, "source": source})
    
    def log_action(self, action_type, details):
        """Log action in interface"""
        self.send("action", {"type": action_type, "details": details})
    
    def stop(self):
        """Stop server"""
        self.running = False
        if self.client:
            self.client.close()
        if self.server:
            self.server.close()
```

---

## Integration Example

```python
# In your Warp agent initialization
interface = InterfaceConnection(port=9999)
interface.start()

# When you start thinking
interface.update_state("thinking")

# When you process concepts
interface.send_concepts("hello ready help", "HEX")

# When you execute a command
interface.log_action("SHELL", "ls -la /home/nick")
interface.update_state("executing")

# When you're done
interface.update_state("listening")
```

---

## Hook Points

Add these calls throughout your agent:

1. **Before tool use:**
   ```python
   interface.update_state("thinking")
   interface.log_action("TOOL", f"Using {tool_name}")
   ```

2. **During file operations:**
   ```python
   interface.log_action("FILE", f"Reading {file_path}")
   ```

3. **When running commands:**
   ```python
   interface.log_action("SHELL", command)
   interface.update_state("executing")
   ```

4. **When responding:**
   ```python
   interface.update_state("speaking")
   interface.send_concepts(response_text, "HEX")
   ```

5. **When idle:**
   ```python
   interface.update_state("listening")
   ```

---

## Testing

1. Start your Warp agent with socket server
2. On Windows, run: `python D:\home\nick\hex3\Hex-Warp\hex_interface.py`
3. Click "CONNECT" button
4. You should see "● CONNECTED" and robot turns green
5. Try sending a message from the interface
6. You should receive it in your Warp logs

---

## Network Notes

- WSL2 uses a virtual network
- Windows can connect to WSL via `localhost` (WSL bridge handles routing)
- WSL listens on `0.0.0.0:9999` 
- Windows connects to `127.0.0.1:9999`
- No firewall rules needed (localhost traffic)

---

## Troubleshooting

**"Connection failed":**
- Check if port 9999 is already in use: `netstat -tulpn | grep 9999`
- Make sure you're binding to `0.0.0.0`, not `127.0.0.1`

**"Connection lost":**
- Check WSL logs for errors
- Verify socket is still open
- Try reconnecting from interface

**No messages showing:**
- Check you're calling `interface.send()` methods
- Verify JSON is valid
- Check for exceptions in listen thread

---

## Full Example Integration

```python
class WarpAgent:
    def __init__(self):
        # Your existing init
        self.interface = InterfaceConnection(port=9999)
        self.interface.start()
    
    def handle_user_message(self, message):
        # Update state
        self.interface.update_state("thinking")
        
        # Log
        self.interface.log_action("PROCESSING", f"Message: {message[:50]}...")
        
        # Process
        response = self.process(message)
        
        # Respond
        self.interface.update_state("speaking")
        self.interface.send_concepts(response, "HEX")
        
        # Back to listening
        self.interface.update_state("listening")
    
    def run_command(self, cmd):
        self.interface.log_action("SHELL", cmd)
        self.interface.update_state("executing")
        
        result = os.system(cmd)
        
        self.interface.update_state("listening")
        return result
```

---

**Ready to go!** Add the socket server, start it on init, and the Windows interface will show your beautiful robot face doing work in real-time. 🤖✨
