@echo off
REM VIF Trading System - Autonomous Scheduler Launcher
REM Place this file in Windows Startup folder for boot-time scheduling
REM No admin rights required

cd /d C:\Users\marti\vif-trading-system
start "VIF Scheduler" /min python schedule_daily.py
