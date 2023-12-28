@echo off
title DynoBOT

where python
IF %ERRORLEVEL% NEQ 0 (
  cls
  echo Necesitas instalar python
  echo https://www.python.org/downloads/
  echo.
  pause
  exit
)

python index.py

pause
exit
