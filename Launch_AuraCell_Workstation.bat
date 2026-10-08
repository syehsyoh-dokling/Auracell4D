@echo off
title AuraCell 4D - GUI (local server)
echo ======================================================================
echo    AuraCell 4D - Physics-gated lineage tracking (GUI + local API)
echo    Serving http://127.0.0.1:8765  -  Ctrl+C to stop
echo ======================================================================
cd /d "%~dp0"
python gui\launch_gui.py
pause
