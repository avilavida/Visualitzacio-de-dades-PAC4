import os
import pandas as pd
from api_data_merger import APIDataMerger


if __name__ == '__main__':

    spotify_client_id = 'spotify_client_id'
    spotify_client_secret = 'spotify_client_secret'

    discogs_token = 'discogs_token'

    save_path = 'data/completed_dataset.csv'

    if os.path.exists(save_path):
        df = pd.read_csv(save_path)
        print(f'Recuperat progrés des de {save_path}')
    else:
        df = pd.read_csv('data/filtered_dataset.csv')
        df['year'] = None
        print('Arxiu carregat')

    adm = APIDataMerger(df, spotify_client_id, spotify_client_secret, discogs_token)
    adm.complete_dataset(save_path)