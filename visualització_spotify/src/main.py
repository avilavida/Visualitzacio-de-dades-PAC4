from data_processor import DataProcessor
from data_summarizer import Summarizer
from genre_kde_plots import GenreKDEVisualizer
import k_means
import numpy as np

if __name__ == '__main__':
    original_dataset_path = 'data/input_data.csv'
    processed_path = 'data/processed_data.csv'

    preprocessor = DataProcessor()
    df = preprocessor.preprocess_data(original_dataset_path, processed_path)

    k_means_file = 'data/k_means_df.csv'
    df = k_means.get_clusters_df(df, True, processed_path, k_means_file)

    summarizer = Summarizer()
    summarizer.summarize_genres(df, 'data/genres_summary.json')

    visualizer = GenreKDEVisualizer(df)
    visualizer.plot_elements(output_dir='plots/common')

    decades = sorted(df['decade'].unique())
    # Generació mapes kde
    for decade in decades:
        decade_str = str(int(decade))
        subset = df[df['decade'] == decade]
        visualizer.plot_decorators(output_dir=f'plots/{decade_str}', decade=decade_str)
        visualizer.plot_dominant_map(subset, f'data/kdes_data/kdes_genres_{decade_str}.npz', f'plots/{decade_str}')
        visualizer.plot_all_layers(f'data/kdes_data/kdes_genres_{decade_str}.npz', f'plots/{decade_str}')

    # Generació mapes kde interpolats
    decades = sorted(df['decade'].unique())
    kde_dicts = []

    for d in decades:
        kde = np.load(f'data/kdes_data/kdes_genres_{int(d)}.npz', allow_pickle=True)['kdes'][()]
        kde_dicts.append(kde)

    num_interpolated_frames = 5

    for i in range(len(decades) - 1):
        d1 = decades[i]
        d2 = decades[i + 1]

        for step in range(1, num_interpolated_frames + 1):
            alpha = step / (num_interpolated_frames + 1)
            interpolated_year = (1 - alpha) * d1 + alpha * d2

            visualizer.spline_interpolate_kdes(
                kde_dicts=kde_dicts,
                decades=decades,
                target_year=interpolated_year,
                threshold=0.4,
                d1=d1,
                step=step
            )

    for i in range(len(decades) - 1):
        d1 = decades[i]

        for step in range(1, num_interpolated_frames + 1):
            kde_path = f'data/kdes_data/kdes_genres_{int(d1)}_{step}.npz'
            output_folder = f'plots/{int(d1)}/interpolated_{step}'
            visualizer.plot_dominant_map(None, kde_path, output_folder)
            visualizer.plot_all_layers(kde_path, output_folder)