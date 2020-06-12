#!/bin/sh
VERSION="@VERSION@"
if [[ $VERSION != "@VERSION@" ]]
then
    echo $VERSION
else
    git describe --tags | sed 's/\([^-]*-g\)/r\1/;s/-/./g'
fi

