import os
import sys
import subprocess
import ctypes
import time

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_jarvis():
    """Run the Jarvis executable"""
    # Get the directory of the launcher script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Jarvis executable
    exe_path = os.path.join(base_dir, "Jarvis.exe")
    
    if not os.path.exists(exe_path):
        print(f"Error: Jarvis executable not found at {exe_path}")
        print("Please make sure the launcher is in the same directory as Jarvis.exe")
        input("Press Enter to exit...")
        return
    
    try:
        # Run the executable
        print(f"Starting Jarvis from {exe_path}...")
        subprocess.Popen([exe_path])
    except Exception as e:
        print(f"Error launching Jarvis: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    # Check if admin privileges are needed (uncomment if needed)
    # if not is_admin():
    #     # Re-run the script with admin rights
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    #     sys.exit()
    
    run_jarvis() 