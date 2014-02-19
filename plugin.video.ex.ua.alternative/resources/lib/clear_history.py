# -*- coding: utf-8 -*-
# Name:        module1
# Author:      Roman V.M.
# Created:     15.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import sys
import xbmcvfs
import xbmcgui


def main():
    if sys.argv[1] == 'history':
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить историю поиска?'):
            xbmcvfs.delete('special://masterprofile/addon_data/plugin.video.ex.ua.aternative/.storage/storage')
    elif sys.argv[1] == 'cache':
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить кэш стнаниц?'):
            xbmcvfs.delete('special://masterprofile/addon_data/plugin.video.ex.ua.aternative/.storage/.functions')
    else:
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно удалить cookies?'):
            xbmcvfs.delete('special://masterprofile/addon_data/plugin.video.ex.ua.aternative/.cookies')


if __name__ == '__main__':
    main()