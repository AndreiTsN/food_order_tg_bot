import logging
import os

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

# INFO handler
info_handler = logging.FileHandler(f"{LOGS_DIR}/info.log", encoding="utf-8")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# ERROR handler
error_handler = logging.FileHandler(f"{LOGS_DIR}/error.log", encoding="utf-8")
error_handler.setLevel(logging.WARNING)
error_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Apply configuration globally to the entire application
# All loggers (e.g., logging.getLogger(name)) will use this configuration
logging.basicConfig(
    level=logging.INFO,
    handlers=[info_handler, error_handler, console_handler]
)
