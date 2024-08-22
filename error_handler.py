"""
에러 핸들러 정의 
"""

from flask import jsonify

def register_error_handlers(app):
    # 404 에러 핸들러 정의
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    # 400 에러 핸들러 정의
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"error": "Bad request"}), 400

    # 500 에러 핸들러 정의
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500