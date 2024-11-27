pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_DIR = '.' // Update this path if your docker-compose.yml is in a different directory
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Clone your repository
                git url: 'https://github.com/Technocrats-Seasia/revizoboard-be.git', branch: 'Feature-Jenkins-File'
            }
        }
        
        stage('Build Docker Images') {
            steps {
                script {
                    dir(DOCKER_COMPOSE_DIR) {
                        sh 'docker-compose build'
                    }
                }
            }
        }

        stage('Deploy Services') {
            steps {
                script {
                    dir(DOCKER_COMPOSE_DIR) {
                        sh 'docker-compose down'
                        sh 'docker-compose up -d'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                dir(DOCKER_COMPOSE_DIR) {
                    sh 'docker-compose logs'
                }
            }
        }
    }
}
