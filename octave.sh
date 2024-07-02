#!/usr/bin/bash
#---------------------------------------------------------
# Set the base-dir and source the utilities
TC_HPC_SOFTWARE=${TC_HPC_SOFTWARE:-"$(realpath ${PWD})"}
source $TC_HPC_SOFTWARE/utilities/utils.sh

#---------------------------------------------------------
# TC-HPC build script
#---------------------------------------------------------
# download URL
DOWNLOAD_URL='https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda_12.2.0_535.54.03_linux.run'
# the md5sum of the package
ARCHIVE_MD5='72aefb16c35ecb91074b85c27fa26e46'
DEPENDENCY_MODULE_LIST=''
# The module help
MODULEFILE_HELP='
The NVIDIA® CUDA® Toolkit provides a development environment for creating high-performance, GPU-accelerated applications.
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

# copy untarred directory to installed directory
# For only one directory extracted in build dir, use "*/" so no folder name change
bash ${ARCHIVE_PATH} --silent --toolkit --installpath=${PKG_INSTALL_DIR}

# this function will create environments based on bin,lib,lib64,inc...
create_lua_modulefile

cd $TC_HPC_SOFTWARE
