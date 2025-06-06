import pandas as pd
import sys

if __name__ == '__main__':

    # Llegeix el dataset
    df = pd.read_csv('data/dataset.csv')

    # Càlcul dels quartils i IQR
    Q1 = df['duration_ms'].quantile(0.25)
    Q3 = df['duration_ms'].quantile(0.75)
    IQR = Q3 - Q1

    # Límits per definir outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df_filtered = df[
        (df['duration_ms'] >= lower_bound) &
        (df['duration_ms'] <= upper_bound) &
        (df['speechiness'] < 0.66) &
        (df['instrumentalness'] < 0.9)
    ]

    # Desa el nou DataFrame en format CSV
    df_filtered.to_csv('data/filtered_dataset.csv', index=False)