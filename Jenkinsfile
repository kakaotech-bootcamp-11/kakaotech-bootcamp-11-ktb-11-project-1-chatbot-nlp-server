pipeline {
    agent none
    environment {
        DOCKER_REPO = "ktb11chatbot/ktb-11-project-1-chatbot-nlp"
        GIT_BRANCH = 'main'  // 빌드할 Git 브랜치
        JENKINS_NAMESPACE = 'devops-tools'  // kaniko로 build 할때 사용할 네임스페이스 보통 jenkins와 같은 namespace에서 함
        KANIKO_POD_YAML = '/var/jenkins_home/kaniko/nlp-kaniko-ci.yaml' // Kaniko Pod YAML 파일 경로 name 수정할것
        // KANIKO_POD_YAML NFS.dir path 생성후에 그 안에 Kaniko-ci.yaml을 넣어줘야 함
        KANIKO_POD_NAME = 'kaniko-nlp'
        DEPLOYMENT_NAMESPCE = 'ktb-chatbot'
        DEPLOYMENT_NAME = 'nlp-deployment'
        DEPLOYMENT_CONTAINER_NAME = 'nlp'
    }
    stages {
        stage('Checkout Source Code') {
            agent any
            steps {
                // Git 소스 코드를 체크아웃
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Current Git Commit Short: ${env.GIT_COMMIT_SHORT}" // Git 커밋 ID 앞 7자리를 tag로 쓸 예정
                }
            }
        }
        stage('Update Kaniko YAML') {
            agent { label '' }
                    steps {
                        script {
                            // 이미지 태그를 생성하고, kaniko-ci.yaml 파일에서 build해서 push registry value 덮어쓰기 tag 포함
                            sh """
                            sed -i 's|--destination=.*|--destination=docker.io/${DOCKER_REPO}:${GIT_COMMIT_SHORT}",|' ${KANIKO_POD_YAML}
                            """
                        }
                    }
                }
        stage('Deploy Kaniko Pod') {
            agent { label '' }
                    steps {
                        script {
                            // 동적으로 수정된 Kaniko Pod YAML 파일을 Kubernetes에 적용
                            sh """
                            kubectl create -f ${KANIKO_POD_YAML} -n ${JENKINS_NAMESPACE}
                            """
                        }
                    }
                }
        stage('Deploy to Kubernetes') {
            agent { label '' }
            steps {
                script {
                    //6분 대기
                    for (int i = 6; i > 0; i--) {
                                    echo "남은 대기 시간: ${i}분"
                                    sleep time: 1, unit: 'MINUTES'
                                }
                    // Kubernetes set image로 배포
                    sh """
                    kubectl set image deployment/${DEPLOYMENT_NAME} \
                    -n ${DEPLOYMENT_NAMESPCE} ${DEPLOYMENT_CONTAINER_NAME}=docker.io/${DOCKER_REPO}:${GIT_COMMIT_SHORT}
                    kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${DEPLOYMENT_NAMESPCE}
                    """
                }
            }
        }
    }
    post {
            success {
                echo 'Build and push successful!'
                withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                        discordSend description: """
                        제목 : ${currentBuild.displayName}
                        결과 : ${currentBuild.result}
                        실행 시간 : ${currentBuild.duration / 1000}s
                        로그 : ${kanikolog.take(1500)} //1500자 이내로 kaniko build 한 로그 기록 출려하도록 함
                        """,
                        link: env.BUILD_URL, result: currentBuild.currentResult,
                        title: "${env.JOB_NAME} : ${currentBuild.displayName} 성공",
                        webhookURL: "$DISCORD"
                        }
//                 agent { label '' }
                script {
                        // Kaniko Pod 삭제
                    sh """
                    kubectl delete -f ${KANIKO_POD_YAML} -n ${JENKINS_NAMESPACE}
                    """
                }
            }
            failure {
                echo 'Build or deployment failed. Check logs for details.'
                withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                    discordSend description: """
                    제목 : ${currentBuild.displayName}
                    결과 : ${currentBuild.result}
                    실행 시간 : ${currentBuild.duration / 1000}s
                    로그 : ${kanikolog.take(1500)} //1500자 이내로 kaniko build 한 로그 기록 출려하도록 함
                    """,
                    link: env.BUILD_URL, result: currentBuild.currentResult,
                    title: "${env.JOB_NAME} : ${currentBuild.displayName} 실패",
                    webhookURL: "$DISCORD"
                    }
//                 agent { label '' }
                script {
                 // Kaniko Pod의 로그 확인
                sh """
                kubectl logs ${KANIKO_POD_NAME} -n ${JENKINS_NAMESPACE}
                kubectl delete -f ${KANIKO_POD_YAML} -n ${JENKINS_NAMESPACE}
                """
            }//script
        }//failure
    }//post
}//pipeline
