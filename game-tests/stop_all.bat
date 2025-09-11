@echo off
echo Pythonプロセスを停止中...
taskkill /IM python.exe /F 2>nul
echo Chromeプロセスを停止中...
taskkill /IM chrome.exe /F 2>nul
echo 完了！
pause