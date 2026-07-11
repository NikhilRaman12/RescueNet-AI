@echo off
cd /d "c:\Users\Nikhil Raman K\RescueNet-AI"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010 --reload
