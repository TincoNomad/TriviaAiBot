import logging
from logging.handlers import RotatingFileHandler
import os

def setup_bot_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    os.makedirs('logs/bot', exist_ok=True)
    
    handler = RotatingFileHandler(
        f'logs/bot/{log_file}',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Loggers específicos para el bot
bot_logger = setup_bot_logger('discord_bot', 'bot.log')
command_logger = setup_bot_logger('bot_commands', 'commands.log')
game_logger = setup_bot_logger('game_interactions', 'game.log')
