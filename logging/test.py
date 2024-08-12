from logger_config import setup_custom_logger
import sys

logger = setup_custom_logger(__name__)

def divide(a, b):
    try:
        return a / b
    except Exception as e:
        logger.error("Exception occurred", exc_info=sys.exc_info())
        raise

def main():
    try:
        divide(1, 0)
    except Exception as e:
        logger.error("Unhandled exception occurred", exc_info=sys.exc_info())

if __name__ == "__main__":
    main()