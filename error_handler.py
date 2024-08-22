"""
에러 핸들러 정의 
"""

from flask import jsonify, make_response
import logging
# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': "Resource not found",  'code': 404, "description": f"{error.description}"})

    # 400 에러 핸들러 정의
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({'error': "Bad request",  'code': 400, "description": f"{error.description}"})


    # 500 에러 핸들러 정의
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': "Internal server error",  'code': 500, "description": f"{error.description}"})
