import time
import threading
import sys
import webbrowser
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import asyncio
import os
try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
except ImportError:
    tk = None

# Important: ensure project root is in path or run from root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from node_agent.agent.core import NodeAgent

class AverraWindowsApp:
    def __init__(self):
        link_key = self.get_saved_key()
        self.agent = NodeAgent(node_link_key=link_key)
        self.agent_thread = None
        self.icon = None

    def get_saved_key(self) -> str:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        key_path = os.path.join(appdata, "averra_node_link_key.txt")
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                return f.read().strip()
        return ""

    def save_key(self, key: str):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        key_path = os.path.join(appdata, "averra_node_link_key.txt")
        with open(key_path, "w") as f:
            f.write(key.strip())

    def set_node_link_key(self, icon, item_):
        if not tk:
            print("tkinter not available")
            return
        root = tk.Tk()
        root.withdraw()
        current = self.get_saved_key()
        key = simpledialog.askstring(
            "Link Your Node",
            "Enter your Node Link Key from averra.network/dashboard:",
            initialvalue=current,
            parent=root
        )
        root.destroy()
        if key and key.strip():
            self.save_key(key)
            self.agent.node_link_key = key.strip()
            messagebox.showinfo("Averra Node", "Node Link Key saved successfully.")

    def create_image(self, color1, color2):
        # Generate a simple icon based on two colors
        image = Image.new('RGB', (64, 64), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (16, 16, 48, 48),
            fill=color2)
        return image

    def start_agent(self, icon, item):
        if not self.agent.is_running:
            self.agent.is_running = True
            
            def run_agent():
                # Set up asyncio loop for the agent thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    self.agent.start()
                except Exception as e:
                    print(f"Agent stopped or crashed: {e}")
                    
            self.agent_thread = threading.Thread(target=run_agent, daemon=True)
            self.agent_thread.start()
            
            # Update menu to show it's running
            icon.notify("Averra Node has started.", "Averra Network")
            self.update_menu(icon)

    def stop_agent(self, icon, item):
        if self.agent.is_running:
            self.agent.stop()
            if self.agent_thread:
                self.agent_thread.join(timeout=3)
            icon.notify("Averra Node stopped.", "Averra Network")
            self.update_menu(icon)

    def open_dashboard(self, icon, item_):
        webbrowser.open("https://averra.network/dashboard")

    def exit_app(self, icon, item):
        self.stop_agent(icon, item)
        icon.stop()

    def update_menu(self, icon):
        # Determine dynamic titles based on state
        status_text = "Status: ONLINE 🟢" if self.agent.is_running else "Status: OFFLINE 🔴"
        wallet_text = f"Wallet: {self.agent.node_id[:8]}..." if self.agent.node_id else "Wallet: Not Connected"
        
        # We can't fetch wallet dynamically easily without polling, so keeping it simple for MVP
        
        menu = pystray.Menu(
            item(status_text, lambda: None, enabled=False),
            item(wallet_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Start Inference Node', self.start_agent, enabled=not self.agent.is_running),
            item('Stop Inference Node', self.stop_agent, enabled=self.agent.is_running),
            pystray.Menu.SEPARATOR,
            item('Set Node Link Key...', self.set_node_link_key),
            item('Open Developer Dashboard', self.open_dashboard),
            pystray.Menu.SEPARATOR,
            item('Quit Averra', self.exit_app)
        )
        icon.menu = menu

    def run(self):
        # We use a blue/cyan theme for the icon
        image = self.create_image((9, 9, 11), (56, 189, 248))
        
        self.icon = pystray.Icon("Averra Node", image, "Averra AI Compute Node")
        self.update_menu(self.icon)
        
        # icon.run() blocks the main thread and displays the system tray
        self.icon.run()

if __name__ == "__main__":
    app = AverraWindowsApp()
    app.run()
