
# CiefpTvProgram – EPG Viewer Plugin
- **Version: 1.0
- **Author: Ciefp
- **Platform: Enigma2 (Linux STB)


![Bouquet](https://github.com/ciefp/CiefpTvProgram/blob/main/ciefptvprogram.jpg)

# Description:
- **CiefpTvProgram is a simple and functional Enigma2 plugin that allows you to browse the Electronic Program Guide (EPG) for a list of selected TV channels. 
- **The channel list is displayed on the left, and detailed EPG information appears on the right, including show titles, start times, and descriptions.

# Features:
- **Displays a customizable list of TV channels (CHANNEL_LIST_DATA).
- **Automatically downloads and parses EPG XML files from TVProfil.net.
- **Shows channel picons for the currently selected channel.
- **Displays plugin logo and additional background graphics.
- **Switches between channel view and EPG view (OK button).
- **Supports scrolling through both channel list and EPG data (up/down arrows).

# Usage:
- **Launching the plugin:
- **The plugin can be accessed via the Plugin Menu or the Extensions Menu on your Enigma2 device.

# Navigation:
- **Up/Down: Navigate through the channel list or EPG entries.
- **OK: Switches focus between the channel list and the EPG content view.
- **EXIT: Closes the plugin.

# Automatic EPG download:
- **On first launch, the plugin downloads EPG data and saves it to /tmp/CiefpTvProgram/.


# ..:: CiefpSettings ::..

# TV Program v1.3

# Explanation of changes
1.Adding a constant for the last update file:
- LAST_UPDATE_FILE = os.path.join(EPG_DIR, "last_update.txt")
is defined to store the date of the last update in the file /tmp/CiefpTvProgram/last_update.txt.

2.New method checkLastUpdate:
- This method checks for the existence of the file last_update.txt.
- If the file does not exist, it returns True (starts the update).
- If the file exists, it reads the date from the file, compares it with the current date and returns True
if 2 or more days have passed since the last update.

3.New method updateLastUpdateFile:
- Deletes the old last_update.txt file if it exists.
- Creates a new file with the current date in the format YYYY-MM-DD (e.g. 2025-06-30) after a successful EPG update.

4.Modification of the downloadAndParseEPG method:
- If no update is needed (the file last_update.txt exists and is less than 2 days old), it loads the cached EPG files from /tmp/CiefpTvProgram/ and parses them.
- If an update is needed, it downloads new EPG files, decompiles them, parses them and finally updates last_update.txt by calling updateLastUpdateFile.

# ..:: CiefpSettings ::..