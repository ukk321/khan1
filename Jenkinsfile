pipeline {
    agent any

    environment {
        SCRIPT_PATH = '/home/ubuntu/ecomm_script.sh'
        TARGET_BRANCH = 'main-dev' // specify the branch you want to trigger on
    }

    triggers {
        githubPush() // Triggered by GitHub webhook
    }

    stages {
        stage('Check Branch') {
            steps {
                script {
                    // Print the branch for verification
                    def branch = env.GIT_BRANCH?.replace('origin/', '')
                    echo "Detected branch after stripping 'origin/': ${branch}"
                    echo "Target branch: ${TARGET_BRANCH}"
                }
            }
        }

        stage('Run Script') {
            when {
                expression {
                    // Remove 'origin/' from GIT_BRANCH and compare it with TARGET_BRANCH
                    def branch = env.GIT_BRANCH?.replace('origin/', '')
                    branch == TARGET_BRANCH
                }
            }
            steps {
                echo "Running on branch: ${TARGET_BRANCH}"
                sh "sudo -u ubuntu /home/ubuntu/ecomm_script.sh"
            }
        }
    }

    post {
        success {
            echo 'Script executed successfully!'
        }
        failure {
            echo 'Script execution failed. Check logs for details.'
        }
    }
}
