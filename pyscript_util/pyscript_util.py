#!/usr/bin/env python3
"""
pyscript_util - Python script utilities for maximum compatibility
Provides command execution and directory management functions using os.system
"""

import os
import sys
import inspect
import typing

# Global stack to maintain stage hierarchy
_stage_stack = []


class CommandFailedError(Exception):
    """
    Exception raised when a command execution fails in 'sure' mode

    Attributes:
        command (str): The command that failed
        exit_code (int): The exit code returned by the command
        is_root (bool): Whether the command was executed with sudo privileges
    """

    def __init__(self, command, exit_code, is_root=False):
        """
        Initialize CommandFailedError

        Args:
            command (str): The command that failed
            exit_code (int): The exit code returned by the command
            is_root (bool): Whether the command was executed with sudo privileges
        """
        self.command = command
        self.exit_code = exit_code
        self.is_root = is_root

        command_type = "Root command" if is_root else "Command"
        super().__init__(f"{command_type} failed with exit code {exit_code}: {command}")


class stage:
    """
    Context manager for hierarchical step execution with formatted output

    Usage:
        with stage("step1"):
            # Some operations
            with stage("substep1"):
                # Nested operations
                pass

    Prints formatted headers like:
    =====================
    step1
    =====================

    =====================
    step1 / substep1
    =====================
    """

    def __init__(self, step_name):
        """
        Initialize stage with step name

        Args:
            step_name (str): Name of the current step
        """
        self.step_name = step_name

    def __enter__(self):
        """
        Enter the stage context - print header and push to stack

        Returns:
            stage: Self reference for context manager
        """
        # Push current step to stack
        _stage_stack.append(self.step_name)

        # Create step path from stack
        step_path = " / ".join(_stage_stack)

        # Print formatted header
        print(f"\n{'=' * 21}")
        print(step_path)
        print("=" * 21)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the stage context - pop from stack

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        # Pop current step from stack
        if _stage_stack:
            _stage_stack.pop()

        # Don't suppress exceptions
        return False


# def get_current_stage_path():
#     """
#     Get the current stage path as a string

#     Returns:
#         str: Current stage path (e.g., "step1 / substep1") or empty string if no stages
#     """
#     return " / ".join(_stage_stack) if _stage_stack else ""


# def print_stage_info():
#     """
#     Print current stage stack information for debugging
#     """
#     if _stage_stack:
#         print(f"Current stage path: {get_current_stage_path()}")
#         print(f"Stage depth: {len(_stage_stack)}")
#     else:
#         print("No active stages")


def run_cmd(command):
    """
    Execute a command using os.system and print the command before running it

    Args:
        command (str): The command to execute

    Returns:
        int: The exit status of the command (0 for success, non-zero for failure)
    """
    print(f"Executing command: {command}")
    result = os.system(command)
    print(f"Command completed with exit code: {result}")
    return result


def run_root_cmd(command):
    """
    Execute a command with sudo privileges using os.system

    Args:
        command (str): The command to execute with sudo

    Returns:
        int: The exit status of the command (0 for success, non-zero for failure)
    """
    sudoprefix = ""
    if os.geteuid() != 0:
        sudoprefix = "sudo "

    sudo_command = f"{sudoprefix}{command}"
    print(f"Executing root command: {sudo_command}")
    result = os.system(sudo_command)
    print(f"Root command completed with exit code: {result}")
    return result


def run_cmd_sure(command):
    """
    Execute a command and ensure it succeeds (raise exception on failure)

    Args:
        command (str): The command to execute

    Returns:
        int: Always returns 0 (success)

    Raises:
        CommandFailedError: If the command fails (non-zero exit code)
    """
    print(f"Executing command (sure): {command}")
    result = os.system(command)
    if result != 0:
        print(f"Command failed with exit code: {result}")
        print(f"Failed command: {command}")
        raise CommandFailedError(command, result, is_root=False)
    print(f"Command completed successfully")
    return result


def run_root_cmd_sure(command):
    """
    Execute a command with sudo privileges and ensure it succeeds (raise exception on failure)

    Args:
        command (str): The command to execute with sudo

    Returns:
        int: Always returns 0 (success)

    Raises:
        CommandFailedError: If the command fails (non-zero exit code)
    """
    result = run_root_cmd(command)
    if result != 0:
        print(f"Root command failed with exit code: {result}, will raise exception")
        raise CommandFailedError(command, result, is_root=True)
    return result


def chdir_to_cur_file():
    """
    Change the current working directory to the directory containing the calling script

    This function should be called from the main script to ensure all relative paths
    are resolved relative to the script's location. It intelligently finds the actual
    calling script, not intermediate library code.

    Returns:
        str: The new current working directory
    """
    # Try to find the actual calling script by walking up the call stack
    caller_file = None
    frame_index = 1

    while frame_index < 10:  # Limit search to prevent infinite loops
        try:
            frame = sys._getframe(frame_index)
            potential_file = frame.f_globals.get("__file__")

            if potential_file is None:
                frame_index += 1
                continue

            # Convert to absolute path for comparison
            abs_potential_file = os.path.realpath(potential_file)
            abs_current_file = os.path.realpath(__file__)

            # Skip if this is the current library file
            if abs_potential_file == abs_current_file:
                frame_index += 1
                continue

            # Skip if this is another library file (contains site-packages or pyscript_util)
            if (
                "site-packages" in abs_potential_file
                or "pyscript_util" in abs_potential_file
                and abs_potential_file != abs_current_file
            ):
                frame_index += 1
                continue

            # This looks like the actual calling script
            caller_file = abs_potential_file
            print(f"Found calling script: {caller_file}")
            break

        except ValueError:
            # No more frames available
            break

        frame_index += 1

    # Fallback strategies if we couldn't find the caller
    if caller_file is None:
        # Try to use sys.argv[0] if available (main script)
        if len(sys.argv) > 0 and sys.argv[0]:
            potential_main = os.path.realpath(sys.argv[0])
            if os.path.isfile(potential_main) and potential_main.endswith(".py"):
                caller_file = potential_main
                print(f"Using main script from sys.argv[0]: {caller_file}")
            else:
                print(f"Warning: sys.argv[0] is not a valid Python file: {sys.argv[0]}")

        # Final fallback: use the current working directory
        if caller_file is None:
            print(
                "Warning: Could not determine calling script, using current working directory"
            )
            current_dir = os.getcwd()
            print(f"Current working directory: {current_dir}")
            return current_dir

    # Get the directory containing the calling script
    script_dir = os.path.dirname(caller_file)
    print(f"Changing directory to: {script_dir}")
    os.chdir(script_dir)
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    return current_dir


def setup_script_environment():
    """
    Alias for chdir_to_cur_file() - setup script environment

    Returns:
        str: The new current working directory
    """
    return chdir_to_cur_file()


def find_file_upwards(filename) -> typing.Optional[str]:
    """
    Search for a file by walking up the directory tree from current working directory

    This function starts from the current working directory and searches for the
    specified file by moving up one directory level at a time until the file is
    found or the root directory is reached.

    Cross-platform path support:
    - Automatically handles Windows backslashes and Unix forward slashes
    - Input like 'dir/subdir/file.txt' works on both Windows and Unix systems
    - Returns paths using the correct separator for the current OS

    Args:
        filename (str): Name of the file to search for (e.g., '.git', 'package.json', 'dir/subdir/file.txt')
                       Supports both forward slashes and backslashes regardless of OS

    Returns:
        Optional[str]: Full path to the found file, or None if not found

    Example:
        # Search for .git directory to find project root
        git_path = find_file_upwards('.git')
        if git_path:
            project_root = os.path.dirname(git_path)
            print(f"Project root: {project_root}")

        # Search for nested configuration files (cross-platform)
        config_path = find_file_upwards('config/app.json')  # Works on Windows and Unix
        webpack_config = find_file_upwards('webpack.config.js')

        # Search for files in subdirectories
        nested_file = find_file_upwards('src/components/App.js')
    """
    # Normalize the filename path for cross-platform compatibility
    # This converts forward slashes to backslashes on Windows, and vice versa
    normalized_filename = os.path.normpath(filename)

    # Start from current working directory and normalize path format
    current_path = os.path.normpath(os.path.realpath(os.getcwd()))

    print(f"Searching for '{normalized_filename}' starting from: {current_path}")

    # Keep searching until we reach the root directory
    while True:
        # Construct the full path to the file we're looking for
        file_path = os.path.join(current_path, normalized_filename)

        print(f"Checking: {file_path}")

        # Check if the file exists
        if os.path.exists(file_path):
            print(f"✓ Found '{normalized_filename}' at: {file_path}")
            return file_path

        # Get parent directory and normalize it
        parent_path = os.path.normpath(os.path.dirname(current_path))

        # If we've reached the root directory, stop searching
        if parent_path == current_path:
            print(f"✗ '{normalized_filename}' not found (reached root directory)")
            return None

        # Move up one directory level
        current_path = parent_path


def setup_npm():
    """
    Setup Node.js 18 and pnpm package manager
    Installs Node.js 18 using NVM (preferred) or system package managers

    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    print("Setting up Node.js 18 and pnpm...")

    try:
        # Check if we're on a supported system
        if sys.platform == "win32":
            print("Windows detected - manual installation required:")
            print("1. Download Node.js 18 from: https://nodejs.org/en/download/")
            print("2. Run: npm install -g pnpm")
            print("3. Or use winget: winget install OpenJS.NodeJS")
            return False

        # For Linux/macOS systems
        print("Detected Unix-like system, proceeding with automatic installation...")

        # Method 1: Try NVM (Node Version Manager) - preferred method
        print("🚀 Trying NVM (Node Version Manager) installation...")
        if install_nodejs_via_nvm():
            return True

        # Method 2: Fall back to system package managers
        print("📦 Falling back to system package manager installation...")
        return install_nodejs_via_package_manager()

    except Exception as e:
        print(f"Error during setup: {e}")
        return False


def install_nodejs_via_nvm():
    """
    Install Node.js via NVM (Node Version Manager)
    This is the preferred method as it doesn't require system package managers

    Returns:
        bool: True if installation successful, False otherwise
    """
    print("Installing Node.js via NVM...")

    # Check if NVM is already installed - comprehensive check
    nvm_dir = os.path.expanduser("~/.nvm")
    nvm_script = os.path.join(nvm_dir, "nvm.sh")

    # Method 1: Check if NVM directory and script exist
    if os.path.exists(nvm_dir) and os.path.exists(nvm_script):
        print("✓ NVM already installed (found ~/.nvm directory and nvm.sh)")
    else:
        # Method 2: Check if nvm command is available in PATH
        nvm_check = os.system("command -v nvm > /dev/null 2>&1")
        if nvm_check == 0:
            print("✓ NVM already installed (found in PATH)")
        else:
            print("NVM not found, installing...")
            # Install NVM using the official install script
            install_script = "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
            if run_cmd(install_script) != 0:
                print("Failed to install NVM")
                return False

            # Source NVM in current session
            nvm_script_content = """
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
"""
            # Write temporary script to load NVM
            with open("/tmp/load_nvm.sh", "w") as f:
                f.write(nvm_script_content)

            print("✓ NVM installed successfully")

    # Install Node.js 18 using NVM
    print("Installing Node.js 18 via NVM...")
    nvm_install_cmd = """
source ~/.bashrc 2>/dev/null || true
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install 18
nvm use 18
nvm alias default 18
"""

    # Write and execute the NVM install script
    with open("/tmp/nvm_install_node.sh", "w") as f:
        f.write(nvm_install_cmd)

    if run_cmd("bash /tmp/nvm_install_node.sh") != 0:
        print("Failed to install Node.js via NVM")
        return False

    # Verify installation (with NVM environment)
    verify_cmd = """
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node --version && npm --version
"""
    with open("/tmp/verify_node.sh", "w") as f:
        f.write(verify_cmd)

    if run_cmd("bash /tmp/verify_node.sh") != 0:
        print("Node.js installation verification failed")
        return False

    # Install pnpm
    print("Installing pnpm via npm...")
    pnpm_install_cmd = """
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
npm install -g pnpm
"""
    with open("/tmp/install_pnpm.sh", "w") as f:
        f.write(pnpm_install_cmd)

    if run_cmd("bash /tmp/install_pnpm.sh") != 0:
        print("Failed to install pnpm, trying alternative method...")
        # Alternative pnpm installation
        if run_cmd("curl -fsSL https://get.pnpm.io/install.sh | sh -") != 0:
            print("Failed to install pnpm via alternative method")
            return False

    # Clean up temporary files
    for temp_file in [
        "/tmp/load_nvm.sh",
        "/tmp/nvm_install_node.sh",
        "/tmp/verify_node.sh",
        "/tmp/install_pnpm.sh",
    ]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("✅ Node.js 18 and pnpm installed successfully via NVM!")
    print("💡 To use in new terminals, restart your shell or run:")
    print("   source ~/.bashrc")
    print("🎯 NVM allows you to easily switch Node.js versions:")
    print("   nvm install 16    # Install Node.js 16")
    print("   nvm use 16        # Switch to Node.js 16")
    print("   nvm list          # List installed versions")

    return True


def install_nodejs_via_package_manager():
    """
    Install Node.js via system package managers (fallback method)

    Returns:
        bool: True if installation successful, False otherwise
    """
    print("Installing Node.js via system package manager...")

    # Update package manager first
    if os.system("which apt-get > /dev/null 2>&1") == 0:
        # Ubuntu/Debian
        print("Using apt-get package manager...")

        # Update package list
        if run_root_cmd("apt-get update") != 0:
            print("Failed to update package list")
            return False

        # Install curl and ca-certificates if not present
        run_root_cmd("apt-get install -y curl ca-certificates gnupg")

        # Add NodeSource repository
        print("Adding NodeSource repository for Node.js 18...")
        if (
            run_root_cmd("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -")
            != 0
        ):
            print("Failed to add NodeSource repository")
            return False

        # Install Node.js
        if run_root_cmd("apt-get install -y nodejs") != 0:
            print("Failed to install Node.js")
            return False

    elif os.system("which yum > /dev/null 2>&1") == 0:
        # CentOS/RHEL/Fedora
        print("Using yum package manager...")

        # Add NodeSource repository
        print("Adding NodeSource repository for Node.js 18...")
        if (
            run_root_cmd("curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -")
            != 0
        ):
            print("Failed to add NodeSource repository")
            return False

        # Install Node.js
        if run_root_cmd("yum install -y nodejs") != 0:
            print("Failed to install Node.js")
            return False

    elif os.system("which brew > /dev/null 2>&1") == 0:
        # macOS with Homebrew
        print("Using Homebrew package manager...")

        # Install Node.js 18
        if run_cmd("brew install node@18") != 0:
            print("Failed to install Node.js via Homebrew")
            return False

        # Link Node.js 18
        run_cmd("brew link node@18 --force")

    else:
        print("Unsupported package manager. Please install Node.js 18 manually.")
        print("Recommended: Use NVM - https://github.com/nvm-sh/nvm")
        return False

    # Verify Node.js installation
    print("Verifying Node.js installation...")
    node_result = run_cmd("node --version")
    npm_result = run_cmd("npm --version")

    if node_result != 0 or npm_result != 0:
        print("Node.js installation verification failed")
        return False

    # Install pnpm globally
    print("Installing pnpm package manager...")
    if run_cmd("npm install -g pnpm") != 0:
        print("Failed to install pnpm via npm, trying alternative method...")
        # Alternative installation method
        if run_cmd("curl -fsSL https://get.pnpm.io/install.sh | sh -") != 0:
            print("Failed to install pnpm")
            return False

    # Verify pnpm installation
    print("Verifying pnpm installation...")
    # Source bash profile to make pnpm available in current session
    pnpm_check = os.system("pnpm --version > /dev/null 2>&1")
    if pnpm_check != 0:
        print("pnpm installed but may need shell restart to be available")
        print("Run: source ~/.bashrc or restart your terminal")

    # Display versions
    print("Setup completed! Versions installed:")
    run_cmd("node --version")
    run_cmd("npm --version")
    os.system("pnpm --version 2>/dev/null || echo 'pnpm: restart shell to use'")

    print("✅ Node.js 18 and pnpm setup completed successfully!")
    print("💡 Tips:")
    print("   - Use 'pnpm install' instead of 'npm install' for faster installs")
    print("   - Use 'pnpm add <package>' to add dependencies")
    print("   - Use 'pnpm run <script>' to run package.json scripts")

    return True


def get_available_functions():
    """
    Dynamically get all available public functions in this module

    Returns:
        dict: Dictionary of function names and their full documentation
    """
    current_module = sys.modules[__name__]
    functions = {}

    for name, obj in inspect.getmembers(current_module, inspect.isfunction):
        # Skip private functions (starting with _) and imported functions
        if not name.startswith("_") and obj.__module__ == __name__:
            # Get the full docstring
            doc = inspect.getdoc(obj)
            if doc:
                functions[name] = doc
            else:
                functions[name] = "No description available"

    return functions


def print_available_functions():
    """
    Print all available functions with their descriptions
    """
    functions = get_available_functions()
    print("Available functions:")

    # Sort by function name for consistent output
    for name in sorted(functions.keys()):
        full_doc = functions[name]
        # Get first line as summary
        first_line = full_doc.split("\n")[0].strip()
        print(f"- {name}(): {first_line}")

        # Show if more detailed help is available
        if "Args:" in full_doc or "Example:" in full_doc or "Returns:" in full_doc:
            print(f"  (详细信息: help(pyscript_util.{name}))")


def add_usage_to_cursorrule(cursor_file_path: str):
    """
    Add pyscript_util available functions to cursor rule file
    Extracts function information dynamically from docstrings

    Args:
        cursor_file_path (str): Path to the cursor rule file

    Returns:
        bool: True if successfully updated, False otherwise

    Example:
        add_usage_to_cursorrule('.cursorrules')
        add_usage_to_cursorrule('/path/to/your/.cursorrules')
    """
    try:
        print(f"Adding pyscript_util functions to cursor rule: {cursor_file_path}")

        # Get available functions with full documentation
        functions = get_available_functions()

        # Create content to inject
        content_lines = [
            ">>> pyscript_util 辅助库功能",
            "",
            "pyscript_util - Python脚本实用工具库，提供以下功能：",
            "",
        ]

        # Add function descriptions with more detail
        for func_name in sorted(functions.keys()):
            full_doc = functions[func_name]
            # Extract first line as summary
            first_line = full_doc.split("\n")[0].strip()
            content_lines.append(f"- {func_name}(): {first_line}")

            # Add additional info if docstring has examples
            if "Example:" in full_doc or "Args:" in full_doc:
                content_lines.append(
                    f"  详细信息可通过 help(pyscript_util.{func_name}) 查看"
                )

        content_lines.extend(
            [
                "",
                "基本导入方式:",
                "```python",
                "from pyscript_util import *",
                "# 或",
                "import pyscript_util",
                "```",
                "",
                "<<< pyscript_util 辅助库功能",
            ]
        )

        content_to_inject = "\n".join(content_lines)

        # Read existing file
        file_content = ""
        if os.path.exists(cursor_file_path):
            with open(cursor_file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

        # Check if section exists and update or append
        start_marker = ">>> pyscript_util 辅助库功能"
        end_marker = "<<< pyscript_util 辅助库功能"

        if start_marker in file_content and end_marker in file_content:
            # Update existing section
            start_pos = file_content.find(start_marker)
            end_pos = file_content.find(end_marker) + len(end_marker)
            new_content = (
                file_content[:start_pos] + content_to_inject + file_content[end_pos:]
            )
        else:
            # Append new section
            new_content = (
                file_content + ("\n\n" if file_content else "") + content_to_inject
            )

        # Write updated content
        with open(cursor_file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Successfully updated {cursor_file_path}")
        print(f"📝 Added {len(functions)} functions to cursor rule")
        return True

    except Exception as e:
        print(f"Error updating cursor rule file: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print("pyscript_util - Python Script Utilities")
    print_available_functions()
