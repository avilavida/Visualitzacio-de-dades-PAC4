import musicbrainzngs

import musicbrainzngs
import time

class MusicBrainzClient:
    def __init__(self, rate_limit=1.0):
        self.rate_limit = rate_limit
        musicbrainzngs.set_useragent(
            "MusicEmotionProject", "1.0", "teu@email.com"
        )
        self.last_call = 0

    def _respect_rate_limit(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_call = time.time()

    def get_year(self, artist, track_name, album_name):
        self._respect_rate_limit()
        try:
            result = musicbrainzngs.search_recordings(
                recording=track_name,
                artist=artist,
                release=album_name,
                limit=3
            )
            recordings = result.get('recording-list', [])

            for recording in recordings:
                releases = recording.get('release-list', [])
                for release in releases:
                    release_date = release.get('date')
                    if release_date:
                        return int(release_date.split('-')[0])

                    events = release.get('release-event-list', [])
                    for event in events:
                        event_date = event.get('date')
                        if event_date:
                            return int(event_date.split('-')[0])
            return 0
        except Exception as e:
            print(f'Error cercant {track_name} de {artist}: {e}')
            return 0