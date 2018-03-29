#!/usr/bin/env bash

if [ "$1" = "--reverse" ]
then
    cd autoload/leaderf/fuzzyMatch_C
    rm -rf build
    rm -f ../python/*.so
    echo "C extension uninstalled sucessfully!"
    exit 0
fi

cd autoload/leaderf/fuzzyMatch_C
echo "Begin to compile C extension of Python2 ..."
python setup.py build
if [ $? -eq 0 ]
then
    cp build/lib*2.?/fuzzyMatchC*.so ../python
    if [ $? -eq 0 ]
    then
        echo
        echo C extension of Python2 installed sucessfully!
    fi
fi

echo
echo "Begin to compile C extension of Python3 ..."
python3 setup.py build
if [ $? -eq 0 ]
then
    cp build/lib*3.?/fuzzyMatchC*.so ../python
    if [ $? -eq 0 ]
    then
        echo
        echo C extension of Python3 installed sucessfully!
    fi
fi
