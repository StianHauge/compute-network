import os
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
import logging
import threading
from multiprocessing.connection import Listener, Client

logger = logging.getLogger("AverraIPC")
IPC_SOCKET_PATH = "/tmp/averra_ipc/vram_socket"

class IPCProvider:
    """Runs in the OLD container (v1.1) to serve its VRAM to the NEW container."""
    def __init__(self):
        self.tensors = {}
        # Ensure path exists and remove stale socket
        os.makedirs(os.path.dirname(IPC_SOCKET_PATH), exist_ok=True)
        if os.path.exists(IPC_SOCKET_PATH):
            try:
                os.remove(IPC_SOCKET_PATH)
            except OSError:
                pass
            
        self.listener = Listener(IPC_SOCKET_PATH, family='AF_UNIX')
        logger.info(f"IPC Provider listening for Superposition requests on {IPC_SOCKET_PATH}")

    def register_tensor(self, name: str, tensor: 'torch.Tensor'):
        # share_memory_() transitions CPU tensors to shared memory FDs, 
        # and prepares CUDA tensors for CUDA IPC handled generation.
        if HAS_TORCH:
            tensor.share_memory_()
        self.tensors[name] = tensor
        logger.info(f"Registered shared tensor '{name}' for Inference Superposition.")

    def _serve_loop(self):
        while True:
            try:
                conn = self.listener.accept()
                logger.info("IPC Consumer connected! Initiating VRAM Superposition Transfer...")
                # PyTorch custom reduction automatically sends FDs or CUDA IPC Handles via the pipe!
                conn.send(self.tensors)
                
                ack = conn.recv()
                if ack == "ACK":
                    logger.info("Consumer acknowledged VRAM Superposition successfully.")
            except Exception as e:
                logger.error(f"IPC Server Error: {e}")
            finally:
                if 'conn' in locals(): conn.close()
                

    def start(self):
        t = threading.Thread(target=self._serve_loop, daemon=True)
        t.start()


class IPCConsumer:
    """Runs in the NEW container (v1.2) to steal VRAM from the old without disk overhead."""
    @staticmethod
    def fetch_shared_tensors():
        if not os.path.exists(IPC_SOCKET_PATH):
            logger.info("No IPC Socket found. Booting via Cold Start (Loading from Disk).")
            return None
            
        logger.info(f"IPC Socket '{IPC_SOCKET_PATH}' found! Attempting VRAM Superposition...")
        try:
            conn = Client(IPC_SOCKET_PATH, family='AF_UNIX')
            # Receives the dict of tensors, magically reconstructed by PyTorch 
            # using cudaIpcOpenMemHandle in the background!
            tensors = conn.recv()
            conn.send("ACK")
            conn.close()
            logger.info(f"SUCCESS! Inherited {len(tensors)} tensors directly from VRAM! ZERO-DOWNTIME achieved.")
            return tensors
        except Exception as e:
            logger.warning(f"Failed to inherit from IPC (Falling back to cold boot): {e}")
            return None
