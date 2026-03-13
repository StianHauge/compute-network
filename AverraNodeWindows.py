import time
import threading
import sys
import webbrowser
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import asyncio
import os

# Important: ensure project root is in path or run from root
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from node_agent.agent.core import NodeAgent

class AverraWindowsApp:
    def __init__(self):
        self.agent = NodeAgent()
        self.agent_thread = None
        self.icon = None

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

    def open_dashboard(self, icon, item):
        webbrowser.open("http://127.0.0.1:8080")

    def open_network_explorer(self, icon, item):
        # In MVP, our web portal runs locally on 5173
        webbrowser.open("http://localhost:5173/explorer")

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
            item('Open Local Dashboard', self.open_dashboard),
            item('View Network Explorer', self.open_network_explorer),
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
