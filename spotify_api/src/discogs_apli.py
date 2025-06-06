import time
import requests

class DiscogsClient:
    def __init__(self, user_token=None):
        self.user_token = user_token
        self.base_url = "https://api.discogs.com"
        self.headers = {
            'Authorization': f'Discogs token={self.user_token}',
            'User-Agent': 'MyApp/1.0'
        }
        self.rate_limit = 60
        self.requests_made = 0
        self.reset_time = time.time() + 60

    def _check_rate_limit(self, response):
        limit = int(response.headers.get('X-Discogs-Ratelimit', 60))
        used = int(response.headers.get('X-Discogs-Ratelimit-Used', 0))
        remaining = int(response.headers.get('X-Discogs-Ratelimit-Remaining', limit))
        
        now = time.time()
        if now > self.reset_time:
            self.reset_time = now + 60
            self.requests_made = 0
        
        self.requests_made = used
        
        if remaining <= 1:
            wait = self.reset_time - now
            if wait > 0:
                time.sleep(wait)

    def search_release(self, artist, track_name, album_name):
        params = {
            'artist': artist,
            'title': track_name,
            'release_title': album_name,
            'type': 'release',
            'per_page': 5,
        }
        url = f"{self.base_url}/database/search"
        response = requests.get(url, headers=self.headers, params=params)
        self._check_rate_limit(response)

        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Error a Discogs API: {response.status_code}")
            return []

    def get_year(self, artists, track_name, album_name):
        results = self.search_release(artists, track_name, album_name)
        for release in results:
            year = release.get("year")
            if year:
                try:
                    return int(year)
                except ValueError:
                    continue
        return 0