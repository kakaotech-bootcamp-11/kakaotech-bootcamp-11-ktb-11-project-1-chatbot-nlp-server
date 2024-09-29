#!/bin/bash

# Define API endpoint
API_ENDPOINT="http://localhost:5001/conv"

# Create an array of user inputs
declare -a user_inputs=(
    "카카오 부트캠프의 상세 주소를 알려주세요."
    "카카오 부트캠프의 교육 장소는 어디에요?"
    "카카오 클라우드 교육은 언제에요?"
    "카카오 부트캠프 교육장에 가는 대중교통을 알려주세요."

    "Chat GPT 지원내용을 알려줘"
    "GPT 구독료 청구 방법을 알려줘"
    "GPT랑 AWS 둘 다 지원가능해?"
    "인프런 강의 지원받는 방법을 알려줘"

    "사원증은 어떻게 받아?"
    "지문등록 일정을 알려줘"
    "아직 지문 등록을 안했어."

    "8월 교육 일정을 알려줘"
    "팀 미션 어떻게 진행해?"
    "최신 커리큘럼을 알려줘"
    "우리 쉬는날을 알려줘"
    "부트캠프 방학 언제야?"

    "취직을 해서 교육을 더 이상 듣지 못할 것 같아"
    "교육을 중도에 포기하면 불이익이 있어?"
    "중도포기양식은 어디서 확인할 수 있어?"
    "중도포기서 는 어디에 제출해?"
    "중도탈락하면 지원금차감이 얼마나 될까?"
    "출석률이 얼마나 되어야 수료인정이 될까?"

    "훈련장려금을 알려줘"

    "출석 조건을 알려줘"
    "지각을 6번하면 어떻게 되는거야?"
    "오전 9시 6분에 출석체크 했는데 지각이야?"
    "나 아파서 부트캠프에 못갔는데 출석인정 받고싶어"

    "휴가 신청 양식은 어디서 확인 가능해?"
    "예비군에 가야하는데 따로 제출해야하는 서류가 있을까?"
    "면접을 보러 가는데 제출해야 하는 서류가 있어?"

    "시간표를 알려줘"
    "나 풀스택 과정을 듣고 있는데 자격증 응시료 지원해주는 시험은 어떤 것들이 있어?"
    "나 인공지능 과정을 듣고 있는데 자격증 응시료 지원해주는 시험은 어떤 것들이 있어?"
    "나 클라우드 과정을 듣고 있는데 자격증 응시료 지원해주는 시험은 어떤 것들이 있어?"
    "응시만 하고 시험은 불합격 했는데 그래도 지원을 받을 수 있어?"

    "코렙도 지원을 해줘?"
    "인공지능 과정도 AWS를 지원해줘?"
    "팀 리빌딩을 한다던데 어떻게 하는지 정해졌어?"
    "동아리 활동을 하고 싶은데 규정을 알려줘"
    "동아리 신청 양식은 어디서 확인 가능해?"

    "해커톤 일정이 있어?"
    "해커톤 팀 구성은 어떻게 해야 해?"
    "해커톤 관련 정보는 어디서 확인 가능해?"
)

# Create an empty JSON file to store the results
output_file="test_results.json"
echo "{" > $output_file

# Loop through each user input and make the curl request
for i in "${!user_inputs[@]}"; do
    response=$(curl -s -X POST $API_ENDPOINT -H "Content-Type: application/json" -d "{\"content\": \"${user_inputs[$i]}\"}")
    
    # Check if the response contains "RAG response"
    if echo "$response" | grep -q "RAG response"; then
        type="RAG"
    else
        type="ELSE"
    fi

    # Remove the prefix "RAG response: " or "topic: ELSE" from the response
    cleaned_response=$(echo "$response" | sed 's/RAG response: //' | sed 's/topic: ELSE//')

    # Save the input, response, and type to the JSON file
    echo "\"${user_inputs[$i]}\": {\"response\": \"$cleaned_response\", \"type\": \"$type\"}" >> $output_file
    
    # Add a comma between results, except for the last one
    if [ $i -lt $((${#user_inputs[@]}-1)) ]; then
        echo "," >> $output_file
    fi
done

# Close the JSON object
echo "}" >> $output_file

echo "Test results saved to $output_file"
