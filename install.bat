@echo off
set pyFlag=0
where /Q py
if %ERRORLEVEL% NEQ 0 set pyFlag=1

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
echo Beginning to compile C extension of Python2 ...
cd autoload\leaderf\fuzzyMatch_C

if %pyFlag% EQU 0 (
    py -2 setup.py build --build-lib ..\python
) else (
    python2 setup.py build --build-lib ..\python
)
if %errorlevel% equ 0 (
    echo=
    echo ===============================================
    echo  C extension of Python2 installed sucessfully!
    echo ===============================================
)

echo=
echo Beginning to compile C extension of Python3 ...
if %pyFlag% EQU 0 (
    py -3 setup.py build --build-lib ..\python
) else (
    python3 setup.py build --build-lib ..\python
)
if %errorlevel% equ 0 (
    echo=
    echo ===============================================
    echo  C extension of Python3 installed sucessfully!
    echo ===============================================
)

:end
