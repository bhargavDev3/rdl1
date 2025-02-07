import os
import subprocess

# Constants
VS_PATH = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"
SOLUTION_FILE = r"C:\Users\bhargavhallmark\rdl1\rdl1\rdls\2024\09.September\03092024\DemoReportProject\DemoReportProject.sln"

def deploy_rdl_with_visual_studio():
    """Deploys RDL files using Visual Studio's CLI (devenv.exe)."""
    if not os.path.exists(VS_PATH):
        print(f"Error: Visual Studio executable not found at {VS_PATH}")
        return
    
    if not os.path.exists(SOLUTION_FILE):
        print(f"Error: Solution file not found at {SOLUTION_FILE}")
        return

    try:
        # Run Visual Studio's deploy command
        command = [VS_PATH, SOLUTION_FILE, "/Deploy", "Release"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("RDL files deployed successfully!")
        else:
            print("Deployment failed!")
            print(result.stderr)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    deploy_rdl_with_visual_studio()
