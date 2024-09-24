pipeline {
    agent none
    environment {
        DOCKER_REPO = "ktb11chatbot/ktb-11-project-1-chatbot-nlp"
        GIT_BRANCH = 'main'  // Git branch to build
        JENKINS_NAMESPACE = 'devops-tools'  // Namespace for Kaniko build
        KANIKO_POD_YAML = '/var/jenkins_home/kaniko/nlp-kaniko-ci.yaml' // Path to Kaniko Pod YAML file
        KANIKO_POD_NAME = 'kaniko-nlp'
        DEPLOYMENT_NAMESPACE = 'ktb-chatbot'
        DEPLOYMENT_NAME = 'nlp-deployment'
        DEPLOYMENT_CONTAINER_NAME = 'nlp'
    }
    stages {
        stage('Checkout Source Code') {
            agent any
            steps {
                // Checkout Git source code
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Current Git Commit Short: ${env.GIT_COMMIT_SHORT}" // Use first 7 characters of Git commit ID as tag
                }
            }
        }
        stage('Update Kaniko YAML') {
            agent { label '' }
            steps {
                script {
                    // Update the image tag in the Kaniko YAML file
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
                    // Apply the dynamically updated Kaniko Pod YAML file to Kubernetes
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
                    // Wait for 6 minutes
                    for (int i = 6; i > 0; i--) {
                        echo "Remaining wait time: ${i} minutes"
                        sleep time: 1, unit: 'MINUTES'
                    }
                    // Deploy to Kubernetes using 'kubectl set image'
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
        always {
                node {
                    script {
                        try {
                            // Kaniko 포드 로그를 캡처합니다.
                            kanikolog = sh(script: "kubectl logs ${KANIKO_POD_NAME} -n ${JENKINS_NAMESPACE}", returnStdout: true)
                        } catch (e) {
                            echo "Failed to get Kaniko logs: ${e}"
                            kanikolog = "Kaniko logs not available."
                        }
                        // Kaniko 포드를 삭제합니다.
                        sh """
                        kubectl delete -f ${KANIKO_POD_YAML} -n ${JENKINS_NAMESPACE} || true
                        """
                    }
                }
            }
        success {
            echo 'Build and push successful!'
            withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                discordSend description: """
                제목: ${currentBuild.displayName}
                결과: ${currentBuild.result}
                실행 시간: ${currentBuild.duration / 1000}s
                """,
                link: env.BUILD_URL, result: currentBuild.currentResult,
                title: "${env.JOB_NAME} : ${currentBuild.displayName} Success",
                webhookURL: DISCORD
            }
        }
        failure {
            echo 'Build or deployment failed. Check logs for details.'
            withCredentials([string(credentialsId: 'Discord-Webhook', variable: 'DISCORD')]) {
                discordSend description: """
                제목: ${currentBuild.displayName}
                결과: ${currentBuild.result}
                실행 시간: ${currentBuild.duration / 1000}s
                """,
                link: env.BUILD_URL,
                result: 'FAILURE',
                title: "${env.JOB_NAME} : ${currentBuild.displayName} Failure",
                webhookURL: DISCORD
            }
        }
    }
}