rem Entry point for this solution! Run on a cron job daily or hourly or on whatever schedule you prefer.
call BrowserTabArchiverVenv/Scripts/activate.bat
python archiveBrowserTabs.py
call deployNewData.bat