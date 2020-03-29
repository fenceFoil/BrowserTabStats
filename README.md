## BrowserTabArchiver

![Banner](TabArchiver.png)

Saves a time-series database of all the tabs you leave open in your Firefox browser from recovery.jsonlz4 into SQLite.

Logs errors, and optionally pushes notifications to your phone using the awesome and dockerized server app [Gotify](https://gotify.net/) so that you can correct issues with minimal archiving disruption. (Supply your gotify address and a new app key).

### How to extend for Chrome

Someday I know I'll switch back for some reason!

The following 4 files are simliar to recovery.jsonlz4:

* Current Tabs
* Current Session
* Last Tabs
* Last Session

They can be parsed using a project called Chromegnon which runs in Python 2.7.

```
git clone https://github.com/JRBANCEL/Chromagnon.git
git checkout origin/SNSS
C:\Python27\python.exe chromagnonSession.py "Last Session"
```

... this prints the restore session commands to the console. There is also programmatic access to build into this project in the future if wanted.

### Installation

Tested with Python 3.7

*Optionally: set up and activate a venv named BrowserTabArchiverVenv inside the /BrowserTabArchiver/ folder of this repo. Then you can call runBrowserTabArchiver.bat from a scheduled task on Windows every day.*

At a command line:

```
pip install requirements.txt
```

Fill out `configTemplate.json` with the appropriate values and save as `config.json`. (If on windows, replace backslashes with slashes, \ changes to /).

Run using `python archiveBrowswerTabs.py`

### Database Scheme

In file BrowserTabArchive.db

TABLE: ArchivedTabs

* snapshotID
  * generate this UUID each time you check the profile
* title
  * /windows[#]/tabs[#]/entries[0]/title
* url
  * /windows[#]/tabs[#]/entries[0]/url
* tabID
  * /windows[#]/tabs[#]/entries[0]/ID
* tabWindow 
  * (starts at 0)
  * /windows[THIS]
* tabIndex
  * (starts at 0)
  * /windows[#]/tabs[THIS]
* lastAccessed
    * /windows[#]/tabs[#]/lastAccessed

TABLE: ArchiveSnapshots

* snapshotID
* snapshotTime
  * From the current system clock in UNIX time
* numWindows
* numTabs
* numTabsInLargestWindow
* sessionUpdatedTime
    * CHECK /session/lastUpdate to ensure that this file is being updated as expected
    * send issues to gotify

## Credits

This project licensed under the MIT License. See LICENSE.txt

mozlz4a.py (Mozilla session file extraction tool) provided under the BSD 2-clause license. Modified import on line 33. https://gist.github.com/Tblue/62ff47bef7f894e92ed5

New Tab Icon from IconsMind at iconsmind.com, https://iconsmind.com/classic-license/ (attribution required for free use, link to website https://iconsmind.com)