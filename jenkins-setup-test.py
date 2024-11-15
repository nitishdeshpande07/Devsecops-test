import docker
import time
import requests
from requests.auth import HTTPBasicAuth

# Prompt user for GitHub Repo URL
GITHUB_REPO_URL = input("Enter the public GitHub repository URL: ")

# Configuration Variables
JENKINS_IMAGE = "jenkins/jenkins:lts"  # Replace with your local Jenkins image if different
JENKINS_PORT = 8080
ADMIN_USERNAME = "admin"

# Docker Client
client = docker.from_env()

# Step 1: Start Jenkins Docker Container
def start_jenkins_container():
    print("Starting Jenkins container...")
    container = client.containers.run(
        JENKINS_IMAGE,
        detach=True,
        ports={f"{JENKINS_PORT}/tcp": JENKINS_PORT},
        name="jenkins_server",
        environment={"JENKINS_OPTS": "--prefix=/jenkins"},
    )
    print("Jenkins container started.")
    return container

# Step 2: Wait for Jenkins to be ready
def wait_for_jenkins_ready():
    print("Waiting for Jenkins to be fully initialized...")
    jenkins_url = f"http://localhost:{JENKINS_PORT}/jenkins/login"
    while True:
        try:
            response = requests.get(jenkins_url)
            if response.status_code == 200:
                print("Jenkins is ready.")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(5)  # Check every 5 seconds

# Step 3: Get Jenkins Initial Admin Password from File
def get_jenkins_admin_password_from_file(container):
    print("Retrieving Jenkins initial admin password from the file...")
    password_file_path = "/var/jenkins_home/secrets/initialAdminPassword"
    try:
        password = container.exec_run(f"cat {password_file_path}").output.decode("utf-8").strip()
        return password
    except Exception as e:
        print(f"Error retrieving the password from the file: {e}")
        return None

# Step 4: Retrieve Jenkins Crumb
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

# Step 5: Configure Jenkins with Admin User and Plugins
def configure_jenkins(admin_password):
    jenkins_url = f"http://localhost:{JENKINS_PORT}/jenkins"
    session = requests.Session()
    session.auth = HTTPBasicAuth(ADMIN_USERNAME, admin_password)

    # Retrieve CSRF Crumb
    crumb_header = get_crumb(session, jenkins_url)
    if not crumb_header:
        print("Could not retrieve Jenkins crumb.")
        return

    # Install plugins
    plugins = ["git", "workflow-aggregator", "nodejs"]
    install_plugins(session, jenkins_url, plugins, crumb_header)

    # Set up GitHub integration
    configure_github_integration(session, jenkins_url, crumb_header)

    print("Jenkins configuration complete.")

# Function to Install Plugins
def install_plugins(session, jenkins_url, plugins, crumb_header):
    print("Installing Jenkins plugins...")
    headers = {
        "Content-Type": "text/xml",
    }
    headers.update(crumb_header)  # Add the crumb to headers

    # XML data for plugins
    plugin_xml_data = "<jenkins><install plugin='{}@latest' /></jenkins>"
    
    for plugin in plugins:
        data = plugin_xml_data.format(plugin)
        response = session.post(
            f"{jenkins_url}/pluginManager/installNecessaryPlugins",
            data=data,
            headers=headers
        )
        if response.status_code == 200:
            print(f"Installed plugin: {plugin}")
        else:
            print(f"Failed to install plugin: {plugin} - Status code: {response.status_code}")
            print(f"Error response: {response.text}")
    time.sleep(10)  # Wait for plugins to install



# Configure GitHub Integration
# Updated GitHub Integration Function
def configure_github_integration(session, jenkins_url, crumb_header):
    print("Configuring GitHub integration...")

    # Define the job configuration in XML format
    job_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
    <project>
        <actions/>
        <description>Job for GitHub integration</description>
        <scm class="hudson.plugins.git.GitSCM" plugin="git@latest">
            <configVersion>2</configVersion>
            <userRemoteConfigs>
                <hudson.plugins.git.UserRemoteConfig>
                    <url>{GITHUB_REPO_URL}</url>
                </hudson.plugins.git.UserRemoteConfig>
            </userRemoteConfigs>
            <branches>
                <hudson.plugins.git.BranchSpec>
                    <name>*/main</name> <!-- Adjust branch name if necessary -->
                </hudson.plugins.git.BranchSpec>
            </branches>
            <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
            <submoduleCfg class="list"/>
            <extensions/>
        </scm>
        <builders/>
        <publishers/>
        <buildWrappers/>
    </project>"""

    headers = {
        "Content-Type": "application/xml",
    }
    headers.update(crumb_header)  # Add the crumb to headers

    # First, create the job (if it doesn’t already exist)
    job_name = "GitHub_Integration_Job"
    create_job_url = f"{jenkins_url}/createItem?name={job_name}"
    response = session.post(create_job_url, headers=headers, data=job_config_xml)

    if response.status_code == 200:
        print("GitHub job created successfully.")
    elif response.status_code == 400 and "already exists" in response.text:
        print("GitHub job already exists. Updating configuration...")
        # Update existing job configuration
        config_url = f"{jenkins_url}/job/{job_name}/config.xml"
        response = session.post(config_url, headers=headers, data=job_config_xml)

    # Check if configuration update succeeded
    if response.status_code == 200:
        print("GitHub integration configured.")
    else:
        print(f"Failed to configure GitHub integration: {response.text}")



# Main Function
def main():
    # Start Jenkins Container
    container = start_jenkins_container()

    # Wait for Jenkins to be fully initialized
    wait_for_jenkins_ready()

    # Get Jenkins Admin Password from file
    admin_password = get_jenkins_admin_password_from_file(container)
    if not admin_password:
        print("Could not retrieve Jenkins initial admin password.")
        return
    
    # Configure Jenkins
    configure_jenkins(admin_password)
    
    print("Jenkins setup completed successfully.")

if __name__ == "__main__":
    main()






