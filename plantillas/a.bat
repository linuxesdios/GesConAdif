@echo off
setlocal

rem Recorre .docx y excluye los que ya terminan en _obra.docx o _servicio.docx
for /f "delims=" %%F in ('
  dir /b /a:-d *.docx ^| findstr /ri /v "_obra\.docx$" ^| findstr /ri /v "_servicio\.docx$"
') do (
  copy /Y "%%~fF" "%%~dpnF_obra%%~xF" >nul
  copy /Y "%%~fF" "%%~dpnF_servicio%%~xF" >nul
  echo Duplicado: %%~nxF -> %%~nF_obra%%~xF y %%~nF_servicio%%~xF
)

echo Listo.
endlocal
