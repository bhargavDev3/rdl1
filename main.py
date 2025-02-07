import os
import re
import subprocess
import requests
from requests_ntlm import HttpNtlmAuth

# Constants
CLIENT_NAME = "DemoReports"  # Change this to the new client name
PROJECT_FILE_PATH = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls\2024\09.September\03092024\DemoReportProject\DemoReportProject.rptproj"
SOLUTION_FILE = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls\2024\09.September\03092024\DemoReportProject\DemoReportProject.sln"
VS_PATH = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"

REPORT_USER = "bhargavhallmark"
REPORT_PASSWORD = "qL5R*MLO[h_S<26"
REPORT_SERVER_URL = "http://hallmark2/Reports"  # Use /ReportServer, not /Reports

# Derived paths
PROJECT_DIR = os.path.dirname(PROJECT_FILE_PATH)
RDS_FILE_PATH = os.path.join(PROJECT_DIR, "HallmarkDS.rds")
RDL_FILES = [os.path.join(PROJECT_DIR, f) for f in os.listdir(PROJECT_DIR) if f.endswith(".rdl")]

# Fixed inputs
DATABASE_NAME = "DemoReportsDB"
DATA_SOURCE = "HALLMARK2"

def update_rptproj_file(rptproj_path, client_name, report_server_url):
    """Updates the .rptproj file with the correct report server and folder paths."""
    try:
        with open(rptproj_path, 'r') as file:
            content = file.read()

        content = re.sub(r'<TargetReportFolder>.*</TargetReportFolder>', 
                         f'<TargetReportFolder>/{client_name}/RDLS</TargetReportFolder>', content)
        content = re.sub(r'<TargetDatasourceFolder>.*</TargetDatasourceFolder>', 
                         f'<TargetDatasourceFolder>/{client_name}/DS</TargetDatasourceFolder>', content)
        content = re.sub(r'<TargetServerURL>.*</TargetServerURL>', 
                         f'<TargetServerURL>{report_server_url}</TargetServerURL>', content)

        with open(rptproj_path, 'w') as file:
            file.write(content)

        print(f"Successfully updated: {rptproj_path}")
    except Exception as e:
        print(f"Error updating {rptproj_path}: {e}")

def update_rds_file(rds_path, data_source, database_name):
    """Updates the connection string in the .rds file."""
    try:
        with open(rds_path, 'r') as file:
            content = file.read()

        content = re.sub(r'Data Source=\w+;Initial Catalog=\w+DB', 
                         f'Data Source={data_source};Initial Catalog={database_name}', content)

        with open(rds_path, 'w') as file:
            file.write(content)

        print(f"Successfully updated: {rds_path}")
    except Exception as e:
        print(f"Error updating {rds_path}: {e}")

def rebuild_and_deploy_solution(sln_path):
    """Rebuilds and deploys the solution using Visual Studio's CLI (devenv.exe)."""
    if not os.path.exists(VS_PATH):
        print(f"Error: Visual Studio executable not found at {VS_PATH}")
        return
    
    if not os.path.exists(sln_path):
        print(f"Error: Solution file not found at {sln_path}")
        return

    try:
        # Rebuild the solution
        rebuild_command = [VS_PATH, sln_path, "/Rebuild", "Release"]
        rebuild_result = subprocess.run(rebuild_command, capture_output=True, text=True)

        if rebuild_result.returncode == 0:
            print("Solution rebuilt successfully.")
        else:
            print("Solution rebuild failed!")
            print(rebuild_result.stderr)
            return  # Stop execution if rebuild fails

        # Deploy the reports using Visual Studio CLI
        deploy_command = [VS_PATH, sln_path, "/Deploy", "Release"]
        deploy_result = subprocess.run(deploy_command, capture_output=True, text=True)

        if deploy_result.returncode == 0:
            print("RDL files deployed successfully!")
        else:
            print("Deployment failed!")
            print(deploy_result.stderr)

    except Exception as e:
        print(f"An error occurred: {e}")

def deploy_rdl_files(rdl_files, client_name, username, password):
    """Uploads RDL files to SSRS via HTTP PUT request."""
    for rdl_file in rdl_files:
        report_name = os.path.basename(rdl_file).replace('.rdl', '')
        target_folder = f"/{client_name}/RDLS"
        url = f"{REPORT_SERVER_URL}/browse/DemoReports/RDLS"
        headers = {'Content-Type': 'application/octet-stream'}
        params = {'TargetFolder': target_folder, 'Overwrite': 'true'}

        with open(rdl_file, 'rb') as file:
            try:
                response = requests.put(
                    url, headers=headers, params=params, data=file, 
                    auth=HttpNtlmAuth(username, password)
                )
                if response.status_code == 200:
                    print(f"Successfully deployed {report_name} to {target_folder}")
                else:
                    print(f"Failed to deploy {report_name}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"An error occurred while deploying {report_name}: {e}")

def main():
    """Main function that orchestrates the entire RDL deployment process."""
    update_rptproj_file(PROJECT_FILE_PATH, CLIENT_NAME, REPORT_SERVER_URL)
    update_rds_file(RDS_FILE_PATH, DATA_SOURCE, DATABASE_NAME)
    rebuild_and_deploy_solution(SOLUTION_FILE)
    deploy_rdl_files(RDL_FILES, CLIENT_NAME, REPORT_USER, REPORT_PASSWORD)

if __name__ == "__main__":
    main()
