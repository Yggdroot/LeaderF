#!/usr/bin/env bash

cd "$(dirname "$0")"
PYTHON2_EXEC=$(command -v python2)
PYTHON3_EXEC=$(command -v python3)

if [ "$1" == "--reverse" ]
then
    cd autoload/leaderf/fuzzyMatch_C
    rm -rf build
    rm -f ../python/*.so
    echo "C extension uninstalled sucessfully!"
    exit 0
fi

cd autoload/leaderf/fuzzyMatch_C

if [ -x "$PYTHON2_EXEC" ] ; then
    echo "Begin to compile C extension of Python2 ..."
    $PYTHON2_EXEC setup.py build
    if (( $? == 0 ))
    then
        cp build/lib*2.?/fuzzyMatchC*.so ../python
        if (( $? == 0 ))
        then
            echo
            echo C extension of Python2 installed sucessfully!
        fi
    fi
fi

if [ -x "$PYTHON3_EXEC" ] ; then
    echo
    echo "Begin to compile C extension of Python3 ..."
    $PYTHON3_EXEC setup.py build
    if (( $? == 0 ))
    then
        cp build/lib*3.?/fuzzyMatchC*.so ../python
        if (( $? == 0 ))
        then
            echo
            echo C extension of Python3 installed sucessfully!
        fi
    fi
fi
