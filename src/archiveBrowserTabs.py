import datetime
import json
import logging
from logging import debug, info, warning, error, critical
import os
from shutil import copyfile
import sqlite3
import sys
import time
import uuid

import mozlz4a
from gotifyLoggingHandler import GotifyHandler

if __name__ == "__main__":
    logFormat = "[%(levelname)s] %(asctime)s: %(message)s"
    logFormatter = logging.Formatter(logFormat)

    # Log to a file and to the error stream
    logging.basicConfig(filename='data/archiveBrowserTabsLog.txt', level=logging.DEBUG, format=logFormat)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)
    streamHandler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(streamHandler)

    try:
        info ('Loading config from config.json...')
        config = {}
        with open('data/config.json') as f:
            config = json.load(f)

        # Setup gotify error logging
        if 'logging' in config:
            if 'gotify' in config['logging'] and config['logging']['gotify']['enabled']:
                gotifyHandler = GotifyHandler(config['logging']['gotify']['address'], config['logging']['gotify']['apiKey'], config['logging']['gotify']['priority'])
                gotifyHandler.setLevel(logging.WARNING)
                gotifyHandler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
                logging.getLogger().addHandler(gotifyHandler)

                # Test gotify error logging
                if not os.path.isfile('data/gotifyWasTested'):
                    warning("New gotify logger set up. This is a test message.")
                    open('data/gotifyWasTested', 'a').close()

        info ("=== Beginning Tab Data Archiving ===")

        # Decompress Firefox tab data
        info ('Copying tab recovery data from {}...'.format(config['restoreSessionLocation']))
        if not os.path.isfile(config['restoreSessionLocation']):
            error('The Firefox tab session restore file was not found! Tried {}'.format(config['restoreSessionLocation']))
            sys.exit(1)
        copyfile(config['restoreSessionLocation'], 'data/recovery.jsonlz4')
        info ('Decompressing tab data...')
        tabJSON = None
        with open('data/recovery.jsonlz4', 'rb') as f:
            tabJSON = mozlz4a.decompress(f)

        # Import Firefox tab data
        info ('Loading decompressed tab data...')
        tabData = json.loads(tabJSON)

        # Create database if it does not already exist
        if not os.path.isfile('data/tabArchive.db'):
            warning('tabArchive.db not found, creating new db...')
            conn = sqlite3.connect('data/tabArchive.db')
            conn.execute('''CREATE TABLE ArchiveSnapshots (
                snapshotID TEXT, 
                snapshotTime INTEGER, 
                numWindows INTEGER, 
                numTabs INTEGER, 
                numTabsInLargestWindow INTEGER, 
                sessionUpdatedTime INTEGER
            )''')
            conn.execute('''CREATE TABLE ArchivedTabs (
                snapshotID TEXT,
                title TEXT,
                url TEXT,
                tabID INTEGER,
                tabWindow INTEGER,
                tabIndex INTEGER,
                lastAccessed INTEGER
            )''')
            conn.commit()
            conn.close()

        # Open database
        info("Opening tab archive database...")
        conn = sqlite3.connect('data/tabArchive.db')

        # Write tab data into database
        info("Writing tab snapshot...")

        # Write snapshot info
        snapshotID = str(uuid.uuid4())
        windowTabCounts = [len(window['tabs']) for window in tabData['windows']]
        sessionUpdatedTime = tabData['session']['lastUpdate']
        snapshotInfo = (
            snapshotID,
            int(time.time()),
            len(tabData['windows']),
            sum(windowTabCounts),
            max(windowTabCounts),
            sessionUpdatedTime
        )
        conn.execute("INSERT INTO ArchiveSnapshots VALUES (?,?,?,?,?,?)", snapshotInfo)

        if config['saveTabURLs']:
            # Write tab info
            info("Saving URLs of each open tab")
            currWindow = -1
            currTab = -1
            try:
                #temp = []
                for windowNum, windowData in enumerate(tabData['windows']):
                    for tabNum, tabData in enumerate(windowData['tabs']):
                        currWindow = windowNum # note debug info
                        currTab = tabNum # note debug info

                        #temp.append(len(tabData['entries']))

                        title = None
                        url = None
                        tabID = None
                        if 'entries' in tabData and len(tabData['entries']) > 0:
                            currEntryIndex = tabData['index'] - 1
                            if currEntryIndex < 0:
                                # Indicates that the user hasn't navigated anywhere yet on this tab.
                                # Weird.
                                pass
                            elif currEntryIndex == 0 and len(tabData['entries']) <= 0:
                                # Indicates that the user hasn't navigated anywhere yet on this tab.
                                # Weird.
                                pass
                            elif currEntryIndex >= 1 and currEntryIndex >= len(tabData['entries']):
                                # Edge case: tab index points beyond end of list of entries!!!!
                                warning("Tab index beyond end of tab entries: len entries = {}, index = {}, tabNum = {}, windowNum = {}".format(len(tabData['entries']), currEntryIndex, tabNum, windowNum))
                            else:
                                currEntry = tabData['entries'][currEntryIndex]
                                title = currEntry['title']
                                url = currEntry['url']
                                tabID = currEntry['ID']

                        tabInfo = (
                            snapshotID,
                            title,
                            url,
                            tabID,
                            windowNum,
                            tabNum,
                            tabData['lastAccessed']
                        )
                        conn.execute("INSERT INTO ArchivedTabs VALUES (?,?,?,?,?,?,?)", tabInfo)
                #import statistics
                #debug("len {}, mean {}, median {}, mode {}, range {}, min {}, max {}".format(len(temp), statistics.mean(temp), statistics.median(temp), statistics.mode(temp), max(temp) - min(temp), min(temp), max(temp)))
                #debug("indexes of 0 entries: {}".format([ i for i in range(len(temp)) if temp[i] == 0 ]))
            except Exception as e:
                logging.exception("Uncaught exception while archiving tabs (iterating through specific tab info: window {}, tab {}). Snapshot not archived.".format(currWindow, currTab))
        else:
            info('NOT saving URLs of each open tab (as set by "saveTabURLs":false in config.json')

        # Commit new data into database
        info("Committing new tab archive snapshot into database...")
        conn.commit()
        conn.close()

        # Clean up
        for tempFile in ['data/recovery.jsonlz4']:
            os.remove(tempFile)

        # Announce a warning if the tab session looks stale
        sessionUpdatedDateTime = datetime.datetime.fromtimestamp(sessionUpdatedTime/1000)
        sessionUpdatedAge = datetime.datetime.now() - sessionUpdatedDateTime
        info("Firefox tab session file was last updated {}, {} ago.".format(sessionUpdatedDateTime.strftime('%c'), sessionUpdatedAge))
        if sessionUpdatedAge.days > 7:
            warning("Firefox tab session file stale: {} last updated {} days ago.".format(config['restoreSessionLocation'], sessionUpdatedAge.days))

        info("=== Tab archive completed! ===")

    except Exception as e:
        logging.exception("Uncaught exception while archiving tabs. Snapshot not archived.")