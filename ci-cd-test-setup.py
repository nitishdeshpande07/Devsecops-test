import docker
import time
import requests
from requests.auth import HTTPBasicAuth

# Configuration Variables
JENKINS_PORT = 8080
ADMIN_USERNAME = "admin"
GITHUB_REPO_URL = "https://github.com/example/repo"  # Replace with your GitHub repo URL

# Docker Client
client = docker.from_env()

# Step 1: Retrieve Jenkins Initial Admin Password from File
def get_jenkins_admin_password(container):
    print("Retrieving Jenkins initial admin password from the file...")
    password_file_path = "/var/jenkins_home/secrets/initialAdminPassword"
    try:
        password = container.exec_run(f"cat {password_file_path}").output.decode("utf-8").strip()
        return password
    except Exception as e:
        print(f"Error retrieving the password from the file: {e}")
        return None

# Step 2: Retrieve Jenkins Crumb
def get_crumb(session, jenkins_url):
    print("Retrieving Jenkins crumb for CSRF protection...")
    crumb_url = f"{jenkins_url}/crumbIssuer/api/json"
    response = session.get(crumb_url)
    if response.status_code == 200:
        crumb = response.json().get("crumb")
        crumb_field = response.json().get("crumbRequestField")
        print("Crumb retrieved successfully.")
        return {crumb_field: crumb}
    else:
        print(f"Failed to retrieve crumb: {response.text}")
        return None

# Step 3: Configure CI/CD Pipeline
def configure_cicd_pipeline(session, jenkins_url, crumb_header):
    print("Configuring CI/CD pipeline...")

    job_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
    <flow-definition plugin="workflow-job@latest">
        <actions/>
        <description>CI/CD Pipeline for {GITHUB_REPO_URL}</description>
        <keepDependencies>false</keepDependencies>
        <properties/>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@latest">
            <scm class="hudson.plugins.git.GitSCM" plugin="git@latest">
                <configVersion>2</configVersion>
                <userRemoteConfigs>
                    <hudson.plugins.git.UserRemoteConfig>
                        <url>{GITHUB_REPO_URL}</url>
                    </hudson.plugins.git.UserRemoteConfig>
                </userRemoteConfigs>
                <branches>
                    <hudson.plugins.git.BranchSpec>
                        <name>*/main</name>
                    </hudson.plugins.git.BranchSpec>
                </branches>
                <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                <submoduleCfg class="list"/>
                <extensions/>
            </scm>
            <scriptPath>Jenkinsfile</scriptPath> <!-- Change if your pipeline file is named differently -->
            <lightweight>true</lightweight>
        </definition>
        <triggers>
            <hudson.triggers.SCMTrigger>
                <spec>H/5 * * * *</spec> <!-- Polling schedule or configure webhook for trigger on every commit -->
            </hudson.triggers.SCMTrigger>
        </triggers>
        <disabled>false</disabled>
    </flow-definition>"""

    job_name = "CI_CD_Pipeline"
    create_job_url = f"{jenkins_url}/createItem?name={job_name}"
    headers = {"Content-Type": "application/xml"}
    headers.update(crumb_header)

    # Create or update the job
    response = session.post(create_job_url, headers=headers, data=job_config_xml)
    if response.status_code == 200:
        print("CI/CD Pipeline job created successfully.")
    elif response.status_code == 400 and "already exists" in response.text:
        print("CI/CD Pipeline job already exists. Updating configuration...")
        config_url = f"{jenkins_url}/job/{job_name}/config.xml"
        response = session.post(config_url, headers=headers, data=job_config_xml)
        
        if response.status_code == 200:
            print("CI/CD Pipeline updated successfully.")
        else:
            print(f"Failed to update CI/CD pipeline: {response.text}")
    else:
        print(f"Failed to configure CI/CD pipeline: {response.status_code} - {response.text}")

# Step 4: Define Placeholder SecOps Function
def secops_function():
    print("Executing SecOps functions... (Placeholder)")
    # Placeholder for further SecOps automation

# Main Function
def main():
    container = client.containers.get("jenkins_server")  # Assumes container is running
    admin_password = get_jenkins_admin_password(container)
    
    if not admin_password:
        print("Failed to retrieve Jenkins admin password.")
        return
    
    jenkins_url = f"http://localhost:{JENKINS_PORT}/jenkins"
    session = requests.Session()
    session.auth = HTTPBasicAuth(ADMIN_USERNAME, admin_password)
    
    # Retrieve CSRF Crumb
    crumb_header = get_crumb(session, jenkins_url)
    if not crumb_header:
        print("Could not retrieve Jenkins crumb.")
        return
    
    # Configure CI/CD Pipeline
    configure_cicd_pipeline(session, jenkins_url, crumb_header)
    
    # Trigger the SecOps function placeholder
    secops_function()

    print("CI/CD pipeline setup completed successfully.")

if __name__ == "__main__":
    main()
