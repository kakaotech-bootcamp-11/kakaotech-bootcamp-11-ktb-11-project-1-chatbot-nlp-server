import logging
import traceback
import sys

class CustomFormatter(logging.Formatter):
    def formatException(self, exc_info):
        """예외 정보를 포맷합니다."""
        tb_str = traceback.format_exception(*exc_info)
        return ''.join(tb_str).strip()  # 포맷을 깔끔하게 정리합니다.
    
    def format(self, record):
        """로그 메시지 포맷을 정의합니다."""
        # 기본 로그 메시지
        log_message = super().format(record)
        
        # 예외 메시지와 커스텀 메시지 생성
        exception_message = f"{{{record.exc_info[1]}}}" if record.exc_info else ''
        custom_message = f"{{나의 커스텀 로그}} - {exception_message}".strip()
        
        # 포맷 조정
        return (f"{record.asctime} {record.levelname} - {record.pathname} > line {record.lineno} "
                f"in {record.funcName}() \n{custom_message}\n{record.msg}")

def setup_custom_logger(name):
    """커스텀 로거를 설정합니다."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler('error.log')
    file_handler.setLevel(logging.ERROR)
    
    # 포맷터 설정
    formatter = CustomFormatter('%(asctime)s %(levelname)s - %(pathname)s > line %(lineno)d in %(funcName)s() \n%(message)s')
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    
    return logger
