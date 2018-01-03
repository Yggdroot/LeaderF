@echo off
if /i "%1" equ "--reverse" (
    cd autoload\leaderf\fuzzyMatch_C
    rd /s /q build
    cd ..\python
    del *.pyd
    echo C extension uninstalled sucessfully!
    goto end
)
echo Begin to compile C extension of Python2 ...
cd autoload\leaderf\fuzzyMatch_C
py -2 setup.py build --compiler=mingw32
if %errorlevel% neq 0 goto second
pushd build\lib*2.?
xcopy /y fuzzyMatchC*.pyd ..\..\..\python\
if %errorlevel% equ 0 (
    echo=
    echo C extension of Python2 installed sucessfully!
)
popd

:second
echo=
echo Begin to compile C extension of Python3 ...
py -3 setup.py build
if %errorlevel% neq 0 goto end
pushd build\lib*3.?
xcopy /y fuzzyMatchC*.pyd ..\..\..\python\
if %errorlevel% equ 0 (
    echo=
    echo C extension of Python3 installed sucessfully!
)
popd

:end
