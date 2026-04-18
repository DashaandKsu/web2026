@echo off
cd /d "%~dp0app"
set FLASK_APP=app
echo Starting Flask...
echo Open: http://127.0.0.1:5000/
echo Post: http://127.0.0.1:5000/posts/0
echo.
python -m flask run
