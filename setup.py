import os
import sys
import shutil
import winreg
from setuptools import setup, find_packages

def installvpol():
    if sys.platform == "win32":
        scriptsDir = os.path.join(sys.prefix, "Scripts")
    else:
        scriptsDir = os.path.join(sys.prefix, "bin")

    shutil.copy("vpol.py", os.path.join(scriptsDir, "vpol.py"))
    shutil.copy("vpol_editor.py", os.path.join(scriptsDir, "vpol_editor.py"))

    with open(os.path.join(scriptsDir, "vpol.bat"), "w") as f:
        f.write(f'@echo off\n"{sys.executable}" "{os.path.join(scriptsDir, "vpol.py")}" %*')

    print("VPOL installed successfully!")

def associatevpolfiles():
    if sys.platform != "win32":
        print("File association is only supported on Windows.")
        return

    vpolScript = os.path.join(sys.prefix, "Scripts", "vpol.py")
    vpolEditorScript = os.path.join(sys.prefix, "Scripts", "vpol_editor.py")
    iconPath = os.path.abspath("vpol.ico")

    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".vpol") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Virtual Processing Operating Language File")

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "Virtual Processing Operating Language File") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "VPOL Script")
            with winreg.CreateKey(key, "DefaultIcon") as iconKey:
                winreg.SetValue(iconKey, "", winreg.REG_SZ, iconPath)
            with winreg.CreateKey(key, "shell") as shellKey:
                with winreg.CreateKey(shellKey, "open") as openKey:
                    with winreg.CreateKey(openKey, "command") as commandKey:
                        winreg.SetValue(commandKey, "", winreg.REG_SZ, f'"{sys.executable}" "{vpolScript}" "%1"')
                with winreg.CreateKey(shellKey, "edit") as editKey:
                    winreg.SetValue(editKey, "", winreg.REG_SZ, "Edit VPOL File")
                    with winreg.CreateKey(editKey, "command") as editCommandKey:
                        winreg.SetValue(editCommandKey, "", winreg.REG_SZ, f'"{sys.executable}" "{vpolEditorScript}" "%1"')
                with winreg.CreateKey(shellKey, "Edit with VPOL") as editVpolKey:
                    winreg.SetValue(editVpolKey, "", winreg.REG_SZ, "Edit with VPOL")
                    with winreg.CreateKey(editVpolKey, "command") as editVpolCommandKey:
                        winreg.SetValue(editVpolCommandKey, "", winreg.REG_SZ, f'"{sys.executable}" "{vpolEditorScript}" "%1"')

        print("VPOL file association created successfully!")
    except Exception as e:
        print(f"Error creating file association: {e}")

def main():
    setup(
        name="vpol",
        version="1.0",
        packages=find_packages(),
        install_requires=[
            "colorama",
            "requests",
            "scapy",
        ],
        py_modules=["vpol", "vpol_editor"],
        entry_points={
            "console_scripts": [
                "vpol=vpol:main",
                "vpol_editor=vpol_editor:main",
            ],
        },
        include_package_data=True,
        package_data={
            "": ["vpol.ico"],
        },
    )

    installvpol()
    associatevpolfiles()

    vpolVersion = "1.0"
    with open(os.path.join(sys.prefix, "Scripts", "vpol_version.bat"), "w") as f:
        f.write(f'@echo VPOL version {vpolVersion}')

    print("VPOL setup completed successfully!")

if __name__ == "__main__":
    main()
