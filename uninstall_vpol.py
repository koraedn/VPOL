import os
import sys
import shutil
import winreg

def removefromscripts():
    if sys.platform == "win32":
        scriptsDir = os.path.join(sys.prefix, "Scripts")
    else:
        scriptsDir = os.path.join(sys.prefix, "bin")

    filesToRemove = ["vpol.py", "vpol.bat", "vpol_version.bat"]
    
    for file in filesToRemove:
        filePath = os.path.join(scriptsDir, file)
        if os.path.exists(filePath):
            os.remove(filePath)
            print(f"Removed {filePath}")
        else:
            print(f"{filePath} not found")

def removefileassociation():
    if sys.platform != "win32":
        print("File association removal is only supported on Windows.")
        return

    try:
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, ".vpol")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "Virtual Processing Operating Language File")
        print("VPOL file association removed successfully")
    except WindowsError:
        print("VPOL file association not found or already removed")

def main():
    print("Uninstalling VPOL...")
    removefromscripts()
    removefileassociation()
    print("VPOL uninstallation completed")

if __name__ == "__main__":
    main()
