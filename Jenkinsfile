def helmDeploy(Map args) {
    dir("helm-chart/app/${args.app_name}") {
        echo "[INFO] Step 1: Helm Deploy dry-run"
        sh """helm upgrade --install ${args.app_name} --namespace ${args.namespace} --set image.tag="${args.image_tag}" -f ${args.app_env}.yaml . --dry-run --debug"""

        echo "[INFO] Step 2: Helm Deploy"
        sh """helm upgrade --install ${args.app_name} --namespace ${args.namespace} --set image.tag="${args.image_tag}" -f ${args.app_env}.yaml . -w """
    }
}

def toJson = {
    input ->
    groovy.json.JsonOutput.toJson(input)
}

pipeline {
    agent {
        kubernetes {
            label "agent-${UUID.randomUUID().toString()}"
            yamlFile 'yaml/pod.yaml'
        }
    }
    stages {
        stage('Prepare') {
            steps {
                script {
                    def madkitty_url= "http://madkitty-api.devops-tools.svc.cluster.local/${app_env}/${app_name}"
                    response = httpRequest consoleLogResponseBody: true, 
                                            contentType: 'APPLICATION_JSON', 
                                            httpMode: 'GET', 
                                            url: madkitty_url, 
                                            validResponseCodes: '200'
                    
                    // writeFile file: 'mad_config.json', text: response.content
                    // def config = readJSON file: 'mad_config.json'
                    def config = readJSON text: response.content
                    def harbor_url = "harbor.mymyhub.com"
                    def image_repo = "${harbor_url}/images/${app_name}"
                    
                    config.each {
                        env["APP_"+it.key.toUpperCase()] = it.value
                    }
                    env.HARBOR_URL = harbor_url
                    env.APP_IMAGE_REPO = image_repo
                    if (config.type == "nodejs") {
                        env.APP_UT_TAG = "nodejs"
                        env.APP_UT_CMD = "yarn install && yarn test:coverage"
                    } else {
                        error '[ERROR] Invalid App Type'
                    }
                    // props = readJSON text: env.APP_CONFIG
                    // println(props.name)
                }
            }
            post {
                    success {
                        script {
                            echo "Stage: success ..."
                        }
                    }
                    unsuccessful {
                        script {
                            echo "Stage: unsuccessful ..."
                        }
                    }
            }
        }

        stage('Git'){
            steps {
                script {
                    git branch: 'dev',
                        credentialsId: '45ffa5c8-48bf-4c18-b40f-334bc25d0c56',
                        url: env.APP_GIT_URL
                    def image_tag  = sh(script: "git rev-parse --short HEAD",returnStdout:true).trim()
                    env.APP_IMAGE_TAG = image_tag
                    def robot_msg  = sh(script: "git log ${image_tag} --format='%s (%h)' -1",returnStdout:true).trim()
                    env.APP_ROBOT_MSG = robot_msg
                }
            }
            post {
                success {
                    script {
                        echo "Stage: success ..."
                    }
                }
                unsuccessful {
                    script {
                        echo "Stage: unsuccessful ..."
                    }
                }
            }
        }

        stage('Unit Test'){
            steps {
                script {
                    // container(APP_UT_TAG) {
                    //     sh APP_UT_CMD
                    // }
                    echo "[INFO] Sonarqube"
                }
            }
            post {
                success {
                    script {
                        echo "Stage: success ..."
                    }
                }
                unsuccessful {
                    script {
                        echo "Stage: unsuccessful ..."
                    }
                }
            }
        }

        stage('Docker'){
            steps {
                script {
                    container('docker') {
                        echo "[Step] Compile docker image"
                        
                        def url= "https://${env.HARBOR_URL}/api/v2.0/projects/images/repositories/${env.app_name}/artifacts/${env.APP_IMAGE_TAG}/tags"
                        def response = httpRequest httpMode: 'GET', 
                                                   url: url, 
                                                   authentication: 'harbor-token'
                        if (response.status == 200) {
                            echo "[INFO] Skipped ${env.APP_IMAGE_REPO}:${env.APP_IMAGE_TAG} Exists"
                        } else {
                            docker.withRegistry("https://${env.HARBOR_URL}", "harbor-token") {
                                echo "[INFO] Build"
                                if (env.APP_SPECIAL_DIR) {
                                    container = docker.build("${env.APP_IMAGE_REPO}:${env.APP_IMAGE_TAG}", ". --build-arg SPECIAL_NAME=${env.APP_SPECIAL_NAME} --build-arg SPECIAL_DIR=${env.APP_SPECIAL_DIR}")
                                } else {
                                    container = docker.build("${env.APP_IMAGE_REPO}:${env.APP_IMAGE_TAG}", ".")
                                }
                                echo "[INFO] Push"
                                container.push()
                                echo "[INFO] Delete"
                                sh "docker rmi ${env.APP_IMAGE_REPO}:${env.APP_IMAGE_TAG}" 
                            }
                        }
                    }
                }
            }
            post {
                success {
                    script {
                        echo "Stage: success ..."
                    }
                }
                unsuccessful {
                    script {
                        echo "Stage: unsuccessful ..."
                    }
                }
            }
        }

        stage('Helm'){
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'harbor-token', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
                        container('helm') {
                            withKubeConfig([credentialsId: app_env]) {
                                helmDeploy(
                                    username      : DOCKER_USER,
                                    password      : DOCKER_PASSWORD,
                                    app_name      : env.app_name,
                                    app_env       : env.app_env,
                                    namespace     : env.APP_NAMESPACE,
                                    image_tag     : env.APP_IMAGE_TAG
                                )
                            }
                        }
                    }
                }
            }
            post {
                success {
                    script {
                        echo "Stage: success ..."
                    }
                }
                unsuccessful {
                    script {
                        echo "Stage: unsuccessful ..."
                    }
                }
            }
        }


    }

    post {
        success {
            script {
                def body = [
                    "title": "${app_env} ${app_name} Build Success",
                    "text": "${env.APP_ROBOT_MSG}\nurl: ${BUILD_URL}"
                ]
                def response = httpRequest consoleLogResponseBody: true, 
                                           contentType: 'APPLICATION_JSON', 
                                           httpMode: 'POST', 
                                           url: "https://open.feishu.cn/open-apis/bot/hook/${env.APP_WEBHOOK}", 
                                           requestBody: toJson(body),
                                           validResponseCodes: '200'
            }
        }
        unsuccessful {
            script {
                def body = [
                    "title": "${app_env} ${app_name} Build Failed",
                    "text": "${env.APP_ROBOT_MSG}\nurl: ${BUILD_URL}"
                ]
                def response = httpRequest consoleLogResponseBody: true, 
                                           contentType: 'APPLICATION_JSON', 
                                           httpMode: 'POST', 
                                           url: "https://open.feishu.cn/open-apis/bot/hook/${env.APP_WEBHOOK}", 
                                           requestBody: toJson(body),
                                           validResponseCodes: '200'
            }
        }
    }
}
