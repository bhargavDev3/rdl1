import os
import re
import subprocess
import requests
from requests_ntlm import HttpNtlmAuth

# Constants
CLIENT_NAME = "DemoReports"  # Change this to the new client name
SOLUTION_FILE_PATH = r"C:\Users\bhargavhallmark\Desktop\rdls\2024\09.September\03092024\DemoReportProject"
REPORT_USER = "bhargavhallmark"
REPORT_PASSWORD = "qL5R*MLO[h_S<26"
REPORT_SERVER_URL = "http://hallmark2/Reports"  # Replace with your SSRS server URL

# Derived paths
SOLUTION_DIR = os.path.dirname(SOLUTION_FILE_PATH)
RDS_FILE_PATH = os.path.join(SOLUTION_DIR, "HallmarkDS.rds")
RDL_FILES = [os.path.join(SOLUTION_DIR, f) for f in os.listdir(SOLUTION_DIR) if f.endswith(".rdl")]

# Fixed inputs
DATABASE_NAME = "DemoReportsDB"  # Hardcoded database name
DATA_SOURCE = "HALLMARK2"  # Hardcoded data source

def update_sln_file(sln_path, client_name):
    with open(sln_path, 'r') as file:
        content = file.read()

    # Replace the client name in TargetDataSourceFolder and TargetReportFolder
    content = content.replace("/rar/DS", f"/{client_name}/DS")
    content = content.replace("/rar/RDLS", f"/{client_name}/RDLS")

    with open(sln_path, 'w') as file:
        file.write(content)

def update_rds_file(rds_path, data_source, database_name):
    with open(rds_path, 'r') as file:
        content = file.read()

    # Replace the entire connection string
    content = re.sub(
        r'Data Source=\w+;Initial Catalog=\w+DB',
        f'Data Source={data_source};Initial Catalog={database_name}',
        content
    )

    with open(rds_path, 'w') as file:
        file.write(content)

def rebuild_solution(sln_path):
    msbuild_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
    command = [msbuild_path, sln_path, "/t:Rebuild", "/p:Configuration=Release"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Solution rebuilt successfully.")
    else:
        print("Failed to rebuild solution:", result.stderr)

def deploy_rdl_files(rdl_files, client_name, username, password):
    for rdl_file in rdl_files:
        report_name = os.path.basename(rdl_file).replace('.rdl', '')
        target_folder = f"/{client_name}/RDLS"
        url = f"{REPORT_SERVER_URL}/Reports/api/v2.0/Reports"
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        params = {
            'TargetFolder': target_folder,
            'Overwrite': 'true',
        }
        with open(rdl_file, 'rb') as file:
            response = requests.put(
                url,
                headers=headers,
                params=params,
                data=file,
                auth=HttpNtlmAuth(username, password),
            )
            if response.status_code == 200:
                print(f"Successfully deployed {report_name} to {target_folder}")
            else:
                print(f"Failed to deploy {report_name}: {response.status_code} - {response.text}")

def main():
    # Update solution file
    update_sln_file(SOLUTION_FILE_PATH, CLIENT_NAME)

    # Update .rds file
    update_rds_file(RDS_FILE_PATH, DATA_SOURCE, DATABASE_NAME)

    # Rebuild the solution
    rebuild_solution(SOLUTION_FILE_PATH)

    # Deploy .rdl files
    deploy_rdl_files(RDL_FILES, CLIENT_NAME, REPORT_USER, REPORT_PASSWORD)

if __name__ == "__main__":
    main()