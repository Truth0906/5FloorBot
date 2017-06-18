@echo off
pyinstaller.exe -y --onefile 5FloorBot.spec
if exist "5FloorBotOption.txt" (
	copy "5FloorBotOption.txt" .\dist\5FloorBot
)