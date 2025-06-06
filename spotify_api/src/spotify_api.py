import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger("spotipy").setLevel(logging.ERROR)
logging.getLogger("spotipy").setLevel(logging.CRITICAL)

class SpotipyClient:
    def __init__(self, client_id, client_secret, max_retries=3, rate_limit=1.0):
        self.auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(
            auth_manager=self.auth_manager,
            retries=0,
            status_retries=0,
            backoff_factor=0,
            requests_timeout=10,
        )
        self.max_retries = max_retries
        self.rate_limit = rate_limit  # segons entre peticions
        self._last_request_time = 0

    def get_year(self, track_id):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

        try:
            track = self.sp.track(track_id)
            self._last_request_time = time.time()
            release_date = track['album']['release_date']
            if release_date:
                return int(release_date.split('-')[0])
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                time.sleep(5)
            else:
                print(f"Error inesperat amb el track {track_id}: {e}")
            return 0
        except Exception as e:
            print(f"Error desconegut amb el track {track_id}: {e}")
            return 0