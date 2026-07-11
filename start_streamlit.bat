@echo off
cd /d "%~dp0"
.venv\Scripts\python -m streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1
