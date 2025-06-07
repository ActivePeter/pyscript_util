#!/usr/bin/env python3
"""
Export offline installer for pyscript_util
Creates a standalone installer package that can be used without internet connection
"""

import os
import sys
import shutil
import datetime

def chdir_to_cur_file():
    """Change to the directory containing this script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    return script_dir

def run_cmd(command):
    """Execute a command using os.system"""
    print(f"Executing command: {command}")
    result = os.system(command)
    print(f"Command completed with exit code: {result}")
    return result

def create_offline_installer():
    """Create offline installer package"""
    print("Creating pyscript_util offline installer...")
    
    # Get current directory (now this is the root directory)
    current_dir = chdir_to_cur_file()
    
    # Create installer directory name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    installer_name = f"pyscript_util_offline_installer_{timestamp}"
    installer_dir = os.path.join(current_dir, installer_name)
    
    # Create installer directory
    print(f"Creating installer directory: {installer_dir}")
    os.makedirs(installer_dir, exist_ok=True)
    
    # Copy all files and directories from current directory except installer directories
    print(f"Copying files from: {current_dir}")
    
    for item in os.listdir(current_dir):
        # Skip installer directories and this script
        if (item.startswith('pyscript_util_offline_installer_') or 
            item == os.path.basename(__file__)):
            print(f"Skipping: {item}")
            continue
        
        src_path = os.path.join(current_dir, item)
        dst_path = os.path.join(installer_dir, item)
        
        if os.path.isdir(src_path):
            print(f"Copying directory: {item}")
            shutil.copytree(src_path, dst_path)
        else:
            print(f"Copying file: {item}")
            shutil.copy2(src_path, dst_path)
    
    # Create install.py script
    install_script_path = os.path.join(installer_dir, "install.py")
    create_install_script(install_script_path)
    print(f"Created: install.py")
    
    print(f"\nOffline installer created successfully!")
    print(f"Installer location: {installer_dir}")
    print(f"To install pyscript_util, run in the installer directory:")
    print(f"  python install.py")
    
    return True

def create_install_script(install_path):
    """Create install.py script"""
    install_content = '''#!/usr/bin/env python3
"""
One-click installer for pyscript_util
"""

import os
import sys

def run_cmd(command):
    """Execute a command"""
    print(f"Executing: {command}")
    result = os.system(command)
    if result != 0:
        print(f"Command failed with exit code: {result}")
        return False
    return True

def main():
    print("pyscript_util One-Click Installer")
    print("=" * 35)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Try different installation methods
    methods = [
        ("pip install (local)", "pip install ."),
        ("pip install (editable)", "pip install -e ."),
        ("setup.py install", f"{sys.executable} setup.py install"),
    ]
    
    for method_name, command in methods:
        print(f"\nTrying: {method_name}")
        if run_cmd(command):
            print(f"✓ Installation successful using: {method_name}")
            break
        else:
            print(f"✗ Failed: {method_name}")
    else:
        print("\nAll installation methods failed!")
        print("Manual installation options:")
        print("1. Copy pyscript_util.py to your Python site-packages directory")
        print("2. Add the current directory to your PYTHONPATH")
        sys.exit(1)
    
    # Test the installation
    print("\nTesting installation...")
    try:
        import pyscript_util
        print("✓ pyscript_util imported successfully")
        print("✓ Installation completed!")
    except ImportError as e:
        print(f"✗ Import test failed: {e}")

if __name__ == "__main__":
    main()
'''
    with open(install_path, 'w', encoding='utf-8') as f:
        f.write(install_content)

if __name__ == "__main__":
    success = create_offline_installer()
    if not success:
        sys.exit(1) 