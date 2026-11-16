@echo off
cd /d "%~dp0"
docker compose -f compose.try.yaml -f compose.autocloud.yaml up -d
pause
