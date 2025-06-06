import pandas as pd
import os
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score

def plot_elbow(X):
    inertia = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        inertia.append(kmeans.inertia_)

    plt.plot(range(1, 11), inertia, marker='o')
    plt.xlabel('Nombre de clústers (k)')
    plt.ylabel('Inèrcia')
    plt.title('Mètode del colze')
    plt.grid(True)
    plt.show()

def plot_silhouette(X):
    silhouette_scores = []
    for k in range(2, 11):
        print(f'Testing k = {k}')
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        silhouette_scores.append(score)

    plt.plot(range(2, 11), silhouette_scores, marker='o')
    plt.xlabel('Nombre de clústers (k)')
    plt.ylabel('Silhouette Score')
    plt.title('Silhouette Score per k')
    plt.grid(True)
    plt.show()

def get_clusters_df(df, plot_bool, processed_path, k_means_file):
    if os.path.exists(k_means_file):
        print(f"Recuperat progrés des de {k_means_file}")
        return pd.read_csv(k_means_file)
    
    df = pd.read_csv(processed_path)
    # 1. Calcular mitjanes de valence i energy per grup de gènere
    genre_summary = df.groupby('genre_group')[['valence', 'energy']].mean().reset_index()

    # 2. Aplicar KMeans
    k = 7
    kmeans = KMeans(n_clusters=k, random_state=42)
    genre_summary['cluster'] = kmeans.fit_predict(genre_summary[['valence', 'energy']])

    print("📊 Composició de clústers:")
    for cluster_id in sorted(genre_summary['cluster'].unique()):
        cluster_genres = genre_summary[genre_summary['cluster'] == cluster_id]['genre_group'].tolist()
        print(f"Cluster {cluster_id}: {cluster_genres}")

    # 3. Assignació de noms als clusters manualment
    cluster_to_name = {
        0: 'Urban & Latin',
        1: 'Indie / Asian / Jazz',
        2: 'Classical',
        3: 'Metal',
        4: 'Pop & Rock',
        5: 'Folk & Country',
        6: 'Electronic'
    }

    genre_summary['genre_cluster'] = genre_summary['cluster'].map(cluster_to_name)

    # 4. Merge amb el DataFrame original
    df = df.merge(genre_summary[['genre_group', 'genre_cluster']], on='genre_group', how='left')

    df.to_csv(k_means_file, index=False)

    if not plot_bool:
        return df
    # 5. Visualització
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=genre_summary, x='valence', y='energy', hue='genre_cluster', palette='tab10', s=100)

    for _, row in genre_summary.iterrows():
        plt.text(row['valence'] + 0.01, row['energy'] + 0.01, row['genre_group'], fontsize=9)

    plt.title('Clusters de gèneres segons valence i energy')
    plt.xlabel('Valence')
    plt.ylabel('Energy')
    plt.legend(title='Gènere agrupat')
    plt.tight_layout()
    plt.show()

    return df