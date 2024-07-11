import os
import subprocess
import sys
import sysconfig

def create_venv(venv_path):
    # Create the virtual environment
    subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
    print(f"Virtual environment created at {venv_path}")

def configure_libpython(venv_path):
    try:
        # Path to the site-packages directory of the virtual environment
        site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
        
        # Get the path and name of the main Python's libpython library
        libpython_path = sysconfig.get_config_var("LIBDIR")
        libpython_name = sysconfig.get_config_var("LDLIBRARY")
        libpython_full_path = os.path.join(libpython_path, libpython_name)
        
        # Ensure the site-packages directory exists
        if not os.path.exists(site_packages):
            os.makedirs(site_packages)
        
        # Create a symbolic link to the libpython in the site-packages directory of the virtual environment
        symlink_path = os.path.join(site_packages, libpython_name)
        if not os.path.exists(symlink_path):
            os.symlink(libpython_full_path, symlink_path)
            print(f"Symbolic link created at {symlink_path} pointing to {libpython_full_path}")
        else:
            print(f"Symbolic link already exists at {symlink_path}")
    except Exception as e:
        print(f"An error occurred while configuring libpython: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_venv.py <path_to_virtual_env>")
        sys.exit(1)

    venv_path = sys.argv[1]

    create_venv(venv_path)
    configure_libpython(venv_path)

if __name__ == "__main__":
    main()
