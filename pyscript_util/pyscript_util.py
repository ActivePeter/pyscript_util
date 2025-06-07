#!/usr/bin/env python3
"""
pyscript_util - Python script utilities for maximum compatibility
Provides command execution and directory management functions using os.system
"""

import os
import sys


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
    sudo_command = f"sudo {command}"
    print(f"Executing root command: {sudo_command}")
    result = os.system(sudo_command)
    print(f"Root command completed with exit code: {result}")
    return result


def run_cmd_sure(command):
    """
    Execute a command and ensure it succeeds (exit on failure)
    
    Args:
        command (str): The command to execute
        
    Returns:
        int: Always returns 0 (success) or exits the program
    """
    print(f"Executing command (sure): {command}")
    result = os.system(command)
    if result != 0:
        print(f"Command failed with exit code: {result}")
        print(f"Failed command: {command}")
        sys.exit(result)
    print(f"Command completed successfully")
    return result


def run_root_cmd_sure(command):
    """
    Execute a command with sudo privileges and ensure it succeeds (exit on failure)
    
    Args:
        command (str): The command to execute with sudo
        
    Returns:
        int: Always returns 0 (success) or exits the program
    """
    sudo_command = f"sudo {command}"
    print(f"Executing root command (sure): {sudo_command}")
    result = os.system(sudo_command)
    if result != 0:
        print(f"Root command failed with exit code: {result}")
        print(f"Failed command: {sudo_command}")
        sys.exit(result)
    print(f"Root command completed successfully")
    return result


def chdir_to_cur_file():
    """
    Change the current working directory to the directory containing the current script
    
    This function should be called from the main script to ensure all relative paths
    are resolved relative to the script's location.
    
    Returns:
        str: The new current working directory
    """
    # Get the directory of the calling script
    frame = sys._getframe(1)
    caller_file = frame.f_globals.get('__file__')
    
    if caller_file is None:
        print("Warning: Could not determine caller file, using current __file__")
        caller_file = __file__
    
    script_dir = os.path.dirname(os.path.abspath(caller_file))
    print(f"Changing directory to: {script_dir}")
    os.chdir(script_dir)
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    return current_dir


if __name__ == "__main__":
    # Example usage
    print("pyscript_util - Python Script Utilities")
    print("Available functions:")
    print("- run_cmd(command): Execute command with logging")
    print("- run_root_cmd(command): Execute command with sudo")
    print("- run_cmd_sure(command): Execute command and exit on failure")
    print("- run_root_cmd_sure(command): Execute sudo command and exit on failure")
    print("- chdir_to_cur_file(): Change to script's directory")
    print("- setup_script_environment(): Alias for chdir_to_cur_file()")
    
    # Demonstrate chdir_to_cur_file
    print("\nDemonstrating chdir_to_cur_file():")
    chdir_to_cur_file() 