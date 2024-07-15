#!/bin/bash

# Define the default path for the virtual environment
venv_path="$(pwd)/my_venv"

# Function to create a virtual environment
create_venv() {
    if python3 -m venv "$venv_path"; then
        echo "Virtual environment created at $venv_path"
    else
        echo "Failed to create virtual environment"
        exit 1
    fi
}

# Function to configure libpython
configure_libpython() {
    # Path to the site-packages directory of the virtual environment
    site_packages="$venv_path/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"
    
    # Get the path and name of the main Python's libpython library
    libpython_path=$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')
    libpython_name=$(python3 -c 'import sysconfig; print(sysconfig.get_config_var("LDLIBRARY"))')

    if [ -z "$libpython_path" ] || [ -z "$libpython_name" ]; then
        echo "Could not find libpython path or name. Ensure Python development files are installed."
        exit 1
    fi
    
    libpython_full_path="$libpython_path/$libpython_name"
    
    # Ensure the site-packages directory exists
    mkdir -p "$site_packages"
    
    # Create a symbolic link to the libpython in the site-packages directory of the virtual environment
    symlink_path="$site_packages/$libpython_name"
    if [ ! -e "$symlink_path" ]; then
        ln -s "$libpython_full_path" "$symlink_path"
        echo "Symbolic link created at $symlink_path pointing to $libpython_full_path"
    else
        echo "Symbolic link already exists at $symlink_path"
    fi
}

# Main script execution
create_venv
configure_libpython
