import os
import sys
import time
import feedparser

from crontab import CronTab
from threading import Thread
from sqlalchemy.sql import and_
from flask.ext.login import current_user

from . import db
from .models import Alarm, Music
from my_mpd import PersistentMPDClient


# get current environment variable for crontab commands
# env_path     = os.environ['VIRTUAL_ENV']
env_path = '/home/pi/.virtualenvs/apiclock'
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
cron_command = env_path + '/bin/python ' + script_path + '/mpdplay.py'
newcron = CronTab(user=True)


class Snooze(Thread):
    """Activate a thread for Snooze function."""

    def __init__(self, radiosnooze, minutessnooze):
        Thread.__init__(self)
        self.radio = radiosnooze
        self.duree = minutessnooze*60
        self.client = PersistentMPDClient()
        self.client.clear()

    def run(self):
        """start jouerMPD stop during minutesnooze then stop MPD."""
        self.client.add(self.radio)
        self.client.play()
        time.sleep(self.duree)
        self.client.stop()


def snooze(radiosnooze, minutessnooze):
    """Create a Snooze thread and start it."""
    thr_snooze = Snooze(radiosnooze, minutessnooze)
    thr_snooze.start()


class Chrono_(Thread):
    """Activate a thread for chrono function."""

    def __init__(self, mediachrono, minuteschrono):
        Thread.__init__(self)
        self.media = mediachrono
        self.duree = minuteschrono * 60
        self.client = PersistentMPDClient()
        self.client.clear()

    def run(self):
        """start jouerMPD after a delay = minuteschrono."""
        print "ok"
        time.sleep(self.duree)
        self.client.add('/home/pi/Apiclock_PROD/app/static/music/UPLOAD_call.mp3')
        self.client.play()

        # DEBUGG
        print "----------------"
        print self.media
        # DEBUGG

        time.sleep(120)
        self.client.stop()


def Chrono(mediachrono, minuteschrono):
    """Create a Snooze thread and start it."""
    thr_chrono = Chrono_(mediachrono, minuteschrono)
    thr_chrono.start()


def addcronenvoi(monalarme):
    """Transform and add alarm in crontab with a 2h duration."""
    alarmduration = int(monalarme['heure'])+2

    job = newcron.new(command=cron_command + ' ' + monalarme['path'],
                      comment='Alarme ID:' + str(monalarme['id']))

    # # Frequence = week or day
    # if int(monalarme['repetition']) == 2:
    #     jours = ",".join(map(str, monalarme['jours']))
    # elif int(monalarme['repetition']) == 1:
    #     jours = "'*'"
    # else:
    #     pass
    #
    # # Frequence = Month
    # if int(monalarme['repetition']) == 3:
    #     daysofmonth = str(moment.now().format("D"))
    # else:
    #     daysofmonth = "'*'"
    #     month = "'*'"
    #     jours = "'*'"
    #
    # # Frequence = Year
    # if int(monalarme['repetition']) == 4:
    #     daysofmonth = str(moment.now().format("D"))
    #     month = str(moment.now().format("M"))
    # else:
    #     month = "'*'"
    #     daysofmonth = "'*'"
    #     jours = "'*'"
    #
    # job.setall(
    #     monalarme['minute'],
    #     "{}-{}".format(monalarme['heure'], alarmduration),
    #     # str(monalarme['heure'])+'-'+str(alarmduration),
    #     daysofmonth,
    #     month,
    #     jours)
    jours = ",".join(map(str, monalarme['jours']))
    job.setall(
        monalarme['minute'],
        "{}-{}".format(monalarme['heure'], alarmduration),
        # str(monalarme['heure'])+'-'+str(alarmduration),
        '*',
        '*',
        jours)

    # FREQUENCE
    # ('0', 'None')('1', 'Days'), ('2', 'Weeks'),
    # ('3', 'Month'), ('4', 'Year')])

    job.enable()
    try:
        newcron.write()
        return 0
    except:
        return 1


def removecron(idalarm):
    newcron.remove_all(comment='Alarme ID:'+str(idalarm))
    newcron.write()


def statealarm(idalarm):
    """
    Find the existing alarm by id in crontab comment
    and activate or deactivate it.
    """
    actionalarm = newcron.find_comment('Alarme ID:' + str(idalarm))
    actionalarm = next(actionalarm)
    alarms = Alarm.query.filter(Alarm.id == idalarm).first()
    if alarms.state == 1:
        alarms.state = 0
        actionalarm.enable(False)
    else:
        alarms.state = 1
        actionalarm.enable()
    newcron.write()
    db.session.commit()


def getpodcasts():
    """Get all emissions for the current_user podcast."""
    podcasts = Music.query.filter(and_(Music.music_type == '2',
                                       Music.users == current_user.id)).all()
    listepodcast = []
    # Get URL of all emissions off the podcast
    for emission in podcasts:
        d = feedparser.parse(emission.url)
        emissions = [(d.entries[i]['title'],
                     d.entries[i].enclosures[0]['href'])
                     for i, j in enumerate(d.entries)]
        listepodcast.append(emissions)
    return listepodcast
