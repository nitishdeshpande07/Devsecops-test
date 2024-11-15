## This module's script would be responsible for 2 fucntionality provisioing 
# 1. The OWASP Dependency Check Docker Image needs to be spined up and then further
# - This project directory and path is to be dynamically supplied to it so as to 
# Perform the Software Dependency Check. And then through a logical combination of the 
# following commands :  
# now we would be performing the entire scan and then compiling the 
# entire report and then storing it in the project's source directory as SCA Results/
# and also provide an on screen option to the user to choose to view the results or move
# to the further deployment stage. 

import os
import subprocess
import sys

def get_project_path():
    """Get the full path of the current project directory."""
    return os.path.abspath(os.getcwd())

def run_dependency_check(project_directory):
    """Run OWASP Dependency Check Docker container for the project."""
    report_directory = os.path.join(project_directory, 'SCA Results')
    
    # Ensure the report directory exists
    if not os.path.exists(report_directory):
        os.makedirs(report_directory)

    print(f"Running OWASP Dependency Check on the project in {project_directory}...")

    try:
        # Run the OWASP Dependency Check Docker container with the NVD API key
        subprocess.check_call([
            'docker', 'run', '--rm',
            '-v', f"{project_directory}:/src", 
            '-v', f"{report_directory}:/report",
            'owasp/dependency-check', 
            '--scan', '/src', 
            '--format', 'ALL', 
            '--out', '/report',
            '--project', 'NodeJS Project Dependency Check',
            '--nvdApiKey', '9eaafe4b-6c9c-423f-b3e4-d5279e4130e6'  # API key passed here
        ])
        print(f"Dependency check completed. Reports are stored in {report_directory}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run OWASP Dependency Check. Error: {e}")
        return False
    return True

def view_report(report_directory):
    """Provide an option to view the generated HTML report."""
    html_report_path = os.path.join(report_directory, 'dependency-check-report.html')
    
    if os.path.isfile(html_report_path):
        print(f"HTML Report found: {html_report_path}")
        view_choice = input("Do you want to view the Dependency Check report? (yes/no): ").strip().lower()
        
        if view_choice == 'yes':
            if sys.platform == 'win32':
                os.startfile(html_report_path)  # For Windows
            elif sys.platform == 'darwin':
                subprocess.call(['open', html_report_path])  # For macOS
            else:
                subprocess.call(['xdg-open', html_report_path])  # For Linux
        else:
            print("Skipping report view.")
    else:
        print("HTML report not found.")

def main():
    """Main function to run OWASP Dependency Check and provide user options."""
    project_directory = get_project_path()
    report_directory = os.path.join(project_directory, 'SCA Results')
    
    # Run the OWASP Dependency Check scan
    if not run_dependency_check(project_directory):
        return

    # Provide the option to view the generated report
    view_report(report_directory)

    # Further step for deployment or additional actions
    next_step = input("Do you want to move to the deployment stage? (yes/no): ").strip().lower()
    if next_step == 'yes':
        print("Proceeding to the deployment stage...")
        # Add deployment logic here
    else:
        print("Exiting the process.")

if __name__ == "__main__":
    main()

