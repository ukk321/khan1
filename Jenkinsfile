pipeline {
    agent any

    environment {
        // AWS Credentials (from Jenkins credentials)
        AWS_ACCESS_KEY_ID = credentials('aws-access-key') // ID of the Access Key credential
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key') // ID of the Secret Key credential

        // AWS Region and S3 Bucket
        AWS_REGION = 'us-east-1' // Your AWS Region
        S3_BUCKET = 'jbuckei' // Your S3 bucket name
    }

    stages {
        // Stage 1: Checkout code from GitHub
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ukk321/khan1.git' // Your GitHub repository
            }
        }

        // Stage 2: Build the static site (if needed)
        stage('Build') {
            steps {
                sh 'echo "Building static site..."'
                // Add build commands if needed (e.g., npm install, npm run build)
                // Example:
                // sh 'npm install'
                // sh 'npm run build'
            }
        }

        // Stage 3: Deploy to S3
        stage('Deploy to S3') {
            steps {
                sh '''
                echo "Deploying to S3..."
                aws s3 sync . s3://${S3_BUCKET} --region ${AWS_REGION} --acl public-read --exclude ".git/*" --exclude "Jenkinsfile" --delete
                '''
            }
        }
    }
}
