@echo off
if /i "%1" equ "--reverse" (
    cd autoload\leaderf\fuzzyMatch_C
    rd /s /q build
    cd ..\python
    del *.pyd
    echo ======================================
    echo  C extension uninstalled sucessfully!
    echo ======================================
    goto end
)
echo Begin to compile C extension of Python2 ...
cd autoload\leaderf\fuzzyMatch_C
py -2 setup.py build
if %errorlevel% neq 0 goto second
pushd build\lib*2.?
xcopy /y *.pyd ..\..\..\python\
if %errorlevel% equ 0 (
    echo=
    echo ===============================================
    echo  C extension of Python2 installed sucessfully!
    echo ===============================================
)
popd

:second
echo=
echo Begin to compile C extension of Python3 ...
py -3 setup.py build
if %errorlevel% neq 0 goto end
pushd build\lib*3.?
xcopy /y *.pyd ..\..\..\python\
if %errorlevel% equ 0 (
    echo=
    echo ===============================================
    echo  C extension of Python3 installed sucessfully!
    echo ===============================================
)
popd

:end
