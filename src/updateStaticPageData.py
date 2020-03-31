import sqlite3
import time

if __name__ == "__main__":
    # Query sqllite for most recent timeseries data
    conn = sqlite3.connect('data/tabArchive.db')
    c = conn.cursor()
    timestamps, tabsOpen = map(list,zip(*[(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)), numTabs) for t, numTabs in conn.execute('SELECT snapshotTime,numTabs FROM ArchiveSnapshots ORDER BY snapshotTime ASC')]))
    conn.close()

    # Write results of query to javascript file
    with open('staticPageOut/open-tabs-data.js', 'w') as f:
        # Output timeseries data as multiple arrays correlated by index.
        # date format must be YYYY-MM-DD HH:MM:SS
        f.writelines([
            'openTabsDataTimestamps={};\n'.format(timestamps),
            'openTabsCount={};\n'.format(tabsOpen)
        ])