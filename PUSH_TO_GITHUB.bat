@echo off
title Push Updates to GitHub (Roadside App)
cd /d "%~dp0"
echo =======================================================
echo PUSHING LATEST UPDATES TO GITHUB & RENDER...
echo =======================================================
echo.
"C:\Users\HP\AppData\Local\GitHubDesktop\app-3.6.2\resources\app\git\cmd\git.exe" push origin main
echo.
echo =======================================================
echo DONE! Render will automatically deploy in ~30 seconds.
echo Check your live app: https://roadside-app.onrender.com
echo =======================================================
pause
