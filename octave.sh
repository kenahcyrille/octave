#!/usr/bin/bash
#---------------------------------------------------------
# Set the base-dir and source the utilities
TC_HPC_SOFTWARE=${TC_HPC_SOFTWARE:-"$(realpath ${PWD})"}
source $TC_HPC_SOFTWARE/utilities/utils.sh

#---------------------------------------------------------
# TC-HPC build script
#---------------------------------------------------------
# Download URL for Octave
DOWNLOAD_URL='https://ftp.gnu.org/gnu/octave/octave-7.3.0.tar.gz'
# The md5sum of the package
ARCHIVE_MD5='insert_correct_md5_here'
DEPENDENCY_MODULE_LIST=''
# The module help
MODULEFILE_HELP='
GNU Octave is a high-level language, primarily intended for numerical computations. It provides capabilities for the numerical solution of linear and nonlinear problems and for performing other numerical experiments.
'

#---------------------------------------------------------
# The build section
#---------------------------------------------------------
# First and foremost, set the prefixes
set_prefixes

# Next download the tarball and extract it
# This places the extracted sources in $PKG_BUILD_DIR
download_only

# We need to load any dependency modules
load_modules

# Navigate to the build directory
cd $PKG_BUILD_DIR

# Configure, build, and install Octave
./configure --prefix=${PKG_INSTALL_DIR}
make
make install

# This function will create environments based on bin,lib,lib64,inc...
create_lua_modulefile

# Navigate back to the software directory
cd $TC_HPC_SOFTWARE
