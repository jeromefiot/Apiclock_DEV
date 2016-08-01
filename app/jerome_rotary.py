# Sample code for both the RotaryEncoder class and the Switch class.
# The common pin for the encoder should be wired to ground.
# The sw_pin should be shorted to ground by the switch.

# Force parent directory as lib one
import sys
import os
# Compute package path
#package_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
#sys.path.append(package_path)

from flask import Flask, current_app
from config import config
import rotary_encoder
import switch
import OLD_mympd

app = Flask(__name__)
app.config.from_object(config['default'])

with app.app_context():
    # http://stackoverflow.com/questions/7505988/importing-from-a-relative-path-in-python
    app_apiclock = current_app._get_current_object()

    A_PIN = 7
    B_PIN = 1
    SW_PIN = 3

    mpd_player = OLD_mympd.PersistentMPDClient()

    encoder = rotary_encoder.RotaryEncoder.Worker(A_PIN, B_PIN)
    encoder.start()
    switch = switch.Switch(SW_PIN)
    last_state = None

    while True:
        delta = encoder.get_delta()
        if delta != 0:
            print ("rotate %d" % delta)
            mpd_player.play_media()

        sw_state = switch.get_state()
        if sw_state != last_state:
            print ("switch %d" % sw_state)
            last_state = sw_state
            mpd_player.stop()
