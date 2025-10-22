@echo off
REM ========================================
REM Acceso directo al Administrador de DB
REM ========================================

setlocal
REM Ir al directorio del script y luego a db_admin (independiente del CWD)
pushd "%~dp0db_admin" 2>nul
if errorlevel 1 (
	echo [ERROR] No se encontro la carpeta db_admin relativa a este archivo.
	echo Ruta esperada: %~dp0db_admin
	exit /b 1
)

python admin_db.py %*

popd
endlocal
