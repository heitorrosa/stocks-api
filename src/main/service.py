import sys
import os
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main.app.api import API

class Service:
    instances = {}
    
    @classmethod
    def initialize(cls, service_name: str, port: int):
        key = f"{service_name}_{port}"
        if key not in cls.instances:
            instance = API(service_name, port)
            thread = threading.Thread(target=instance.run, daemon=True)
            thread.start()
            cls.instances[key] = instance
        return cls.instances[key]