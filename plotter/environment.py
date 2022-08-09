from pathlib import Path
import os, sys

_local_source_paths = [ 
    # path to ESP8266 side implementation - needed to import measurement handling modules
    "../sources",

    # path to Measurement Manager application directory - used to plot data
    "../external/measurement_manager/app"
]

def get_directory_path(file : str = __file__):
    """Returns directory path of given file (this file used if no arguments)"""
    return Path(os.path.dirname(os.path.realpath(file)))

def add_internal_sources_to_path():
    """Adds internal source directories to Python's path, to allow importing the modules."""
    dir_path = get_directory_path()

    for path in _local_source_paths:
        abs_path = os.path.realpath(dir_path / path)
        sys.path.append(abs_path)

    # also append internal sources for Measurement Manager
    from managerHelpers import addInternalFoldersToPath
    addInternalFoldersToPath()
