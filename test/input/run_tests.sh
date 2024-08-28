#!/bin/bash

# Define API endpoint
API_ENDPOINT="http://localhost:5001/conv"

# Create an array of user inputs
declare -a user_inputs=(
    "카카오 부트캠프의 상세 주소를 알려주세요."
    "카카오 부트캠프에 주차 지원이 되나요?"
    "카카오 부트캠프에서 제공되는 교육 내용은 무엇인가요?"
    "카카오 부트캠프에서 출석 인정 기준은 무엇인가요?"
    "카카오 부트캠프의 교육 시간표를 알고 싶어요."
    "인프런 강의 신청 방법을 알려주세요."
    "인프런 크레딧 지원에 대해 설명해주세요."
    "인프런 강의 수강 시 할인 혜택이 있나요?"
    "인프런 강의 신청 기간은 언제인가요?"
    "인프런 강의 신청에 제한이 있나요?"
    "클라우드 과정 자격증 지원 내용은 무엇인가요?"
    "응시료 지원을 위한 제출 서류는 무엇인가요?"
    "자격증 응시료 지원 신청 방법을 알려주세요."
    "응시료 지원 대상 자격증 목록을 알려주세요."
    "응시료 지원 신청 기한은 언제인가요?"
    "사원증 배부 일정이 어떻게 되나요?"
    "사원증 배부 장소는 어디인가요?"
    "사원증으로 출입이 가능한 시점은 언제인가요?"
)

# Create an empty JSON file to store the results
output_file="test_results.json"
echo "{" > $output_file

# Loop through each user input and make the curl request
for i in "${!user_inputs[@]}"; do
    response=$(curl -s -X POST $API_ENDPOINT -H "Content-Type: application/json" -d "{\"content\": \"${user_inputs[$i]}\"}")
    echo "\"${user_inputs[$i]}\": \"$response\"" >> $output_file
    
    # Add a comma between results, except for the last one
    if [ $i -lt $((${#user_inputs[@]}-1)) ]; then
        echo "," >> $output_file
    fi
done

# Close the JSON object
echo "}" >> $output_file

echo "Test results saved to $output_file"
