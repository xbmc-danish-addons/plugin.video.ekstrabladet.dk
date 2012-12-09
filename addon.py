#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import os
import sys
import urllib2
import re
import urlparse
import datetime

import buggalo

import xbmcgui
import xbmcaddon
import xbmcplugin

BASE_URL = 'http://ekstrabladet.dk'
MONTHS = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']

class EBTVAddon(object):
    def showClips(self):
        u = urllib2.urlopen(BASE_URL + '/ebtv/')
        html = u.read()
        u.close()

        # Big one
        for m in re.finditer('<img alt="" src="([^"]+)"></a>.*?</p>.*?<h1><a href="([^"]+)".*?>(.*?)</h1>.*?\| (.*?) \|', html, re.DOTALL):
            image = m.group(1)
            url = m.group(2)
            title = m.group(3).strip()
            date = self.parseDate(m.group(4))
            self.addClip(url, image, title, date)


        # Lige nu
        for m in re.finditer('<img alt="" src="([^"]+)">.*?</a>.*?<a href="([^"]+)" class="txt".*?>(.*?)<em>([^<]+)</em>', html, re.DOTALL):
            image = m.group(1)
            url = m.group(2)
            title = m.group(3).strip()
            date = self.parseDate(m.group(4))
            self.addClip(url, image, title, date)

        # Seneste TV
        for m in re.finditer('<a class="img" href="([^"]+)">.*?<img src="([^"]+)".*?<a class="txt".*?>(.*?)<em>([^<]+)</em>', html, re.DOTALL):
            url = m.group(1)
            image = m.group(2)
            title = m.group(3).strip()
            date = self.parseDate(m.group(4))
            self.addClip(url, image, title, date)


        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.endOfDirectory(HANDLE)

    def addClip(self, url, image, title, date):
        infoLabels = dict()
        infoLabels['studio'] = ADDON.getAddonInfo('name')
        infoLabels['title'] = title.decode('iso-8859-1')
        if date:
            infoLabels['date'] = date.strftime('%d.%m.%Y')
            infoLabels['aired'] = date.strftime('%Y-%m-%d')
            infoLabels['year'] = int(date.strftime('%Y'))
        else:
            print title

        item = xbmcgui.ListItem(title, iconImage = image)
        item.setInfo('video', infoLabels)
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(HANDLE, PATH + '?url=' + url, item)

    def playClip(self, url):
        u = urllib2.urlopen(url)
        html = u.read()
        u.close()

        m = re.search('clip_id=([0-9]+)', html)
        if m:
            path = 'http://front.xstream.dk/eb/mobile/mediamaker_iphone.php?clip_id=' + m.group(1)
            thumbnailImage = BASE_URL + '/template/v1-1/components/diverse/relay.jsp?url=' + m.group(1)
            item = xbmcgui.ListItem(path = path, thumbnailImage = thumbnailImage)
            xbmcplugin.setResolvedUrl(HANDLE, True, item)
        else:
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())

    def parseDate(self, dateStr):
        m = re.search('([0-9]{2}:[0-9]{2}, )?([0-9]{1,2}). ([a-z]{3})( [0-9]{4})?', dateStr)
        if m:
            day = int(m.group(2))
            month = MONTHS.index(m.group(3)) + 1
            if m.group(4):
                year = int(m.group(4).strip())
            else:
                year = datetime.datetime.now().year

            return datetime.datetime(year, month, day)

        return None

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')

    buggalo.SUBMIT_URL = 'http://tommy.winther.nu/exception/submit.php'
    try:
        ebtv = EBTVAddon()
        if PARAMS.has_key('url'):
            ebtv.playClip(PARAMS['url'][0])
        else:
            ebtv.showClips()
    except Exception:
        buggalo.onExceptionRaised()
