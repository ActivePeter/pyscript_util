#!/usr/bin/env python3
"""
pyscript_util - Python script utilities for maximum compatibility
"""

from .pyscript_util import (
    run_cmd,
    run_root_cmd,
    run_cmd_sure,
    run_root_cmd_sure,
    chdir_to_cur_file,
    setup_script_environment,
    find_file_upwards,
    setup_npm,
    get_available_functions,
    print_available_functions,
    stage,
    add_usage_to_cursorrule,
)

__version__ = "0.1.0"
__all__ = [
    "run_cmd",
    "run_root_cmd",
    "run_cmd_sure",
    "run_root_cmd_sure",
    "chdir_to_cur_file",
    "setup_script_environment",
    "find_file_upwards",
    "setup_npm",
    "get_available_functions",
    "print_available_functions",
    "stage",
    "add_usage_to_cursorrule",
]
