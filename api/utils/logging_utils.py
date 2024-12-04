import logging
import json
from datetime import datetime
from functools import wraps
import traceback

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log detallado del error
            error_details = {
                'timestamp': datetime.now().isoformat(),
                'function': func.__name__,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
            logger.error(f"Exception details: {json.dumps(error_details, indent=2)}")
            raise
    return wrapper
