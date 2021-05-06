import pychromecast
import sys
import time

services, browser = pychromecast.discovery.discover_chromecasts()

# Change to the friendly name of your Chromecast
CAST_NAME = "Living Room display"

# Change to an audio or video url
MEDIA_URL = "https://www.funmag.org/wp-content/uploads/2013/11/08-alarm-ringtones.mp3"

chromecasts, browser  = pychromecast.get_listed_chromecasts(friendly_names=[CAST_NAME])

if not chromecasts:
    print('No chromecast with name "{}" discovered'.format(CAST_NAME))
    sys.exit(1)

cast = chromecasts[0]

# Start socket client's worker thread and wait for initial status update
cast.wait()
print(
    'Found chromecast with name "{}", attempting to play "{}"'.format(
        CAST_NAME, MEDIA_URL
    )
)

cast.media_controller.play_media(MEDIA_URL, "audio/mp3")

try:
    while True:
        pass
except KeyboardInterrupt:
    cast.media_controller.stop()
    pychromecast.discovery.stop_discovery(browser)

print("Exited")
