import os
import re
import subprocess

# Constants
CLIENT_NAME = "DemoReports"  # Change this to the new client name
PROJECT_FILE_PATH = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls\2024\09.September\03092024\DemoReportProject\DemoReportProject.rptproj"  # Path to .rptproj file
REPORT_USER = "bhargavhallmark"
REPORT_PASSWORD = "qL5R*MLO[h_S<26"
REPORT_SERVER_URL = "http://hallmark2/ReportServer"  # Use the SSRS Web Service endpoint

# Derived paths
PROJECT_DIR = os.path.dirname(PROJECT_FILE_PATH)
RDS_FILE_PATH = os.path.join(PROJECT_DIR, "HallmarkDS.rds")
RDL_FILES = [os.path.join(PROJECT_DIR, f) for f in os.listdir(PROJECT_DIR) if f.endswith(".rdl")]

# Fixed inputs
DATABASE_NAME = "DemoReportsDB"  # Hardcoded database name
DATA_SOURCE = "HALLMARK2"  # Hardcoded data source

def update_rptproj_file(rptproj_path, client_name, report_server_url):
    try:
        # Read the .rptproj file as a text file
        with open(rptproj_path, 'r') as file:
            content = file.read()

        # Replace TargetReportFolder
        content = re.sub(
            r'<TargetReportFolder>.*</TargetReportFolder>',
            f'<TargetReportFolder>/{client_name}/RDLS</TargetReportFolder>',
            content
        )

        # Replace TargetDatasourceFolder
        content = re.sub(
            r'<TargetDatasourceFolder>.*</TargetDatasourceFolder>',
            f'<TargetDatasourceFolder>/{client_name}/DS</TargetDatasourceFolder>',
            content
        )

        # Replace TargetServerURL
        content = re.sub(
            r'<TargetServerURL>.*</TargetServerURL>',
            f'<TargetServerURL>{report_server_url}</TargetServerURL>',
            content
        )

        # Write the updated content back to the file
        with open(rptproj_path, 'w') as file:
            file.write(content)
        print(f"Successfully updated: {rptproj_path}")
    except Exception as e:
        print(f"An error occurred while updating {rptproj_path}: {e}")

def update_rds_file(rds_path, data_source, database_name):
    try:
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
        print(f"Successfully updated: {rds_path}")
    except PermissionError:
        print(f"Permission denied: {rds_path}. Ensure you have read/write access.")
    except FileNotFoundError:
        print(f"File not found: {rds_path}. Ensure the path is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")

def rebuild_solution(sln_path):
    msbuild_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    command = [msbuild_path, sln_path, "/t:Rebuild", "/p:Configuration=Release"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Solution rebuilt successfully.")
    else:
        print("Failed to rebuild solution:", result.stderr)

def deploy_rdl_files(rdl_files, client_name, username, password):
    rs_exe_path = r"C:\Program Files\Microsoft SQL Server Reporting Services\Shared Tools\RS.exe"
    for rdl_file in rdl_files:
        report_name = os.path.basename(rdl_file).replace('.rdl', '')
        target_folder = f"/{client_name}/RDLS"
        command = [
            rs_exe_path,
            '-i', rdl_file,  # Input .rdl file
            '-s', REPORT_SERVER_URL,  # SSRS server URL
            '-u', username,  # Username
            '-p', password,  # Password
            '-l', '600',  # Timeout for connection (600 seconds)
            '-v', '600',  # Timeout for execution (600 seconds)
            '-e', 'Exec2005',  # Execution mode (for SSRS 2005 compatibility)
            '-o'  # Overwrite existing report if it exists
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully deployed {report_name} to {target_folder}")
            else:
                print(f"Failed to deploy {report_name}: {result.stderr}")
        except Exception as e:
            print(f"An error occurred while deploying {report_name}: {e}")

def main():
    # Update .rptproj file
    update_rptproj_file(PROJECT_FILE_PATH, CLIENT_NAME, REPORT_SERVER_URL)

    # Update .rds file
    update_rds_file(RDS_FILE_PATH, DATA_SOURCE, DATABASE_NAME)

    # Rebuild the solution
    rebuild_solution(PROJECT_FILE_PATH)

    # Deploy .rdl files
    deploy_rdl_files(RDL_FILES, CLIENT_NAME, REPORT_USER, REPORT_PASSWORD)

if __name__ == "__main__":
    main()