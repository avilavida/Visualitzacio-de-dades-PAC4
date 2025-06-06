import json

class Summarizer():
    def __init__(self):
        pass

    def summarize_genres(self, df, path):
        summary = df.groupby('genre_cluster').agg(
            num_songs=('genre_cluster', 'count'),
            avg_energy=('energy', 'mean'),
            avg_valence=('valence', 'mean')
        ).reset_index()
        
        summary['avg_energy'] = summary['avg_energy'].round(2)
        summary['avg_valence'] = summary['avg_valence'].round(2)
        summary_dict = summary.set_index('genre_cluster').to_dict(orient='index')
        
        # Estadístiques per dècada i gènere
        decades_group = df.groupby(['decade', 'genre_cluster']).agg(
            num_songs=('genre_cluster', 'count'),
            avg_energy=('energy', 'mean'),
            avg_valence=('valence', 'mean')
        ).reset_index()
        
        # Arrodonim
        decades_group['avg_energy'] = decades_group['avg_energy'].round(2)
        decades_group['avg_valence'] = decades_group['avg_valence'].round(2)
        
        # Creem diccionari amb la jerarquia decade -> genre -> stats
        decades_dict = {}
        for _, row in decades_group.iterrows():
            decade = str(row['decade'])      # <-- arreglat aquí
            genre = row['genre_cluster']
            stats = {
                'num_songs': int(row['num_songs']),
                'avg_energy': row['avg_energy'],
                'avg_valence': row['avg_valence']
            }
            if decade not in decades_dict:
                decades_dict[decade] = {}
            decades_dict[decade][genre] = stats
        
        # Metadades
        metadata = {
            'total_records': len(df)
        }
        
        # JSON final
        final_json = {
            'metadata': metadata,
            'genres': summary_dict,
            'decades': decades_dict
        }
        
        with open(path, 'w') as f:
            json.dump(final_json, f, indent=4)