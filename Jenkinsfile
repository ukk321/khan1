pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-2'             
        S3_BUCKET = 'myec2testj'             
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ukk321/khan1.git'
            }
        }

        stage('Build') {
            steps {
                sh '''
                echo "Building static site..."
                # If you have no build step, you can leave this as is.
                # Otherwise, uncomment below if using Node.js-based static site:
                # npm install
                # npm run build
                '''
            }
        }

        stage('Deploy fortest.html to S3') {
            steps {
                withAWS(credentials: 'aws-jenkins-creds', region: "${AWS_REGION}") {
                    sh '''
                    echo "Deploying fortest.html to S3..."
                    aws s3 cp fortest.html s3://${S3_BUCKET}/ --acl public-read
                    '''
                }
            }
        }
    }
}
