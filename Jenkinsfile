pipeline {
    agent any
    environment {
        DOCKER_REPO = "ktb11chatbot/ktb-11-project-1-chatbot-nlp"
        GIT_BRANCH = 'main'  // 빌드할 Git 브랜치
        JENKINS_NAMESPACE = 'devops-tools'  // Kaniko 빌드를 위한 네임스페이스
        KANIKO_POD_YAML = '/var/jenkins_home/kaniko/nlp-kaniko-ci.yaml' // Kaniko Pod YAML 파일 경로
        KANIKO_POD_NAME = 'kaniko-nlp'
        DEPLOYMENT_NAMESPACE = 'ktb-chatbot'
        DEPLOYMENT_NAME = 'nlp-deployment'
        DEPLOYMENT_CONTAINER_NAME = 'nlp'
    }
    stages {
        stage('Checkout Source Code') {
            steps {
                // Git 소스 코드 체크아웃
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Current Git Commit Short: ${env.GIT_COMMIT_SHORT}" // Git 커밋 ID의 앞 7자를 태그로 사용
                }
            }
        }
        stage('Update Kaniko YAML') {
            steps {
                script {
                    // Kaniko YAML 파일에서 이미지 태그 업데이트
                    sh """
                    sed -i 's|--destination=.*|--destination=docker.io/${DOCKER_REPO}:${GIT_COMMIT_SHORT}",|' ${KANIKO_POD_YAML}
                    """
                }
            }
        }
        stage('Deploy Kaniko Pod') {
            steps {
                script {
                    // 기존 Kaniko Pod 삭제 후 새로운 Kaniko Pod 배포
                    sh """
                    kubectl delete pod ${KANIKO_POD_NAME} -n ${JENKINS_NAMESPACE} --ignore-not-found
                    kubectl create -f ${KANIKO_POD_YAML} -n ${JENKINS_NAMESPACE}
                    """
                }
            }
        }
        stage('Wait for Kaniko Build') {
            steps {
                script {
                    // Kaniko Pod가 완료될 때까지 대기
                    timeout(time: 15, unit: 'MINUTES') {
                        waitUntil {
                            def status = sh(script: "kubectl get pod ${KANIKO_POD_NAME} -n ${JENKINS_NAMESPACE} -o jsonpath='{.status.phase}'", returnStdout: true).trim()
                            echo "Kaniko Pod Status: ${status}"
                            return (status == 'Succeeded') || (status == 'Failed')
                        }
                    }
                    // 최종 상태 확인
                    def finalStatus = sh(script: "kubectl get pod ${KANIKO_POD_NAME} -n ${JENKINS_NAMESPACE} -o jsonpath='{.status.phase}'", returnStdout: true).trim()
                    if (finalStatus != 'Succeeded') {
                        error "Kaniko build failed with status: ${finalStatus}"
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Kubernetes에 이미지 배포
                    sh """
                    kubectl set image deployment/${DEPLOYMENT_NAME} \
                    -n ${DEPLOYMENT_NAMESPACE} ${DEPLOYMENT_CONTAINER_NAME}=docker.io/${DOCKER_REPO}:${GIT_COMMIT_SHORT}
                    kubectl rollout status deployment/${DEPLOYMENT_NAME} -n ${DEPLOYMENT_NAMESPACE}
                    """
                }
            }
        }
    }
   post {
           success {
               echo 'Build and push successful!'
               withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                   discordSend title: "${env.JOB_NAME} : ${env.GIT_COMMIT_SHORT}",
                               description: "Build #${env.BUILD_NUMBER} 성공 ✅",
                               webhookURL: DISCORD
               }
           }
           failure {
               echo 'Build or deployment failed. Check logs for details.'
               withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                   discordSend title: "${env.JOB_NAME} : ${env.GIT_COMMIT_SHORT}",
                               description: "Build #${env.BUILD_NUMBER} 실패 ❌",
                               webhookURL: DISCORD
               }
           }
       }
   }