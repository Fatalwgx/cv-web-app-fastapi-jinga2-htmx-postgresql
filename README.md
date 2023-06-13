# Web cv app with automated testing and dedicated infrastucture
  <p align="left">
    <img src="https://github.com/Fatalwgx/README/blob/master/icons/python.svg" title="Python" width="50" height="50"  alt="python"/>
    <img src="https://cdn.worldvectorlogo.com/logos/fastapi-1.svg" title="FastAPI" width="50" height="50"  alt="allure"/>
    <img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/97_Docker_logo_logos-256.png" title="Docker" width="50" height="50"  alt="allure"/>
    <img src="https://cdn.worldvectorlogo.com/logos/postgresql.svg" title="postgres" width="50" height="50"  alt="allure"/>
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/aa/Requests_Python_Logo.png" title="requests" width="50" height="50"  alt="allure"/>
    <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Selenium_Logo.png" title="selenium" width="50" height="50"  alt="allure"/>
    <img src="https://github.com/Fatalwgx/README/blob/master/icons/selenoid.svg" title="selenoid" width="50" height="50"  alt="selenoid"/>
    <img src="https://github.com/Fatalwgx/README/blob/master/icons/jenkins.svg" title="Jenkins" width="50" height="50"  alt="jenkins"/>
    <img src="https://github.com/Fatalwgx/README/blob/master/icons/allure.svg" title="Allure" width="50" height="50"  alt="allure"/>
 </p>

## Summary
### Purpose
Personal project started with interest in how api's are created which ended up iflating several times way beyond the scope of my capabailities. It maybe janky, but I learned a lot with it and it actually serves it's purpose - it's a good and flexible dummy for my automation project.

### Application
Backend is written in python using FastAPI and pydantic for validation. "Frontend" is done by returning html documents as responses and web interactions, such as requests are done with HTMX. Application has it's own Postgres database and communicates with it on api methods level. The whole project is containerized with docker.

### Infrastructure
[Infrastructure project](https://github.com/Fatalwgx/cvwebsite-infra-docker-jenkins-selenoid) acts as external and independent service hosting Jenkins, Selenoid and Selenoid-ui for automated test runs. Jenkins has already preconfigured plugins and pipelines with jenkisfiles for this project. Automation is runs on Jenkins' master machine, web-ui test runs on selenoid which feature video, screenshot and html-page logging to allure-reports. Through selenoid-ui sessions can be monitored, debugged and manually tested.

### Automation
[Automation project](https://github.com/Fatalwgx/cvwebsite-automation-tests) features web-ui selenium based test, with selene as a wrapper api above selenium. Api test are performed with requests and schema validation using pydantic. These can be triggered locally, from Jenkins pipeline or can also run from a dedicated container if needed. All the test runs generate allure-reports, which in turn are attached to specific runs in Jenkins. Database interactions can performed with sqlalchemy helper directly into the database.


## Setup and execution

### Prerequisites
- Make sure docker is installed
- Make sure that docker compose v2 is enabled
- Im using wsl2, so there's a slight possibility that something might be different on linux

### Part 1 - Application
---
1. Change directory to your preference
2. Clone project from https://github.com/Fatalwgx/cv-web-app-fastapi-jinga2-htmx-postgresql.git
```
git clone https://github.com/Fatalwgx/cv-web-app-fastapi-jinga2-htmx-postgresql.git
```
3. Start docker compose with image build option in detached mode
```
docker compose up -d --build
```
![mintty_wj9xW5Jw0N](https://github.com/Fatalwgx/README/assets/98048609/57bfc3a6-33cf-42f3-85f9-d90d07d44ee4)

4. Once terminal process finishes, you can check whether or not the app is available by opening http://localhost:80/ in a browser

- CV Page
![chrome_CDbL1oLcGC](https://github.com/Fatalwgx/README/assets/98048609/090c30df-40c9-4fcd-879e-9438e7b3037e)

- File Attachments
![chrome_urcCvQWYKE](https://github.com/Fatalwgx/README/assets/98048609/02d13d16-fa0a-4eda-919f-3b4e4263b1de)

- Slots Game
![chrome_ljhc87Zewg](https://github.com/Fatalwgx/README/assets/98048609/11f7f18f-a9a6-4ed4-b010-572b24a01174)

- Api Swagger Documentation
![chrome_HaL5XIXayY](https://github.com/Fatalwgx/README/assets/98048609/c03684e4-fd83-4ac3-85d3-1893be58701c)

### Part 2 - Infrastructure
---
1. Change directory to your preference
2. Clone project from https://github.com/Fatalwgx/cvwebsite-infra-docker-jenkins-selenoid
This one will take sometime because Jenkins is already installed and weights around ~500Mb
```
git clone https://github.com/Fatalwgx/cvwebsite-infra-docker-jenkins-selenoid
```
3. Start docker compose with image build option in detached mode. Might take a few minutes for Jenkins to initialize completely.
```
docker compose up -d --build
```
![mintty_dbrABCoAhv](https://github.com/Fatalwgx/README/assets/98048609/e453509e-dd1a-4099-ab80-b611cc8e1f85)

4. Once Jenkins is up, it can be accessed at http://localhost:8888/ credentials are admin/admin
5. From dashboard select "Regression" pipeline. This project's automation is running using the following jenkinsfile
```
pipeline {
    agent any

    stages {
        stage('checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/Fatalwgx/cvwebsite-automation-tests'
            }
        }
        stage('test execution') {
            steps {
                catchError(buildResult: 'UNSTABLE', message: 'uh oh', stageResult: 'UNSTABLE') {
                    withEnv(['REMOTE_DRV=http://selenoid:4444/wd/hub', 'WEB_URL=http://api:80', 'API_SERVICE_URL=http://api:80', 'pg_user=postgres', 'pg_password=postgres', 'pg_alias=postgres-container']) {
                        sh 'pip install -r requirements.txt'
                        sh 'pytest ./tests/ --alluredir=allure-results'
                    }
                }
            }
        }
        stage('reporting') {
            steps {
                allure includeProperties: false, jdk: '', reportBuildPolicy: 'ALWAYS', results: [[path: 'allure-results']]
            }
        }
    }
}

```

6. Click "Build now", Jenkins will follow instructions from jenkinsfile, install, build and run test automation.
![chrome_q33rnbx1MN](https://github.com/Fatalwgx/README/assets/98048609/ddf83fd8-37a2-400b-8ac9-e899aa9b2e50)

7. Once the run is completed click on allure logo in the build history sidebar to view detailed report of the runs and it's attachemnts.
![chrome_Rdp6WdkDNY](https://github.com/Fatalwgx/README/assets/98048609/ffa10dba-61ad-4ee0-99f0-73f0ed9bc41a)

