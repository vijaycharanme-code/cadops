@echo off
echo Starting CADMind Studio...
start /b python backend-sim\server.py 8000
cd frontend
npm run preview -- --port 1420
