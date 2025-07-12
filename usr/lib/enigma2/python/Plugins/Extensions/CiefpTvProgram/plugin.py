from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Tools.LoadPixmap import LoadPixmap
import sys
import platform
import os
import gzip
import urllib.request
import xml.etree.ElementTree as ET
import datetime
import time
import io
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ciefp_tvprogram.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Diagnostic logging for Python environment
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Platform: {platform.platform()}")

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpTvProgram/"
PICON_PATH = os.path.join(PLUGIN_PATH, "picon/")  # Picon directory
PLACEHOLDER_PICON = os.path.join(PICON_PATH, "placeholder.png")  # Placeholder picon
EPG_DIR = "/tmp/CiefpTvProgram"  # EPG storage directory
EPGIMPORT_FILE = "/etc/epgimport/rytecSRB_Basic.xml"
LAST_UPDATE_FILE = os.path.join(EPG_DIR, "last_update.txt")  # File to track last update

# Channel list based on lista.txt (no service references needed)
CHANNEL_LIST_DATA = [
    "RTS1",
    "RTS2",
    "B92",
    "Prva",
    "Pink",
    "Nova S",
    "HTV1",
    "HTV2",
    "HTV3",
    "HTV4",
    "Nova TV",
    "RTL",
    "RTL2",
    "Doma TV",
    "Plava TV",
    "Vinkovačka TV",
    "TV Zapad",
    "SLO1",
    "SLO2",
    "SLO3",
    "Nova M",
    "Al Jazeera Balkans",
    "RTRS",
    "BHT1",
    "FTV",
    "OBN",
    "Hayat",
    "Nova BH",
    "Cartoon Network",
    "Disney Channel",
    "Kika",
    "MTV 00",
    "CMC Music",
    "HBO",
    "SciFi",
    "Cinestar",
    "Discovery",
    "Eurosport",
    "Sport Klub HR",
    "Arena Sport 1 HR",
    "Arena Sport 1 BH",
    "Arena Sport 1",
    "Arena Sport 2",
    "Arena Sport 3",
    "CNN",
    "Euronews",
    "Sky News",
    "BBC1",
    "CNBC",
    "Bloomberg",
    "RAI1",
    "RTL DE",
    "PRO7",
    "Kabel1",
    "Sat1",
    "ZDF"
]

# EPG URLs from epg_list.txt
EPG_URLS = {
    "rts1.sr": "https://tvprofil.net/xmltv/data/rts1.sr/weekly_rts1.sr_tvprofil.net.xml.gz",
    "rts2.sr": "https://tvprofil.net/xmltv/data/rts2.sr/weekly_rts2.sr_tvprofil.net.xml.gz",
    "b92.sr": "https://tvprofil.net/xmltv/data/b92.sr/weekly_b92.sr_tvprofil.net.xml.gz",
    "prva-srpska-tv.sr": "https://tvprofil.net/xmltv/data/prva-srpska-tv.sr/weekly_prva-srpska-tv.sr_tvprofil.net.xml.gz",
    "pink.sr": "https://tvprofil.net/xmltv/data/pink.sr/weekly_pink.sr_tvprofil.net.xml.gz",
    "nova-s.sr": "https://tvprofil.net/xmltv/data/nova-s.sr/weekly_nova-s.sr_tvprofil.net.xml.gz",
    "htv1.hr": "https://tvprofil.net/xmltv/data/htv1.hr/weekly_htv1.hr_tvprofil.net.xml.gz",
    "htv2.hr": "https://tvprofil.net/xmltv/data/htv2.hr/weekly_htv2.hr_tvprofil.net.xml.gz",
    "htv3.hr": "https://tvprofil.net/xmltv/data/htv3.hr/weekly_htv3.hr_tvprofil.net.xml.gz",
    "htv4.hr": "https://tvprofil.net/xmltv/data/htv4.hr/weekly_htv4.hr_tvprofil.net.xml.gz",
    "nova.hr": "https://tvprofil.net/xmltv/data/nova.hr/weekly_nova.hr_tvprofil.net.xml.gz",
    "rtl.hr": "https://tvprofil.net/xmltv/data/rtl.hr/weekly_rtl.hr_tvprofil.net.xml.gz",
    "rtl2.hr": "https://tvprofil.net/xmltv/data/rtl2.hr/weekly_rtl2.hr_tvprofil.net.xml.gz",
    "doma-tv.movie": "https://tvprofil.net/xmltv/data/doma-tv.movie/weekly_doma-tv.movie_tvprofil.net.xml.gz",
    "plava-televizija.hr": "https://tvprofil.net/xmltv/data/plava-televizija.hr/weekly_plava-televizija.hr_tvprofil.net.xml.gz",
    "vinkovacka-tv.hr": "https://tvprofil.net/xmltv/data/vinkovacka-tv.hr/weekly_vinkovacka-tv.hr_tvprofil.net.xml.gz",
    "tv-zapad.hr": "https://tvprofil.net/xmltv/data/tv-zapad.hr/weekly_tv-zapad.hr_tvprofil.net.xml.gz",
    "slo1.si": "https://tvprofil.net/xmltv/data/slo1.si/weekly_slo1.si_tvprofil.net.xml.gz",
    "slo2.si": "https://tvprofil.net/xmltv/data/slo2.si/weekly_slo2.si_tvprofil.net.xml.gz",
    "slo3.si": "https://tvprofil.net/xmltv/data/slo3.si/weekly_slo3.si_tvprofil.net.xml.gz",
    "nova-m.cg": "https://tvprofil.net/xmltv/data/nova-m.cg/weekly_nova-m.cg_tvprofil.net.xml.gz",
    "al-jazeera-balkans.info": "https://tvprofil.net/xmltv/data/al-jazeera-balkans.info/weekly_al-jazeera-balkans.info_tvprofil.net.xml.gz",
    "rtrs.ba": "https://tvprofil.net/xmltv/data/rtrs.ba/weekly_rtrs.ba_tvprofil.net.xml.gz",
    "bht1.ba": "https://tvprofil.net/xmltv/data/bht1.ba/weekly_bht1.ba_tvprofil.net.xml.gz",
    "ftv.ba": "https://tvprofil.net/xmltv/data/ftv.ba/weekly_ftv.ba_tvprofil.net.xml.gz",
    "obn.ba": "https://tvprofil.net/xmltv/data/obn.ba/weekly_obn.ba_tvprofil.net.xml.gz",
    "hayat-tv.ba": "https://tvprofil.net/xmltv/data/hayat-tv.ba/weekly_hayat-tv.ba_tvprofil.net.xml.gz",
    "nova-bh.ba": "https://tvprofil.net/xmltv/data/nova-bh.ba/weekly_nova-bh.ba_tvprofil.net.xml.gz",
    "cartoon-network.toons": "https://tvprofil.net/xmltv/data/cartoon-network.toons/weekly_cartoon-network.toons_tvprofil.net.xml.gz",
    "disney-channel.toons": "https://tvprofil.net/xmltv/data/disney-channel.toons/weekly_disney-channel.toons_tvprofil.net.xml.gz",
    "kika.toons": "https://tvprofil.net/xmltv/data/kika.toons/weekly_kika.toons_tvprofil.net.xml.gz",
    "mtv00s.music": "https://tvprofil.net/xmltv/data/mtv00s.music/weekly_mtv00s.music_tvprofil.net.xml.gz",
    "cmc.music": "https://tvprofil.net/xmltv/data/cmc.music/weekly_cmc.music_tvprofil.net.xml.gz",
    "hbo.movie": "https://tvprofil.net/xmltv/data/hbo.movie/weekly_hbo.movie_tvprofil.net.xml.gz",
    "scifi.movie": "https://tvprofil.net/xmltv/data/scifi.movie/weekly_scifi.movie_tvprofil.net.xml.gz",
    "cinestar-tv.movie": "https://tvprofil.net/xmltv/data/cinestar-tv.movie/weekly_cinestar-tv.movie_tvprofil.net.xml.gz",
    "discovery-europe.doc": "https://tvprofil.net/xmltv/data/discovery-europe.doc/weekly_discovery-europe.doc_tvprofil.net.xml.gz",
    "eurosport.sport": "https://tvprofil.net/xmltv/data/eurosport.sport/weekly_eurosport.sport_tvprofil.net.xml.gz",
    "sportklub-hr.sport": "https://tvprofil.net/xmltv/data/sportklub-hr.sport/weekly_sportklub-hr.sport_tvprofil.net.xml.gz",
    "tv-arena-sport-1-hr.sport": "https://tvprofil.net/xmltv/data/tv-arena-sport-1-hr.sport/weekly_tv-arena-sport-1-hr.sport_tvprofil.net.xml.gz",
    "arena-sport-1-ba.sport": "https://tvprofil.net/xmltv/data/arena-sport-1-ba.sport/weekly_arena-sport-1-ba.sport_tvprofil.net.xml.gz",
    "tv-arena-sport-1.sport": "https://tvprofil.net/xmltv/data/tv-arena-sport-1.sport/weekly_tv-arena-sport-1.sport_tvprofil.net.xml.gz",
    "tv-arena-sport-2.sport": "https://tvprofil.net/xmltv/data/tv-arena-sport-2.sport/weekly_tv-arena-sport-2.sport_tvprofil.net.xml.gz",
    "tv-arena-sport-3.sport": "https://tvprofil.net/xmltv/data/tv-arena-sport-3.sport/weekly_tv-arena-sport-3.sport_tvprofil.net.xml.gz",
    "cnn.info": "https://tvprofil.net/xmltv/data/cnn.info/weekly_cnn.info_tvprofil.net.xml.gz",
    "euronews.info": "https://tvprofil.net/xmltv/data/euronews.info/weekly_euronews.info_tvprofil.net.xml.gz",
    "skynews.info": "https://tvprofil.net/xmltv/data/skynews.info/weekly_skynews.info_tvprofil.net.xml.gz",
    "bbc1.uk": "https://tvprofil.net/xmltv/data/bbc1.uk/weekly_bbc1.uk_tvprofil.net.xml.gz",
    "cnbc.info": "https://tvprofil.net/xmltv/data/cnbc.info/weekly_cnbc.info_tvprofil.net.xml.gz",
    "bloomberg.info": "https://tvprofil.net/xmltv/data/bloomberg.info/weekly_bloomberg.info_tvprofil.net.xml.gz",
    "rai-1.it": "https://tvprofil.net/xmltv/data/rai-1.it/weekly_rai-1.it_tvprofil.net.xml.gz",
    "rtl-de.de": "https://tvprofil.net/xmltv/data/rtl-de.de/weekly_rtl-de.de_tvprofil.net.xml.gz",
    "pro-7.de": "https://tvprofil.net/xmltv/data/pro-7.de/weekly_pro-7.de_tvprofil.net.xml.gz",
    "kabel-1.de": "https://tvprofil.net/xmltv/data/kabel-1.de/weekly_kabel-1.de_tvprofil.net.xml.gz",
    "sat-1.de": "https://tvprofil.net/xmltv/data/sat-1.de/weekly_sat-1.de_tvprofil.net.xml.gz",
    "zdf.de": "https://tvprofil.net/xmltv/data/zdf.de/weekly_zdf.de_tvprofil.net.xml.gz"
}

# Channel ID mapping based on lista.txt
CHANNEL_ID_MAPPING = {
    "rts1.sr": "RTS1",
    "rts2.sr": "RTS2",
    "b92.sr": "B92",
    "prva-srpska-tv.sr": "Prva",
    "pink.sr": "Pink",
    "nova-s.sr": "Nova S",
    "htv1.hr": "HTV1",
    "htv2.hr": "HTV2",
    "htv3.hr": "HTV3",
    "htv4.hr": "HTV4",
    "nova.hr": "Nova TV",
    "rtl.hr": "RTL",
    "rtl2.hr": "RTL2",
    "doma-tv.movie": "Doma TV",
    "plava-televizija.hr": "Plava TV",
    "vinkovacka-tv.hr": "Vinkovačka TV",
    "tv-zapad.hr": "TV Zapad",
    "slo1.si": "SLO1",
    "slo2.si": "SLO2",
    "slo3.si": "SLO3",
    "nova-m.cg": "Nova M",
    "al-jazeera-balkans.info": "Al Jazeera Balkans",
    "rtrs.ba": "RTRS",
    "bht1.ba": "BHT1",
    "ftv.ba": "FTV",
    "obn.ba": "OBN",
    "hayat-tv.ba": "Hayat",
    "nova-bh.ba": "Nova BH",
    "cartoon-network.toons": "Cartoon Network",
    "disney-channel.toons": "Disney Channel",
    "kika.toons": "Kika",
    "mtv00s.music": "MTV 00",
    "cmc.music": "CMC Music",
    "hbo.movie": "HBO",
    "scifi.movie": "SciFi",
    "cinestar-tv.movie": "Cinestar",
    "discovery-europe.doc": "Discovery",
    "eurosport.sport": "Eurosport",
    "sportklub-hr.sport": "Sport Klub HR",
    "tv-arena-sport-1-hr.sport": "Arena Sport 1 HR",
    "arena-sport-1-ba.sport": "Arena Sport 1 BH",
    "tv-arena-sport-1.sport": "Arena Sport 1",
    "tv-arena-sport-2.sport": "Arena Sport 2",
    "tv-arena-sport-3.sport": "Arena Sport 3",
    "cnn.info": "CNN",
    "euronews.info": "Euronews",
    "skynews.info": "Sky News",
    "bbc1.uk": "BBC1",
    "cnbc.info": "CNBC",
    "bloomberg.info": "Bloomberg",
    "rai-1.it": "RAI1",
    "rtl-de.de": "RTL DE",
    "pro-7.de": "PRO7",
    "kabel-1.de": "Kabel1",
    "sat-1.de": "Sat1",
    "zdf.de": "ZDF"
}

class CiefpTvProgram(Screen):
    skin = """
        <screen name="CiefpTvProgram" position="center,center" size="1800,800" title="..:: CiefpTvProgram v1.1 za prikaz EPG-a ::..">
            <widget name="channelList" position="0,0" size="350,668" scrollbarMode="showAlways" itemHeight="33" font="Regular;28" />
            <widget name="epgInfo" position="370,0" size="1000,668" scrollbarMode="showAlways" itemHeight="33" font="Regular;28" />
            <widget name="sideBackground" position="1380,0" size="420,668" alphatest="on" />
            <widget name="picon" position="0,668" size="220,132" alphatest="on" />
            <widget name="pluginLogo" position="220,668" size="220,132" alphatest="on" />
            <widget name="backgroundLogo" position="440,668" size="1360,132" alphatest="on" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)

        self.channelListData = CHANNEL_LIST_DATA
        self["channelList"] = MenuList(self.channelListData, enableWrapAround=True)
        self["epgInfo"] = MenuList([], enableWrapAround=True)
        self["picon"] = Pixmap()
        self["pluginLogo"] = Pixmap()
        self["backgroundLogo"] = Pixmap()
        self["sideBackground"] = Pixmap()

        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
            {
                "ok": self.switchView,
                "cancel": self.exit,
                "up": self.up,
                "down": self.down
            }, -1)

        self.currentView = "channels"
        self.epgData = {}
        self.epgLines = []
        self.epgScrollPos = 0
        self.focus_on_channels = True

        if not os.path.exists(EPG_DIR):
            try:
                os.makedirs(EPG_DIR)
                logger.debug(f"Created EPG directory: {EPG_DIR}")
            except Exception as e:
                logger.error(f"Error creating EPG directory: {str(e)}")
                self["epgInfo"].setList([f"Error creating EPG directory: {str(e)}"])

        self.downloadAndParseEPG()
        self.onLayoutFinish.append(self.loadPluginLogo)
        self.onLayoutFinish.append(self.loadBackgroundLogo)
        self.onLayoutFinish.append(self.updateEPGAndPicon)
        self.onLayoutFinish.append(self.loadSideBackground)

    def switchView(self):
        self.currentView = "epg" if self.currentView == "channels" else "channels"
        self.focus_on_channels = self.currentView == "channels"
        self.epgScrollPos = 0
        self["channelList"].instance.setSelectionEnable(self.focus_on_channels)
        self["epgInfo"].instance.setSelectionEnable(not self.focus_on_channels)
        logger.debug(f"Focus switched to {'channels' if self.focus_on_channels else 'EPG'}")
        if self.currentView == "epg":
            self.prepareEPGContent()
            self.showEPGContent()
        else:
            self.updateEPGAndPicon()

    def exit(self):
        self.close()

    def up(self):
        if self.currentView == "channels":
            self["channelList"].up()
            self.updateEPGAndPicon()
            logger.debug("Moved up in channel list")
        elif self.currentView == "epg":
            self["epgInfo"].up()
            logger.debug("Moved up in EPG list")

    def down(self):
        if self.currentView == "channels":
            self["channelList"].down()
            self.updateEPGAndPicon()
            logger.debug("Moved down in channel list")
        elif self.currentView == "epg":
            self["epgInfo"].down()
            logger.debug("Moved down in EPG list")

    def updateEPGAndPicon(self):
        current = self["channelList"].getCurrent()
        if current:
            channel_name = current
            self.prepareEPGContent()  # Prepare EPG content with current program index
            self.showEPGContent()  # Show EPG content and scroll to current program
            self.loadPicon(channel_name)
            logger.debug(f"Updated EPG and picon for channel: {channel_name}")

    def loadPicon(self, channel_name):
        chan_id = next((cid for cid, cname in CHANNEL_ID_MAPPING.items() if cname == channel_name), None)
        if not chan_id:
            logger.debug(f"No channel ID found for {channel_name}")
            return
        picon_name = f"{chan_id}.png"
        filename = os.path.join(PICON_PATH, picon_name)
        logger.debug(f"Attempting to load picon for channel {channel_name}: {filename}")
        pixmap = None
        if os.path.exists(filename):
            try:
                file_size = os.path.getsize(filename)
                logger.debug(f"Picon file found: {filename}, size: {file_size} bytes")
                pixmap = LoadPixmap(filename)
                if pixmap:
                    logger.debug(f"Successfully loaded picon: {filename}")
                else:
                    logger.warning(f"Failed to load pixmap for picon: {filename}")
            except Exception as e:
                logger.error(f"Error loading picon for {channel_name}: {str(e)}")
        else:
            logger.warning(f"Picon file not found: {filename}")
            if os.path.exists(PLACEHOLDER_PICON):
                try:
                    pixmap = LoadPixmap(PLACEHOLDER_PICON)
                    if pixmap:
                        logger.debug(f"Successfully loaded placeholder picon: {PLACEHOLDER_PICON}")
                    else:
                        logger.warning(f"Failed to load pixmap for placeholder picon: {PLACEHOLDER_PICON}")
                except Exception as e:
                    logger.error(f"Error loading placeholder picon: {str(e)}")
            else:
                logger.warning(f"Placeholder picon not found: {PLACEHOLDER_PICON}")
            try:
                dir_contents = os.listdir(PICON_PATH)
                logger.debug(f"Picon directory contents: {dir_contents}")
            except Exception as e:
                logger.error(f"Error listing picon directory {PICON_PATH}: {str(e)}")

        if pixmap and self["picon"].instance:
            try:
                self["picon"].instance.setPixmap(pixmap)
                logger.debug(f"Picon set for channel {channel_name}: {filename}")
            except Exception as e:
                logger.error(f"Error setting picon for {channel_name}: {str(e)}")
        else:
            logger.debug(f"Picon widget not initialized or pixmap not loaded for {channel_name}")

    def loadPluginLogo(self):
        logo_path = os.path.join(PLUGIN_PATH, "plugin_logo.png")
        logger.debug(f"Attempting to load plugin logo: {logo_path}")
        pixmap = None
        if os.path.exists(logo_path):
            try:
                file_size = os.path.getsize(logo_path)
                logger.debug(f"Plugin logo file found: {logo_path}, size: {file_size} bytes")
                pixmap = LoadPixmap(logo_path)
                if pixmap:
                    logger.debug(f"Successfully loaded plugin logo: {logo_path}")
                else:
                    logger.warning(f"Failed to load pixmap for plugin logo: {logo_path}")
            except Exception as e:
                logger.error(f"Error loading plugin logo: {str(e)}")
        else:
            logger.warning(f"Plugin logo file not found: {logo_path}")
            try:
                dir_contents = os.listdir(PLUGIN_PATH)
                logger.debug(f"Plugin directory contents: {dir_contents}")
            except Exception as e:
                logger.error(f"Error listing plugin directory {PLUGIN_PATH}: {str(e)}")

        if pixmap and self["pluginLogo"].instance:
            try:
                self["pluginLogo"].instance.setPixmap(pixmap)
                logger.debug(f"Plugin logo set: {logo_path}")
            except Exception as e:
                logger.error(f"Error setting plugin logo: {str(e)}")
        else:
            logger.debug(f"Plugin logo widget not initialized or pixmap not loaded")

    def loadBackgroundLogo(self):
        logo_path = os.path.join(PLUGIN_PATH, "background_logo.png")
        logger.debug(f"Attempting to load background logo: {logo_path}")
        pixmap = None
        if os.path.exists(logo_path):
            try:
                file_size = os.path.getsize(logo_path)
                logger.debug(f"Background logo file found: {logo_path}, size: {file_size} bytes")
                pixmap = LoadPixmap(logo_path)
                if pixmap:
                    logger.debug(f"Successfully loaded background logo: {logo_path}")
                else:
                    logger.warning(f"Failed to load pixmap for background logo: {logo_path}")
            except Exception as e:
                logger.error(f"Error loading background logo: {str(e)}")
        else:
            logger.warning(f"Background logo file not found: {logo_path}")
            try:
                dir_contents = os.listdir(PLUGIN_PATH)
                logger.debug(f"Plugin directory contents: {dir_contents}")
            except Exception as e:
                logger.error(f"Error listing plugin directory {PLUGIN_PATH}: {str(e)}")

        if pixmap and self["backgroundLogo"].instance:
            try:
                self["backgroundLogo"].instance.setPixmap(pixmap)
                logger.debug(f"Background logo set: {logo_path}")
            except Exception as e:
                logger.error(f"Error setting background logo: {str(e)}")
        else:
            logger.debug(f"Background logo widget not initialized or pixmap not loaded")

    def loadSideBackground(self):
        bg_path = os.path.join(PLUGIN_PATH, "side_background.png")
        pixmap = None
        if os.path.exists(bg_path):
            try:
                pixmap = LoadPixmap(bg_path)
            except Exception as e:
                logger.error(f"Error loading side background: {str(e)}")
        if pixmap and self["sideBackground"].instance:
            try:
                self["sideBackground"].instance.setPixmap(pixmap)
            except Exception as e:
                logger.error(f"Error setting side background: {str(e)}")

    def checkLastUpdate(self):
        """Check if the last update was more than 2 days ago."""
        if not os.path.exists(LAST_UPDATE_FILE):
            logger.debug(f"No last update file found: {LAST_UPDATE_FILE}")
            return True  # No update file, force update
        try:
            with open(LAST_UPDATE_FILE, 'r') as f:
                last_update_str = f.read().strip()
            last_update = datetime.datetime.strptime(last_update_str, '%Y-%m-%d')
            days_since_update = (datetime.datetime.now() - last_update).days
            logger.debug(f"Last update was {days_since_update} days ago on {last_update_str}")
            return days_since_update >= 2  # Update if 2 or more days have passed
        except Exception as e:
            logger.error(f"Error reading last update file {LAST_UPDATE_FILE}: {str(e)}")
            return True  # If error, force update

    def updateLastUpdateFile(self):
        """Update the last_update.txt file with the current date."""
        try:
            # Delete old last_update file if it exists
            if os.path.exists(LAST_UPDATE_FILE):
                os.remove(LAST_UPDATE_FILE)
                logger.debug(f"Removed old last update file: {LAST_UPDATE_FILE}")
            # Create new last_update file with current date
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            with open(LAST_UPDATE_FILE, 'w') as f:
                f.write(current_date)
            logger.debug(f"Created new last update file: {LAST_UPDATE_FILE} with date {current_date}")
        except Exception as e:
            logger.error(f"Error updating last update file {LAST_UPDATE_FILE}: {str(e)}")

    def downloadAndParseEPG(self):
        try:
            # Check if EPGImport file exists
            if os.path.exists(EPGIMPORT_FILE):
                logger.debug(f"Using EPGImport file: {EPGIMPORT_FILE}")
                self.parseEPG(EPGIMPORT_FILE)
                return

            # Check if update is needed based on last_update.txt
            if not self.checkLastUpdate():
                logger.debug("No update needed based on last_update.txt")
                # Load cached EPG files
                channel_ids = {chan_id for chan_id, chan_name in CHANNEL_ID_MAPPING.items() if chan_name in CHANNEL_LIST_DATA}
                for chan_id in channel_ids:
                    epg_file = os.path.join(EPG_DIR, f"{chan_id}.xml")
                    if os.path.exists(epg_file):
                        logger.debug(f"Parsing cached EPG file: {epg_file}")
                        self.parseEPG(epg_file)
                return

            # Proceed with downloading new EPG data
            channel_ids = {chan_id for chan_id, chan_name in CHANNEL_ID_MAPPING.items() if chan_name in CHANNEL_LIST_DATA}
            for chan_id in channel_ids:
                url = EPG_URLS.get(chan_id)
                if not url:
                    logger.debug(f"No EPG URL for channel ID: {chan_id}")
                    continue
                epg_file = os.path.join(EPG_DIR, f"{chan_id}.xml")
                logger.debug(f"Downloading EPG for {chan_id} from {url}")
                temp_file = os.path.join(EPG_DIR, f"{chan_id}.xml.gz")
                urllib.request.urlretrieve(url, temp_file)
                logger.debug(f"Decompressing EPG for {chan_id}: {temp_file}")
                with gzip.open(temp_file, 'rb') as f_in:
                    with open(epg_file, 'wb') as f_out:
                        f_out.write(f_in.read())
                logger.debug(f"Decompressed EPG saved to: {epg_file}")
                os.remove(temp_file)

            # Parse all downloaded EPG files
            for chan_id in channel_ids:
                epg_file = os.path.join(EPG_DIR, f"{chan_id}.xml")
                if os.path.exists(epg_file):
                    logger.debug(f"Parsing EPG file: {epg_file}")
                    self.parseEPG(epg_file)

            # Update the last_update.txt file after successful download and parse
            self.updateLastUpdateFile()
        except Exception as e:
            logger.error(f"EPG download or decompression error: {str(e)}")
            self["epgInfo"].setList([f"Greška pri preuzimanju EPG-a: {str(e)}"])

    def parseEPG(self, epg_file):
        try:
            with open(epg_file, 'rb') as f:
                content = f.read()
                if content.startswith(b'\xEF\xBB\xBF'):
                    content = content[3:]
                try:
                    xml_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    xml_content = content.decode('iso-8859-1')
                tree = ET.parse(io.StringIO(xml_content))
            root = tree.getroot()
            today = datetime.datetime.now().strftime('%Y%m%d')
            if not self.epgData:
                self.epgData = {channel_name: [] for channel_name in CHANNEL_LIST_DATA}
                logger.debug(f"Initialized epgData with channels: {list(self.epgData.keys())}")
            unmatched_channels = set()
            programme_dates = set()
            channel_ids = set()

            for channel in root.findall('channel'):
                chan_id = channel.get('id')
                if chan_id:
                    channel_ids.add(chan_id.lower())

            for programme in root.findall('programme'):
                chan_id = programme.get('channel')
                if chan_id:
                    chan_id = chan_id.lower()
                    title = programme.find('title').text if programme.find('title') is not None else "No Title"
                    desc = programme.find('desc').text if programme.find('desc') is not None else ""
                    start = programme.get('start')
                    if start:
                        programme_dates.add(start[:8])
                        if start[:8] >= today:
                            channel_name = CHANNEL_ID_MAPPING.get(chan_id)
                            if channel_name and channel_name in self.epgData:
                                self.epgData[channel_name].append((start, title, desc))
                                logger.debug(f"Added EPG entry for {channel_name}: {title} at {start}")
                            else:
                                unmatched_channels.add(chan_id)
            logger.debug(f"Programme dates found: {sorted(programme_dates)}")
            logger.debug(f"Channel IDs found in EPG: {sorted(channel_ids)}")
            logger.debug(f"Unmatched EPG channel IDs: {sorted(unmatched_channels)}")
            logger.debug(f"EPG parsing completed. epgData: {{k: len(v) for k, v in self.epgData.items()}}")
        except Exception as e:
            logger.error(f"EPG parsing error: {str(e)}")
            self["epgInfo"].setList([f"Greška pri parsiranju EPG-a: {str(e)}"])

    def getEPGFromXML(self, channel_name):
        epglist = self.epgData.get(channel_name, [])
        if not epglist:
            logger.debug(f"No EPG data for {channel_name} in XML")
            return [f"Nema EPG podataka za kanal: {channel_name}"]
        # Group EPG entries by date
        epg_by_date = {}
        for start, title, desc in sorted(epglist, key=lambda x: x[0]):
            date_str = start[:8]
            date_formatted = datetime.datetime.strptime(date_str, '%Y%m%d').strftime('%d.%m.%Y')
            time_str = start[8:12]
            time_formatted = f"{time_str[:2]}:{time_str[2:]}"
            entry = f"{date_formatted} {time_formatted} - {title}"
            if desc:
                entry += f"\n  {desc}"
            if date_str not in epg_by_date:
                epg_by_date[date_str] = []
            epg_by_date[date_str].append(entry)

        # Combine entries with date headers
        result = []
        for date_str in sorted(epg_by_date.keys()):
            date_formatted = datetime.datetime.strptime(date_str, '%Y%m%d').strftime('%d.%m.%Y')
            result.append(f"--- {date_formatted} ---")
            result.extend(epg_by_date[date_str])
        return result

    def prepareEPGContent(self):
        current = self["channelList"].getCurrent()
        if current:
            channel_name = current
            self.epgLines = self.getEPGFromXML(channel_name)
            logger.debug(f"Prepared EPG content for {channel_name}: {len(self.epgLines)} lines")
            # Find the index of the current program
            now = datetime.datetime.now()
            now_str = now.strftime('%Y%m%d%H%M%S')
            current_index = 0
            for i, line in enumerate(self.epgLines):
                if not line.startswith("---"):
                    try:
                        # Extract date and time from the line
                        date_time_str = line.split(" - ")[0]
                        date_str, time_str = date_time_str.split(" ")
                        date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", '%d.%m.%Y %H:%M')
                        epg_time_str = date_obj.strftime('%Y%m%d%H%M%S')
                        if epg_time_str <= now_str:
                            current_index = i
                        else:
                            break
                    except Exception as e:
                        logger.debug(f"Error parsing EPG line for current program: {line}, error: {str(e)}")
            self.epgScrollPos = current_index
            logger.debug(f"Set EPG scroll position to index {current_index} for current program")

    def showEPGContent(self):
        self["epgInfo"].setList(self.epgLines)
        self["epgInfo"].moveToIndex(self.epgScrollPos)
        logger.debug(f"Showing EPG content, lines: {len(self.epgLines)}, selected index: {self.epgScrollPos}")

from Plugins.Plugin import PluginDescriptor

def main(session, **kwargs):
    session.open(CiefpTvProgram)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="CiefpTvProgram",
        description="Tv Program Prikaz EPG-a v1.2",
        where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
        icon="icon.png",
        fnc=main
    )