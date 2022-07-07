#!/usr/bin/env bash

if [ "$1" = "--reverse" ]
then
    cd autoload/leaderf/fuzzyMatch_C
    rm -rf build
    rm -f ../python/*.so ../python/*.dll
    echo ========================================
    echo ^_^ C extension uninstalled sucessfully!
    echo ========================================
    exit 0
fi

no_python=true

cd autoload/leaderf/fuzzyMatch_C

if command -v python2 > /dev/null 2>&1; then
    no_python=false
    echo "Begin to compile C extension of Python2 ..."
    python2 setup.py build --build-lib ../python
    if [ $? -eq 0 ]
    then
        echo
        echo =================================================
        echo ^_^ C extension of Python2 installed sucessfully!
        echo =================================================
    fi
fi

if command -v python3 > /dev/null 2>&1; then
    $no_python || echo
    no_python=false

    echo "Begin to compile C extension of Python3 ..."
    python3 setup.py build --build-lib ../python
    if [ $? -eq 0 ]
    then
        echo
        echo =================================================
        echo ^_^ C extension of Python3 installed sucessfully!
        echo =================================================
    fi
fi

if $no_python; then
    echo "Can't compile C extension, please install Python2 or Python3" >&2
    exit 1
fi
