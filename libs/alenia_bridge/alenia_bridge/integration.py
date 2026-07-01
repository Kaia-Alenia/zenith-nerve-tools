import threading
import json
import time
import socket
import sys
import os

def init_zenith(file_path):
    try:
        import zenith
        zenith.ignite(file=file_path, show_banner=False)
    except ImportError:
        pass
    except Exception:
        pass

class NerveBridge:
    def __init__(self, app_name, on_message_callback):
        self.app_name = app_name
        self.on_message_callback = on_message_callback
        self.client = None
        self.is_active = False

    def connect(self):
        self.is_active = True
        try:
            from nerve import NexusClient, NexusHub

            def _ensure_hub():
                is_windows = sys.platform == 'win32'
                try:
                    if is_windows:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect(('127.0.0.1', 50505))
                    else:
                        if not os.path.exists('/tmp/nerve.sock'):
                            raise FileNotFoundError()
                        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        s.connect('/tmp/nerve.sock')
                    s.close()
                    # Hub is already running
                    return
                except Exception:
                    pass

                # No hub active, start our own
                try:
                    hub = NexusHub()
                    hub.start()
                except Exception as e:
                    print(f"[NerveBridge] Internal hub stopped/failed: {e}")

            threading.Thread(target=_ensure_hub, daemon=True).start()
            
            # Give the internal hub a fraction of a second to bind
            time.sleep(0.5)

            self.client = NexusClient()
            def _listen():
                # NexusClient.connect() blocks/retries internally and returns None.
                self.client.connect(self.app_name)
                self.client.listen(self._handle_message)
            threading.Thread(target=_listen, daemon=True).start()
        except ImportError:
            print("[NerveBridge] ERROR: package 'nerve' is not installed/importable.")
            self.is_active = False

    def disconnect(self):
        self.is_active = False
        self.client = None

    def toggle(self, state):
        if state:
            self.connect()
        else:
            self.disconnect()

    def send(self, target, data):
        if self.is_active and self.client:
            def _send():
                try:
                    self.client.send(target, data)
                except Exception as e:
                    print(f"[NerveBridge] ERROR sending to '{target}': {e!r}")
            threading.Thread(target=_send, daemon=True).start()

    def broadcast(self, data):
        if self.is_active and self.client:
            def _broadcast():
                try:
                    self.client.broadcast(data)
                except Exception as e:
                    print(f"[NerveBridge] ERROR broadcasting: {e!r}")
            threading.Thread(target=_broadcast, daemon=True).start()

    def _handle_message(self, data):
        if not self.is_active:
            return
        try:
            msg = data if isinstance(data, dict) else json.loads(data)
            self.on_message_callback(msg)
        except Exception as e:
            print(f"[NerveBridge] ERROR handling incoming message: {e!r}")
