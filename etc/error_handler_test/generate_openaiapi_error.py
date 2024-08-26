import openai

class OpenAIErrorSimulator:
    def __init__(self, api_key):
        self.client = openai
        self.client.api_key = api_key

    def trigger_bad_request_error(self):  # 400
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=123,  # 잘못된 형식의 messages
                max_tokens=5
            )
        except openai.BadRequestError as e:
            raise e

    def trigger_authentication_error(self):  # 401
        try:
            invalid_client = openai
            invalid_client.api_key = "sk-invalidkey"  # 잘못된 API 키
            response = invalid_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, world"}],
                max_tokens=5
            )
        except openai.AuthenticationError as e:
            raise e

    def trigger_permission_denied_error(self):  # 403 에러 테스트 하기 어려움 
        pass
        """try:
            response = self.client.chat.completions.create(
                model="davinci-codex",  # 사용 권한이 없는 모델
                messages=[{"role": "user", "content": "Hello, world"}],
                max_tokens=5
            )
        except openai.PermissionDeniedError as e:
            raise e"""

    def trigger_not_found_error(self):  # 404 
        try:
            response = self.client.chat.completions.create(
                model="davinci-codex",  # 사용 권한이 없는 모델
                messages=[{"role": "user", "content": "Hello, world"}],
                max_tokens=5
            )
        except openai.PermissionDeniedError as e:
            raise e
        """try:
            response = self.client.Engine.retrieve("nonexistent-engine")  # 존재하지 않는 엔진 호출
        except openai.NotFoundError as e:
            raise e"""

    def trigger_unprocessable_entity_error(self):  # 422
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, world"}],
                min_tokens= 1  # 잘못된 max_tokens 설정
            )
        except openai.UnprocessableEntityError as e:
            raise e
        except Exception as e:
            print('error', e)
            raise e
    def trigger_type_error(self):  # 400
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, world"}],
                min_tokens= 1  # 잘못된 max_tokens 설정
            )
        except TypeError as e:
            raise e

    """def trigger_rate_limit_error(self):  # 429 테스트 안됨 ㅠ
        try:
            for _ in range(100):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello, world"}],
                    max_tokens=5
                )
        except openai.RateLimitError as e:
            raise e"""

    def trigger_internal_server_error(self):  # 500
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, world"}],
                max_tokens=1000000  # 매우 높은 max_tokens 설정
            )
        except openai.InternalServerError as e:
            raise e
    def trigger_etc_error(self):  # 500
        raise openai.APIError
    
