@echo off
rem Klont das 3D-Repo nach C:\Users\Johann\harmonika\harmonika-3d (einmalig), danach nur noch "git pull"
cd /d "%~dp0"
if exist harmonika-3d\.git (
  cd harmonika-3d
  git pull
) else (
  git clone https://github.com/jpascher/harmonika-3d.git
)
pause
