#!/usr/bin/env bash

set -euo pipefail
shopt -s globstar

source .dbi.conf

get_missing_build_list() {
    missing_builds=()

    for d in core compiled mpi compilers
    do
        for p in $(ls $d/**/*.sh)
        do
            a=${p%*.sh}
            if [ ! -d "$ALL_PACKAGES_INSTALL_PREFIX/$a" ]; then
                missing_builds+=("$a")
            fi
        done
    done

    echo "${missing_builds[@]}"
}

get_missing_build_list
