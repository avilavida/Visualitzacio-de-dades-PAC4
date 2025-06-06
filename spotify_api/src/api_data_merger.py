import pandas as pd
from tqdm import tqdm
import threading
import queue
import time
from musicbrainzngs_api import MusicBrainzClient
from spotify_api import SpotipyClient
from discogs_apli import DiscogsClient

class APIDataMerger():
    def __init__(self, df, spotify_client_id, spotify_client_secret, discogs_token):
        self.df = df
        self.df_length = len(df)

        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret

        self.discogs_token = discogs_token

        self.stop_event = threading.Event()

    def _save_if_safe(self, save_path):
        if self.df_length != len(self.df):
            self.stop_event.set()
            print(f"🛑 Stop Program: DataFrame length changed from {self.df_length} to {len(self.df)}!")
            return False

        self.df.to_csv(save_path, index=False)
        return True
    
    def _autosave_worker(self, save_path, interval=30):
        """
        Guarda el df cada 'interval' segons si hi ha canvis.
        """
        last_saved = 0

        while not self.stop_event.is_set():
            # Comptar files amb 'year' no nul
            processed = self.df['year'].notnull().sum()

            if processed > last_saved + 50:
                status = self._save_if_safe(save_path)

                if not status:
                    return

                print(f"💾 Guardat automàtic després de {processed} cançons processades")
                last_saved = processed

            time.sleep(interval)  # espera abans de tornar a comprovar

    def _worker_spotify(self, spc, q, pbar):
        while not self.stop_event.is_set():
            try:
                idx = q.get(timeout=1)
            except queue.Empty:
                continue

            if idx is None:
                q.task_done()
                break

            row = self.df.loc[idx]
            if pd.notnull(row['year']):
                q.task_done()
                pbar.update(1)
                continue

            year = None
            retries = 0
            max_retries = 5

            while year is None and retries < max_retries and not self.stop_event.is_set():
                year = spc.get_year(row['track_id'])
                if year is None:
                    retries += 1
                    time.sleep(2)

            self.df.loc[idx, 'year'] = int(year) if year else None

            q.task_done()
            pbar.update(1)

    def _worker_musicbrainz(self, mbc, q, pbar):
        while not self.stop_event.is_set():
            try:
                idx = q.get(timeout=1)
            except queue.Empty:
                continue

            if idx is None:
                q.task_done()
                break

            row = self.df.loc[idx]
            if pd.notnull(row['year']):
                q.task_done()
                pbar.update(1)
                continue

            year = mbc.get_year(row['artists'], row['track_name'], row['album_name'])
            self.df.loc[idx, 'year'] = int(year) if year else None

            q.task_done()
            pbar.update(1)

    def _worker_discogs(self, discogs_client, q, pbar):
            while not self.stop_event.is_set():
                try:
                    idx = q.get(timeout=1)
                except queue.Empty:
                    continue

                if idx is None:
                    q.task_done()
                    break

                row = self.df.loc[idx]
                if pd.notnull(row['year']):
                    q.task_done()
                    pbar.update(1)
                    continue

                year = discogs_client.get_year(row['artists'], row['track_name'], row['album_name'])
                self.df.loc[idx, 'year'] = int(year) if year else None

                q.task_done()
                pbar.update(1)

    def complete_dataset(self, save_path):
        spc = SpotipyClient(self.spotify_client_id, self.spotify_client_secret, rate_limit=0.5)
        mbc = MusicBrainzClient(rate_limit=0.9)
        dc = DiscogsClient(user_token=self.discogs_token)

        q_spotify = queue.Queue()
        q_musicbrainz = queue.Queue()
        q_discogs = queue.Queue()

        total_tasks = sum(pd.isnull(self.df['year']))
        pbar = tqdm(total=total_tasks, desc="Processant tracks")

        for i, idx in enumerate(self.df.index):
            if pd.notnull(self.df.loc[idx, 'year']):
                continue
            elif i % 3 == 0:
                q_spotify.put(idx)
            elif i % 2 == 0:
                q_musicbrainz.put(idx)
            else:
                q_discogs.put(idx)

        autosave_thread = threading.Thread(target=self._autosave_worker, args=(save_path, 10))
        t_spotify = threading.Thread(target=self._worker_spotify, args=(spc, q_spotify, pbar))
        t_musicbrainz = threading.Thread(target=self._worker_musicbrainz, args=(mbc, q_musicbrainz, pbar))
        t_discogs = threading.Thread(target=self._worker_discogs, args=(dc, q_discogs, pbar))

        autosave_thread.start()
        t_spotify.start()
        t_musicbrainz.start()
        t_discogs.start()

        try:
            while t_spotify.is_alive() or t_musicbrainz.is_alive() or t_discogs.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupció manual detectada! Finalitzant...")

            # Senyalem als threads que aturin
            self.stop_event.set()

            # Posa None per desbloquejar les cues i fer acabar els workers
            q_spotify.put(None)
            q_musicbrainz.put(None)
            q_discogs.put(None)

            # Esperem que acabin els workers
            t_spotify.join()
            t_musicbrainz.join()
            t_discogs.join()

            # Ara aturem el thread d’autosave
            autosave_thread.join()

            status = self._save_if_safe(save_path)
            if not status:
                return
            print("💾 Progrés guardat abans de sortir")
        else:
            # Si els workers acaben normalment, també parem l’autosave
            self.stop_event.set()
            autosave_thread.join()

        pbar.close()

        final_path = "data/df_filtered_final.csv"
        status = self._save_if_safe(final_path)
        if not status:
            return
        print(f"✅ Arxiu final guardat com {final_path}")