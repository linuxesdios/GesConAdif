@echo off
setlocal enabledelayedexpansion

rem Archivo de salida
set "output_file=python_lineas_filtradas.txt"

rem Eliminar archivo anterior
if exist "%output_file%" del "%output_file%"

echo Extrayendo lineas con: class, archivo:, def, from, import
echo.

set /a count=0
set /a total_lines=0

rem Recorrer archivos .py
for /r %%f in (*.py) do (
    set /a count+=1
    echo Procesando: %%f

    rem Encabezado del archivo procesado
    echo. >> "%output_file%"
    echo ================================== >> "%output_file%"
    echo ARCHIVO: %%f >> "%output_file%"
    echo ================================== >> "%output_file%"
    echo. >> "%output_file%"

    rem Buscar y escribir solo las líneas que contengan las palabras clave específicas
    rem /I = ignorar mayúsculas/minúsculas, /N = mostrar número de línea
    for /f "delims=" %%i in ('findstr /I /N "class " "%%f" 2^>nul') do (
        echo %%i >> "%output_file%"
        set /a total_lines+=1
    )
    
    for /f "delims=" %%i in ('findstr /I /N "archivo: " "%%f" 2^>nul') do (
        echo %%i >> "%output_file%"
        set /a total_lines+=1
    )
    
    for /f "delims=" %%i in ('findstr /I /N "def " "%%f" 2^>nul') do (
        echo %%i >> "%output_file%"
        set /a total_lines+=1
    )
    
    for /f "delims=" %%i in ('findstr /I /N "from " "%%f" 2^>nul') do (
        echo %%i >> "%output_file%"
        set /a total_lines+=1
    )
    
    for /f "delims=" %%i in ('findstr /I /N "import " "%%f" 2^>nul') do (
        echo %%i >> "%output_file%"
        set /a total_lines+=1
    )

    rem Separación entre archivos
    echo. >> "%output_file%"
    echo ---------------------------------------- >> "%output_file%"
    echo. >> "%output_file%"
)

echo.
echo Proceso completado.
echo Se procesaron %count% archivos .py
echo Se extrajeron %total_lines% lineas filtradas
echo Resultado guardado en: %output_file%
echo.
pause