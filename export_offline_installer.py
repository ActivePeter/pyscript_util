#!/usr/bin/env python3
"""
Export offline installer for pyscript_util
Creates a standalone installer package that can be used without internet connection
Now supports dependencies download for offline installation
"""

import os
import sys
import shutil
import datetime
import subprocess
import fnmatch

# 适配系统选择python命令
pythoncmd = "python3"
if sys.platform == "win32":
    pythoncmd = "python"

def should_skip_item(item_name, item_path):
    """
    Determine if an item should be skipped during copying
    Returns True if the item should be skipped, False otherwise
    """
    # Skip specific files and directories (no wildcards)
    skip_items = [
        # Version control
        '.git',
        '.gitignore',
        '.gitattributes',
        '.svn',
        '.hg',
        
        # Python cache and build files
        '__pycache__',
        '.pytest_cache',
        'build',
        'dist',
        '.eggs',
        
        # IDE and editor files
        '.vscode',
        '.idea',
        '.DS_Store',
        'Thumbs.db',
        'desktop.ini',
        
        # Testing and development
        'tests',
        'test',
        '.coverage',
        '.tox',
        '.nox',
        'htmlcov',
        
        # Virtual environments
        'venv',
        'env',
        '.env',
        '.venv',
        'virtualenv',
        
        # Documentation build
        'docs',
        'site',
        
        # OS specific
        '.Trash-1000',
        '.Trash-1001',
        
        # Development configuration files
        '.flake8',
        '.pylintrc',
        'tox.ini',
        'pytest.ini',
        '.github',
        
        # Development and build scripts
        'export_offline_installer.py',
        'publish_to_pip.py',
        'release_package.py',
        'deploy_script.py',
        'dev_setup.py',
        'debug_tool.py',
        'build_package.py',
    ]
    
    # Check for exact matches
    if item_name in skip_items:
        return True
    
    # Check for specific file extensions that should be skipped
    skip_extensions = ['.pyc', '.pyo', '.pyd', '.swp', '.swo', '.tmp', '.temp', '.log']
    _, ext = os.path.splitext(item_name.lower())
    if ext in skip_extensions:
        return True
    
    # Check for backup files
    if item_name.endswith('~'):
        return True
    
    # Check for files ending with .egg-info
    if item_name.endswith('.egg-info'):
        return True
    
    # Check for test files with specific patterns
    if (item_name.startswith('test_') and item_name.endswith('.py')) or item_name == 'conftest.py':
        return True
    
    # Special checks for directories
    if os.path.isdir(item_path):
        # Skip empty directories
        try:
            if not os.listdir(item_path):
                return True
        except PermissionError:
            return True
    
    return False

def get_essential_files():
    """
    Get list of essential files that must be included
    """
    essential_files = [
        'setup.py',
        'setup.cfg',
        'pyproject.toml',
        'README.md',
        'README.rst',
        'README.txt',
        'LICENSE',
        'LICENSE.txt',
        'MANIFEST.in',
        'requirements.txt',
        'requirements-dev.txt',
    ]
    
    return essential_files

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

def run_subprocess(command):
    """Execute a command using subprocess for better output control"""
    print(f"Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def download_dependencies(installer_dir):
    """Download all dependencies as wheel files"""
    print("Downloading dependencies for offline installation...")
    
    # Create dependencies directory
    deps_dir = os.path.join(installer_dir, "dependencies")
    os.makedirs(deps_dir, exist_ok=True)
    
    # Download dependencies using pip download
    # This will download all dependencies including transitive ones
    download_cmd = f"{pythoncmd} -m pip download . --dest {deps_dir} --prefer-binary"
    
    if run_subprocess(download_cmd):
        print("✅ Dependencies downloaded successfully")
        
        # List downloaded files
        print("Downloaded dependency files:")
        for file in os.listdir(deps_dir):
            print(f"  - {file}")
        return True
    else:
        print("⚠️ Failed to download dependencies")
        print("Offline installer will be created without pre-downloaded dependencies")
        # Remove empty deps directory
        if os.path.exists(deps_dir):
            shutil.rmtree(deps_dir)
        return False

def copy_filtered_content(src_dir, dst_dir):
    """
    Copy content from src_dir to dst_dir with filtering
    """
    essential_files = get_essential_files()
    copied_count = 0
    skipped_count = 0
    
    print(f"Copying filtered content from: {src_dir}")
    print("Essential files to include:", essential_files)
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)
        
        # Always skip the installer directory and this script
        if (item == 'pyscript_util_offline_installer' or 
            item == os.path.basename(__file__)):
            print(f"Skipping: {item} (installer files)")
            skipped_count += 1
            continue
        
        # Check if this is an essential file (always include)
        is_essential = item in essential_files
        
        # Check if item should be skipped
        should_skip = should_skip_item(item, src_path) and not is_essential
        
        if should_skip:
            print(f"Skipping: {item} (filtered out)")
            skipped_count += 1
            continue
        
        # Copy the item
        try:
            if os.path.isdir(src_path):
                print(f"Copying directory: {item}")
                # For directories, we also need to filter their contents
                shutil.copytree(src_path, dst_path, ignore=lambda dir, files: [
                    f for f in files 
                    if should_skip_item(f, os.path.join(dir, f)) and f not in essential_files
                ])
            else:
                print(f"Copying file: {item}")
                shutil.copy2(src_path, dst_path)
            
            copied_count += 1
            
        except Exception as e:
            print(f"Error copying {item}: {e}")
            skipped_count += 1
    
    print(f"\nCopy summary: {copied_count} items copied, {skipped_count} items skipped")
    return copied_count > 0

def create_offline_installer():
    """Create offline installer package"""
    print("Creating pyscript_util offline installer...")
    
    # Get current directory (now this is the root directory)
    current_dir = chdir_to_cur_file()
    
    # Create installer directory name
    installer_name = "pyscript_util_offline_installer"
    installer_dir = os.path.join(current_dir, installer_name)
    
    # Create installer directory
    print(f"Creating installer directory: {installer_dir}")
    
    # Remove existing installer directory if it exists
    if os.path.exists(installer_dir):
        print(f"Removing existing installer directory: {installer_dir}")
        shutil.rmtree(installer_dir)
    
    os.makedirs(installer_dir, exist_ok=True)
    
    # Copy filtered content
    if not copy_filtered_content(current_dir, installer_dir):
        print("Error: No files were copied to installer directory")
        return False
    
    # Download dependencies
    has_deps = download_dependencies(installer_dir)
    
    # Create install.py script
    install_script_path = os.path.join(installer_dir, "install.py")
    create_install_script(install_script_path, has_deps)
    print(f"Created: install.py")
    
    print(f"\n✅ Offline installer created successfully!")
    print(f"Installer location: {installer_dir}")
    print(f"To install pyscript_util, run in the installer directory:")
    print(f"  python install.py")
    
    if has_deps:
        print("\n✅ Includes pre-downloaded dependencies for offline installation")
    else:
        print("\n⚠️ No pre-downloaded dependencies - will require internet connection for first install")
    
    # Show installer contents
    print(f"\nInstaller contents:")
    for root, dirs, files in os.walk(installer_dir):
        level = root.replace(installer_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_size = os.path.getsize(os.path.join(root, file))
            print(f"{subindent}{file} ({file_size} bytes)")
    
    return True

def create_install_script(install_path, has_deps=False):
    """Create install.py script"""
    install_content = '''#!/usr/bin/env python3
"""
One-click installer for pyscript_util
Supports both online and offline installation
"""

import os
import sys

# 适配系统选择python命令
pythoncmd = "python3"
if sys.platform == "win32":
    pythoncmd = "python"

def run_cmd(command):
    """Execute a command"""
    print(f"Executing: {command}")
    result = os.system(command)
    if result != 0:
        print(f"Command failed with exit code: {result}")
        return False
    return True

def install_from_dependencies():
    """Install from pre-downloaded dependencies"""
    deps_dir = "dependencies"
    if not os.path.exists(deps_dir):
        return False
    
    print("Installing from pre-downloaded dependencies...")
    
    # Install all wheel files in dependencies directory
    wheel_files = [f for f in os.listdir(deps_dir) if f.endswith('.whl') or f.endswith('.tar.gz')]
    if not wheel_files:
        print("No installable packages found in dependencies directory")
        return False
    
    # Install dependencies first, then the main package
    main_package = None
    deps_packages = []
    
    for wheel_file in wheel_files:
        if wheel_file.startswith('pyscript_util') or wheel_file.startswith('pyscript-util'):
            main_package = wheel_file
        else:
            deps_packages.append(wheel_file)
    
    # Install dependencies
    for dep in deps_packages:
        dep_path = os.path.join(deps_dir, dep)
        if not run_cmd(f"{pythoncmd} -m pip install {dep_path} --no-deps"):
            print(f"Failed to install dependency: {dep}")
            return False
    
    # Install main package
    if main_package:
        main_path = os.path.join(deps_dir, main_package)
        if run_cmd(f"{pythoncmd} -m pip install {main_path} --no-deps"):
            return True
    
    return False

def main():
    # Change to script directory to ensure relative paths work correctly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    
    print("pyscript_util One-Click Installer")
    print("=" * 35)
    print(f"🐍 Using Python command: {pythoncmd}")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    installation_success = False
    
    # Try offline installation first if dependencies are available
    if ''' + str(has_deps) + ''':
        print("\\nTrying offline installation from pre-downloaded dependencies...")
        if install_from_dependencies():
            print("✓ Offline installation successful!")
            installation_success = True
        else:
            print("✗ Offline installation failed, trying online methods...")
    
    # Try online installation methods if offline failed or not available
    if not installation_success:
        methods = [
            ("pip install (local)", f"{pythoncmd} -m pip install ."),
            ("pip install (editable)", f"{pythoncmd} -m pip install -e ."),
            ("setup.py install", f"{pythoncmd} setup.py install"),
        ]
        
        for method_name, command in methods:
            print(f"\\nTrying: {method_name}")
            if run_cmd(command):
                print(f"✓ Installation successful using: {method_name}")
                installation_success = True
                break
            else:
                print(f"✗ Failed: {method_name}")
    
    if not installation_success:
        print("\\nAll installation methods failed!")
        print("Manual installation options:")
        print("1. Copy pyscript_util.py to your Python site-packages directory")
        print("2. Add the current directory to your PYTHONPATH")
        print("3. Install dependencies manually: {pythoncmd} -m pip install pyyaml>=5.1")
        sys.exit(1)
    
    # Test the installation
    print("\\nTesting installation...")
    try:
        import pyscript_util
        print("✓ pyscript_util imported successfully")
        
        # Test yaml import
        try:
            import yaml
            print("✓ pyyaml dependency available")
        except ImportError:
            print("⚠️ pyyaml not found - some features may not work")
        
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