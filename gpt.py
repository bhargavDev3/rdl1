import os
import re
import subprocess

# Constants
CLIENT_NAME = "DemoReports"  # Change this to the new client name
PROJECT_FILE_PATH = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls\2024\09.September\03092024\DemoReportProject\DemoReportProject.rptproj"
REPORT_SERVER_URL = "http://hallmark2/Reports"
REPORT_FOLDER = f"/{CLIENT_NAME}/RDLS"

# Derived paths
PROJECT_DIR = os.path.dirname(PROJECT_FILE_PATH)
RDS_FILE_PATH = os.path.join(PROJECT_DIR, "HallmarkDS.rds")
RDL_FILES = [os.path.join(PROJECT_DIR, f) for f in os.listdir(PROJECT_DIR) if f.endswith(".rdl")]

# Fixed inputs
DATABASE_NAME = "DemoReportsDB"
DATA_SOURCE = "HALLMARK2"

def update_rptproj_file(rptproj_path, client_name, report_server_url):
    """ Updates the .rptproj file with the new client name and server URL. """
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
    """ Updates the .rds file with the new database and data source details. """
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

def rebuild_solution(sln_path):
    """ Rebuilds the Visual Studio solution using MSBuild. """
    msbuild_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    command = [msbuild_path, sln_path, "/t:Rebuild", "/p:Configuration=Release"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Solution rebuilt successfully.")
    else:
        print("Failed to rebuild solution:", result.stderr)

def deploy_rdl_files_with_powershell(rdl_files, report_server_url, report_folder):
    """ Deploys RDL files using PowerShell (mimicking Visual Studio's deploy). """
    ps_script = f"""
    $ReportServerUri = "{report_server_url}"
    $TargetFolder = "{report_folder}"

    Import-Module SQLServer
    
    foreach ($file in {rdl_files}) {{
        $reportName = [System.IO.Path]::GetFileNameWithoutExtension($file)
        Write-Host "Deploying $reportName..."
        Publish-RsReport -Path $file -ReportServerUri $ReportServerUri -Destination $TargetFolder -Overwrite
    }}
    Write-Host "Deployment complete!"
    """

    ps_script_path = os.path.join(PROJECT_DIR, "deploy_reports.ps1")
    with open(ps_script_path, "w") as f:
        f.write(ps_script)

    result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Reports deployed successfully.")
    else:
        print("Failed to deploy reports:", result.stderr)

def main():
    update_rptproj_file(PROJECT_FILE_PATH, CLIENT_NAME, REPORT_SERVER_URL)
    update_rds_file(RDS_FILE_PATH, DATA_SOURCE, DATABASE_NAME)
    rebuild_solution(PROJECT_FILE_PATH)
    deploy_rdl_files_with_powershell(RDL_FILES, REPORT_SERVER_URL, REPORT_FOLDER)

if __name__ == "__main__":
    main()
