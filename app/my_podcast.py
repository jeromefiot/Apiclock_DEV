# -*- coding: utf-8 -*-
import mpd
import podcastparser
import urllib
from crontab import CronTab


class ApiPodcast():
    def __init__(self, name=None, url=None):

        self.name = ""
        self.url = ""
        # check url validity

    def playpodcastlocal(self, name, show):
        """Add podcast and play show local.
        . Check podcast folder (name of podcast)
        . get show and play it local
        """
        pass

    def playpodcastdistant(self, media):
        """Add podcast and play show distant.
        . Check podcast folder (name of podcast)
        . get show and play it distant
        """
        pass

    def addpodcast(sefl, url):
        """Add podcast and shows to mympd.
        . Verify URL validity
        . Create folder (name of podcast)
        . Check free space
        . Get last 5 shows
        . Add cron to check new shows everyday with podcastname in comment
        (if new : check free spacen DL new one and remove oldest)
        (o)ption : send notification
        (o)ption :
        """
        pass

    def removepodcast(self, name):
        """Remove podcast and shows from mympd.
        . Check podcast folder (name of podcast)
        . Remove all shows
        . Remove cron with podcastname in comment
        """
        pass

    def infospodcast(self, url, max_episodes=0):
        """Get podcast shows list (parsed)."""
        parsed = podcastparser.parse(url, urllib.urlopen(url))
        return parsed
