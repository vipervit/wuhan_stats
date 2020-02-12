pipeline {

  agent any

    stages {

       stage('BUILD') {
        steps {
            sh '. $python_prog/dev/bin/activate'
            sh 'rm -r -f dist'
            sh 'python3 setup.py sdist'
        }
       }

       stage('UPLOAD') {
        steps {
           sh 'python3 -m twine upload -u vipervit dist/*'
        }
       }

       stage('DEPLOY') {
        steps {
            sh '. $python_prog/prod/bin/activate'
            sh 'pip install wuhan-stats'
        }
       }

       stage('RESTART APPLICATION') {
       steps {
            sh '. ~/sh/wuhan/wuhan-stop.sh'
            sh '. ~/sh/wuhan/wuhan-start.sh'
        }
       }

    }

}
