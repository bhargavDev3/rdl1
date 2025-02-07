import os
import re
import subprocess
import requests
from requests_ntlm import HttpNtlmAuth

# Constants
BASE_DIR = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls"
START_YEAR = "2024"
START_MONTH = "09.September"
START_DATE = "03092024"

CLIENT_NAME = "DemoReports"
VS_PATH = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"

REPORT_USER = "bhargavhallmark"
REPORT_PASSWORD = "qL5R*MLO[h_S<26"
REPORT_SERVER_URL = "http://hallmark2/Reports"

DATABASE_NAME = "DemoReportsDB"
DATA_SOURCE = "HALLMARK2"

def execute_rdl_deployment():
    """Executes RDL deployment following the structured execution order."""
    start_processing_year = False
    start_processing_month = False

    # Get all year folders sorted
    year_folders = sorted(os.listdir(BASE_DIR))

    for year_folder in year_folders:
        year_path = os.path.join(BASE_DIR, year_folder)

        if not os.path.isdir(year_path):
            print(f"Skipping non-directory: {year_path}")
            continue

        if year_folder == START_YEAR:
            start_processing_year = True

        if not start_processing_year:
            print(f"Skipping year: {year_folder}")
            continue

        # Get all month folders sorted
        month_folders = sorted(os.listdir(year_path))

        for month_folder in month_folders:
            month_path = os.path.join(year_path, month_folder)

            if not os.path.isdir(month_path):
                print(f"Skipping non-directory: {month_path}")
                continue

            if year_folder == START_YEAR and month_folder == START_MONTH:
                start_processing_month = True

            if not start_processing_month:
                print(f"Skipping month: {month_folder}")
                continue

            # Get all date folders sorted
            date_folders = sorted(os.listdir(month_path))

            for date_folder in date_folders:
                date_path = os.path.join(month_path, date_folder)

                if not os.path.isdir(date_path):
                    print(f"Skipping non-directory: {date_path}")
                    continue

                if year_folder == START_YEAR and month_folder == START_MONTH and date_folder < START_DATE:
                    print(f"Skipping date: {date_folder} (before start date)")
                    continue

                print(f"Processing RDL files in: {date_path}")

                # Find solution file (.sln) inside the date folder
                sln_files = [f for f in os.listdir(date_path) if f.endswith(".sln")]
                if not sln_files:
                    print(f"No solution files found in: {date_path}")
                    continue

                for sln_file in sln_files:
                    sln_file_path = os.path.join(date_path, sln_file)
                    project_dir = os.path.dirname(sln_file_path)

                    # Locate the .rptproj and .rds files
                    rptproj_files = [f for f in os.listdir(project_dir) if f.endswith(".rptproj")]
                    rds_files = [f for f in os.listdir(project_dir) if f.endswith(".rds")]
                    rdl_files = [os.path.join(project_dir, f) for f in os.listdir(project_dir) if f.endswith(".rdl")]

                    if not rptproj_files or not rds_files or not rdl_files:
                        print(f"Missing required files in: {project_dir}")
                        continue

                    rptproj_file_path = os.path.join(project_dir, rptproj_files[0])
                    rds_file_path = os.path.join(project_dir, rds_files[0])

                    update_rptproj_file(rptproj_file_path, CLIENT_NAME, REPORT_SERVER_URL)
                    update_rds_file(rds_file_path, DATA_SOURCE, DATABASE_NAME)
                    rebuild_and_deploy_solution(sln_file_path)
                    deploy_rdl_files(rdl_files, CLIENT_NAME, REPORT_USER, REPORT_PASSWORD)

def update_rptproj_file(rptproj_path, client_name, report_server_url):
    """Updates the .rptproj file with correct report server and folder paths."""
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

        print(f"Updated: {rptproj_path}")
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

        print(f"Updated: {rds_path}")
    except Exception as e:
        print(f"Error updating {rds_path}: {e}")

def rebuild_and_deploy_solution(sln_path):
    """Rebuilds and deploys the solution using Visual Studio's CLI."""
    if not os.path.exists(VS_PATH):
        print(f"Error: Visual Studio not found at {VS_PATH}")
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
            return

        # Deploy the solution
        deploy_command = [VS_PATH, sln_path, "/Deploy", "Release"]
        deploy_result = subprocess.run(deploy_command, capture_output=True, text=True)

        if deploy_result.returncode == 0:
            print("Deployment successful!")
        else:
            print("Deployment failed!")
            print(deploy_result.stderr)

    except Exception as e:
        print(f"Error: {e}")

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
                    print(f"Successfully deployed: {rdl_file}")
                else:
                    print(f"Deployment failed for {rdl_file}: {response.status_code}")
            except Exception as e:
                print(f"Error deploying {rdl_file}: {e}")

# Start execution
execute_rdl_deployment()
