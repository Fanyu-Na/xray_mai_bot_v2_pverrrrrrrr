from nonebot.log import logger
import sys
from nonebot import get_driver
from nonebot.log import logger
from logging.handlers import TimedRotatingFileHandler
import logging
import logging.handlers
from src.libraries.GLOBAL_PATH import RUNTIME_LOG_PATH,CUSTOM_LOG_PATH

driver = get_driver()

def setup_logger(name, log_file, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30,encoding="utf-8")
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# 设置日志文件的路径
c_logger = setup_logger('c_logger', f'{CUSTOM_LOG_PATH}/c_logger.log')

@driver.on_startup
async def set_log_format():
    logger.level("DEBUG", color="<blue>", icon=f"*️⃣DDDEBUG")
    logger.level("INFO", color="<white>", icon=f"ℹ️IIIINFO")
    logger.level("SUCCESS", color="<green>", icon=f"✅SUCCESS")
    logger.level("WARNING", color="<yellow>", icon=f"⚠️WARNING")
    logger.level("ERROR", color="<red>", icon=f"⭕EEERROR")

    def default_filter(record):
        """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
        log_level = record["extra"].get("nonebot_log_level", "INFO")
        levelno = logger.level(log_level).no if isinstance(log_level, str) else log_level
        return record["level"].no >= levelno
    
    default_format: str = (
        "<c>{time:YYYY-MM-DD}</c> <blue>{time:HH:mm:ss}</blue> "
        "<lvl>[{level.icon}]</lvl> "
        "<c><{name}.{module}.{function}></c> "
        "{message}")
    """默认日志格式"""

    logger.remove()
    logger.add(
        sys.stdout,
        level=0,
        diagnose=False,
        filter=default_filter,
        format=default_format,
    )

    log_file_path = F"{RUNTIME_LOG_PATH}/xray_bot_runtime.log"

    logger.add(
    log_file_path,
    level=0,
    diagnose=False,
    filter=default_filter,
    format=default_format, 
    rotation="1 hour"
    )

    logger.success("Log配置项设置完毕")

