#!/usr/bin/env bash

set -euo pipefail
shopt -s globstar

source .dbi.conf

for d in core compiled mpi compilers
do
    for p in $(ls $d/**/*.sh)
    do
        a=${p%*.sh}
        if [ ! -d "$ALL_PACKAGES_INSTALL_PREFIX/$a" ]; then
            echo "$a"
        fi
    done
done
