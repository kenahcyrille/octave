#!/usr/bin/bash
#---------------------------------------------------------
# set the base-dir and source the utilities
TC_HPC_SOFTWARE=${TC_HPC_SOFTWARE:-"$(realpath ${PWD})"}
source $TC_HPC_SOFTWARE/utilities/utils.sh

#---------------------------------------------------------
# TC-HPC build script
#---------------------------------------------------------
# Download URL for Octave
DOWNLOAD_URL='https://www.cairographics.org/releases/cairo-1.18.4.tar.xz'
# The md5sum of the package
ARCHIVE_MD5='db575fb41bbda127e0147e401f36f8ac'
DEPENDENCY_MODULE_LIST='system-devel/1.0 meson/1.5.2 ninja/1.12.1 python/3.12.1'
# The module help
MODULEFILE_HELP='Cairo is an open-source graphics library that provides a vector graphics-based, device-independent API for software developers.It provides primitives for two-dimensional drawing across a number of different backends'

#---------------------------------------------------------
# The build section
#---------------------------------------------------------
# First and foremost, set the prefixes

set_prefixes

# Next download the tarball and extract it
# This places the extracted sources in $PKG_BUILD_DIR
download_and_extract

# We need to load any dependency modules
load_modules

# Next set the compiler config and flags
set_build_env "GCC_RELEASE"


# mkdir build && cd build
cd ${PKG_BUILD_DIR}/cairo-1.18.4


meson builddir --prefix=$PKG_INSTALL_DIR \

meson setup build --backend=ninja  
#                   -Denbale-xlib=yes  -Denable-xcb=yes
#                   -Dbuildtype=release
#                   -Dlibcairo2-dev=yes -Dlibpixman-1-dev=yes -Dxlib=yes -Dxcb=yes -Dx11=yes


cd builddir
ninja

# compile and install
meson compile
meson build -C 
ninja install -C


# This function will create environments based on bin,lib,lib64,inc...
create_lua_modulefile

# Navigate back to the software directory
cd $TC_HPC_SOFTWARE
rm -rf $PKG_BUILD_DIR
