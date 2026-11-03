@echo off
chcp 65001 >nul
title DS Quest - setup
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
if errorlevel 1 pause
