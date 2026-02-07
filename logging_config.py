import logging
import sys
from colorama import init

# Инициализируем colorama для Windows
init()

class ColoredFormatter(logging.Formatter):
    """Кастомный форматтер для цветного вывода логов"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__()
        self.fmt = fmt or "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
        self.datefmt = datefmt
        self.formatters = {}
        
        for level in self.COLORS:
            if level != 'RESET':
                colored_fmt = self.COLORS[level] + self.fmt + self.COLORS['RESET']
                self.formatters[level] = logging.Formatter(colored_fmt, datefmt=datefmt)

    def format(self, record):
        formatter = self.formatters.get(record.levelname)
        if formatter:
            return formatter.format(record)
        else:
            return super().format(record)


def setup_logging():
    """Функция для настройки логирования с цветами"""
    logging.basicConfig(level=logging.INFO, handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ])

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(ColoredFormatter())

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)