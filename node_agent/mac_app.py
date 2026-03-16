import rumps
import threading
import requests
import webbrowser
import sys
import os

# Ensure the parent directory is in the path so we can import agent logic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from node_agent.agent.core import NodeAgent, CONTROL_PLANE_URL, NODE_AUTH_TOKEN

class AverraNodeApp(rumps.App):
    def __init__(self):
        super(AverraNodeApp, self).__init__("Averra Node", icon=None)
        self.title = "⚡️"
        
        self.is_running = False
        self.agent = None
        self.agent_thread = None
        
        self.status_button = rumps.MenuItem(title="Start Node", callback=self.toggle_node)
        self.wallet_menu = rumps.MenuItem(title="Wallet Balance: $0.00")
        self.models_menu = rumps.MenuItem(title="Cached Models: 0")
        
        self.menu = [
            self.status_button,
            None,
            self.wallet_menu,
            self.models_menu,
            None,
            rumps.MenuItem(title="Set Node Link Key...", callback=self.set_node_link_key),
            rumps.MenuItem(title="View Local Dashboard", callback=self.open_dashboard)
        ]

    def get_saved_key(self):
        key_path = os.path.expanduser("~/.averra_node_link_key")
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                return f.read().strip()
        return ""

    def save_key(self, key):
        key_path = os.path.expanduser("~/.averra_node_link_key")
        with open(key_path, "w") as f:
            f.write(key.strip())

    def set_node_link_key(self, sender):
        current_key = self.get_saved_key()
        response = rumps.Window(
            message="Enter your Node Link Key from the Developer Dashboard:",
            title="Authenticate Node",
            default_text=current_key,
            dimensions=(300, 24)
        ).run()
        if response.clicked:
            self.save_key(response.text)
            rumps.notification(title="Averra Node", subtitle="Key Saved", message="Node Link Key has been updated.")

    @rumps.timer(5)
    def refresh_stats(self, sender):
        if self.is_running and self.agent and self.agent.node_id:
            try:
                headers = {}
                if NODE_AUTH_TOKEN:
                    headers["Authorization"] = f"Bearer {NODE_AUTH_TOKEN}"
                resp = requests.get(f"{CONTROL_PLANE_URL}/nodes/{self.agent.node_id}/wallet", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    balance = data.get("withdrawable_balance", 0.0) + data.get("pending_rewards", 0.0)
                    self.wallet_menu.title = f"Wallet Balance: ${balance:.2f}"
                    
                self.models_menu.title = f"Cached Models: {len(self.agent.cached_models)}"
            except Exception as e:
                pass # Control plane might be down

    def toggle_node(self, sender):
        if not self.is_running:
            self.is_running = True
            sender.title = "Stop Node"
            self.title = "⚡️(Running)"
            
            # Start Node in background thread
            link_key = self.get_saved_key()
            if not link_key:
                rumps.notification("Averra", "Missing Link Key", "Running as an anonymous community node. Set Key to link to your dashboard.")
                
            self.agent = NodeAgent(node_link_key=link_key)
            self.agent_thread = threading.Thread(target=self.agent.run, daemon=True)
            self.agent_thread.start()
            rumps.notification(title="Averra Node", subtitle="Node Started", message="GPU connected to the inference fabric.")
        else:
            self.is_running = False
            sender.title = "Start Node"
            self.title = "⚡️"
            
            if self.agent:
                self.agent.stop()
                self.agent = None
                
            self.wallet_menu.title = "Wallet Balance: $0.00"
            rumps.notification(title="Averra Node", subtitle="Node Stopped", message="Disconnected from the network.")

    def open_dashboard(self, _):
        webbrowser.open("http://127.0.0.1:8080")

if __name__ == "__main__":
    app = AverraNodeApp()
    app.run()
