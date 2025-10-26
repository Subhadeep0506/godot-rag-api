import os
import sys
import threading
from datetime import datetime
from loguru import logger
import logfire


class LoggerService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LoggerService, cls).__new__(cls)
                    cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        logger.remove()
        try:
            logfire.configure(
                token=os.getenv("LOGFIRE_TOKEN"),
                send_to_logfire=True,
                service_name=os.getenv("LOGFIRE_SERVICE_NAME", "godot-rag-api"),
                service_version=os.getenv("LOGFIRE_SERVICE_VERSION", "1.0.0"),
                environment=os.getenv("ENVIRONMENT", "development"),
            )
            # Add Logfire handler to loguru
            logger.configure(handlers=[logfire.loguru_handler()])
        except Exception as e:
            print(f"Warning: Failed to configure Logfire: {e}")
        
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            backtrace=True,
        )

    @staticmethod
    def get_logger(name: str | None = None):
        """
        Return a loguru logger bound to an optional name.
        If name is None, returns the global logger.
        """
        return logger.bind(name=name) if name else logger

    def log_system_info(self):
        """
        Log and return basic system information as a dictionary
        """
        import platform

        system_info = {
            "logger_initialized": True,
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu_count": os.cpu_count(),
            "thread_count": threading.active_count(),
            "ram": getattr(platform, "machine", lambda: "Unknown")(),
            "used_memory": getattr(sys, "getsizeof", lambda x: "Unknown")(sys.modules),
            "disk": getattr(platform, "node", lambda: "Unknown")(),
            "disk_used": getattr(platform, "platform", lambda: "Unknown")(),
        }

        lg = self.get_logger()
        lg.info("Application Logger Initialized", extra={"system_info": system_info})

        return system_info
