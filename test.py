import unittest
import json
import os
from datetime import datetime
from trash.app import app

class AppIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # JSON 파일 경로 설정
        self.user_input_file = 'test/input/user_inputs.json'
        # 출력 파일을 저장할 디렉토리 설정
        self.output_dir = 'test/output'

        # 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_full_functionality(self):
        """app.py의 모든 기능을 한 번에 테스트 (자동 분류)"""
        # JSON 파일 읽기
        with open(self.user_input_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            user_inputs = data.get('user_inputs', [])

        results = []

        for user_input in user_inputs:
            # 모든 사용자 입력을 단일 엔드포인트로 보냅니다
            response = self.app.post('/conv', 
                                     data=json.dumps({'content': user_input}),
                                     content_type='application/json')

            result = {
                'input': user_input,
                'status_code': response.status_code,
                'response_text': response.get_data(as_text=True)
            }
            results.append(result)

            # 상태 코드가 200인지 확인
            self.assertEqual(response.status_code, 200)
            # 응답 내용이 비어있지 않은지 확인
            self.assertTrue(len(result['response_text']) > 0)

        # 현재 시간 기준으로 파일명 생성
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f'test_results_{current_time}.json')

        # 결과를 JSON 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    unittest.main()

"""user_inputs = [
            "교육 중간에 탈락하면 페널티가 있어?", 
            "훈련 장려금은 얼마야?",
            "출석 확인은 어떻게 해?", 
            "카카오 클라우드 교육 채널에 어떻게 로그인해?", 
            "인프런 강의 지원은 어떻게 받을 수 있어?", 
            "사원증은 언제 배부돼?", 
            "8월 교육 일정은 어떻게 돼?", 
            "팀 미션 세부 내용은 뭐야?", 
            "ChatGPT Plus 지원 방법은 어떻게 돼?", 
            "교육 중도 포기 시 불이익이 있어?", 
            "출석 인정 기준은 무엇이야?", 
            "출석 입력요청대장은 어떻게 작성해?", 
            "Colab Pro+ 지원 내용은 뭐야?", 
            "카카오테크 부트캠프 가는 길은?", 
            "클라우드 강의 일정은 어떻게 돼?", 
            "포기 사유가 취업일 경우 어떻게 해야 해?", 
            "예비군 훈련 시 출석 인정 서류는 무엇이야?", 
            "중도포기서 제출 방법은?", 
            "방학과 토요일 수업 안내는 어떻게 돼?", 
            "교육 중도 포기 시 국민내일배움카드 사용에 불이익이 있어?"
        ]"""""