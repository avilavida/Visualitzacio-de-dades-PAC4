import pandas as pd
import os
import numpy as np

class DataProcessor():
    def __init__(self):
        pass

    def _remove_outliers_iqr(self, subset):
        for col in ['valence', 'energy']:
            Q1 = subset[col].quantile(0.25)
            Q3 = subset[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            subset = subset[(subset[col] >= lower_bound) & (subset[col] <= upper_bound)]
        return subset
    

    def _simplify_genre(self, genre):
        genre = genre.lower()
        if genre in ['pop', 'power-pop', 'pop-film', 'party', 'happy']:
            return 'Pop'
        elif genre in ['rock', 'alt-rock', 'hard-rock', 'punk', 'punk-rock', 'grunge', 'garage', 'psych-rock', 'rock-n-roll', 'rockabilly']:
            return 'Rock'
        elif genre in ['hip-hop', 'rap', 'r-n-b']:
            return 'Hip-Hop / R&B'
        elif genre in ['electronic', 'edm', 'electro', 'trance', 'house', 'techno', 'deep-house', 'minimal-techno', 'progressive-house', 'club', 'dance', 'dancehall', 'detroit-techno', 'chicago-house', 'drum-and-bass', 'dubstep']:
            return 'Electronic'
        elif genre in ['classical', 'opera', 'piano', 'new-age']:
            return 'Classical'
        elif genre in ['jazz', 'blues', 'funk', 'soul', 'groove', 'gospel']:
            return 'Jazz / Soul'
        elif genre in ['country', 'folk', 'bluegrass', 'honky-tonk', 'singer-songwriter', 'songwriter']:
            return 'Country / Folk'
        elif genre in ['metal', 'heavy-metal', 'death-metal', 'black-metal', 'metalcore', 'hardcore', 'grindcore']:
            return 'Metal'
        elif genre in ['latin', 'latino', 'reggaeton', 'salsa', 'samba', 'brazil', 'forro', 'pagode', 'mpb', 'sertanejo', 'tango']:
            return 'Latin'
        elif genre in ['k-pop', 'j-pop', 'j-rock', 'anime', 'j-idol', 'j-dance', 'mandopop', 'cantopop']:
            return 'Asian Pop'
        elif genre in ['ambient', 'chill', 'sleep', 'study', 'acoustic']:
            return 'Chill / Ambient'
        elif genre in ['comedy', 'kids', 'children', 'disney', 'show-tunes']:
            return 'Entertainment / Kids'
        elif genre in ['indie', 'indie-pop', 'alternative']:
            return 'Indie / Alternative'
        else:
            return 'Other'

    def preprocess_data(self, original_dataset_path, processed_path):
        if os.path.exists(processed_path):
            print(f"Recuperat progrés des de {processed_path}")
            return pd.read_csv(processed_path)
            
        df = pd.read_csv(original_dataset_path)
        print("Arxiu carregat")

        df['genre_group'] = df['track_genre'].apply(self._simplify_genre)

        generes_a_excloure = ['Other', 'Entertainment / Kids', 'Chill / Ambient']
        df = df[~df['genre_group'].isin(generes_a_excloure)].copy()

        df = df.groupby('genre_group', group_keys=False).apply(self._remove_outliers_iqr)

        df = df[(df['year'].notna()) & (df['year'] != 0)]
        df = df[df['year'] >= 1980]
        df['decade'] = (df['year'] // 10) * 10

        df = df.sample(10000)

        df.to_csv(processed_path, index=False)
        return df