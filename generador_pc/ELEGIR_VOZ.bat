@echo off
REM Elige el mejor tramo de ENTRENAR_VOZ como referencia de voz y genera 3 pruebas.
REM Uso: doble clic  (o "ELEGIR_VOZ.bat 2" para usar la opcion 2)
set OPC=%1
if "%OPC%"=="" set OPC=1
cd /d "%~dp0"
if exist "D:\HistoriasIA\venv_voz\Scripts\python.exe" (
  "D:\HistoriasIA\venv_voz\Scripts\python.exe" "%~dp0elegir_voz.py" --opcion %OPC%
) else (
  echo No encuentro D:\HistoriasIA\venv_voz. Corre primero el generador para que instale Chatterbox.
)
pause
