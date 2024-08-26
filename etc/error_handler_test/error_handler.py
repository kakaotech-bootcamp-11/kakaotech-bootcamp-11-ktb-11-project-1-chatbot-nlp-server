"""
에러 핸들러 정의 
"""

from flask import jsonify
import openai
from openai import OpenAIError
import logging
# 로깅 설정
logging.basicConfig(
    filename='./logging/error_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

#app = Flask(__name__)

# open ai API 를 정의함 
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': "Resource not found",
            'code': 404,
            'description': getattr(error, 'description', 'Not Found') 
        }), 404
    
    @app.errorhandler(TypeError)
    def handle_type_error(error):
        return jsonify({
            'error': "TypeError",
            'code': 400,
            'description': getattr(error, 'description', 'Not Found') 
        }), 400

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': "Bad request",
            'code': 400,
            'description': getattr(error, 'description', 'Bad Request')
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        print("internal_error, error code : 500")
        print('error:', error) # error: "500 Internal Server Error: The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."
        return jsonify({
            'error': "Internal server error",
            'code': 500,
            'description': getattr(error, 'description', 'Internal Server Error')
        }), 500
    @app.errorhandler(OpenAIError)
    def handle_openai_error(e):
        if isinstance(e, openai.BadRequestError):
            return jsonify({
                'error': "BadRequestError", # 에러 종류
                'code': 400, # 에러 코드 
                'description': f"죄송해요. 시스템 오류가 발생했어요. 잠시 후 다시 시도해주세요.", # 사용자에게 전달할 에러 메시지 
                'error_message': str(e) # 오리지널 에러 메세지 e.g error code: 400 - {'error': {'message': \"Invalid type for 'messages': expected an array of objects, but got an integer instead.\", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'invalid_type'}}",
            })
        elif isinstance(e, openai.AuthenticationError):
            return jsonify({
                'error': "AuthenticationError",
                'code': 401,
                'description': "OpenAI 인증에 실패했습니다. 관리자에게 API 키를 확인을 요청해주세요.",
                'error_message': str(e)
            })
        elif isinstance(e, openai.PermissionDeniedError):
            return jsonify({
                'error': "PermissionDeniedError",
                'code': 403,
                'description': "OpenAI API가 지원되지 않는 국가에서 API를 요청하고 있습니다. 죄송해요, 서비스 이용이 불가해요.",
                'error_message': str(e)
            })
        elif isinstance(e, openai.NotFoundError):
            return jsonify({
                'error': "NotFoundError",
                'code': 404,
                'description': "OpenAI API에서 요청하려는 자원이 없습니다. 관리자에게 연락해주세요. ",
                'error_message': str(e)
            })
        elif isinstance(e, openai.UnprocessableEntityError):
            return jsonify({
                'error': "UnprocessableEntityError",
                'code': 422,
                'description': "죄송해요 시스템 오류가 발생했어요. 관리자에게 연락해주세요 (OpenAI API- 리퀘스트하려는 엔티티가 없음 오류).",
                'error_message': str(e)
            })
        elif isinstance(e, openai.RateLimitError):
            return jsonify({
                'error': "Rate limit exceeded",
                'code': 429,
                'description': "OpenAI API 요청을 너무 많이 했거나, 요금이 부족합니다. 잠시 후 다시 시도하거나 관리자에게 연락해주세요.",
                'error_message': str(e)
            })
        elif isinstance(e, openai.InternalServerError):
            return jsonify({
                'error': "API connection failed",
                'code': 500,
                'description': "내부 서버 에러로 OpenAI API 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
                'error_message': str(e)
            })
        #elif isinstance(e, openai.APIConnectionError):
        #    return {
        #        'error': "API connection failed",
        #        'code': None,
        #        'description': "엔진 트래픽 과부하로 API 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
        #    }
        
        else:
            return jsonify({
                'error': "Unknown error",
                'code': None,
                'description': f"OpenAI API 서버 관련하여 기타 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                'error_message': str(e)
            })

    
        




    