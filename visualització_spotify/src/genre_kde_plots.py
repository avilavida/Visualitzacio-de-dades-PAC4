import numpy as np
import os
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import re
import matplotlib.colors as mcolors
from scipy.interpolate import CubicSpline


class GenreKDEVisualizer:
    def __init__(self, df, resolution=300, palette='tab10', sigma=5):
        self.df = df
        self.resolution = resolution
        self.palette = palette
        self.sigma = sigma

        self.x_grid, self.y_grid = np.meshgrid(
            np.linspace(0, 1, resolution),
            np.linspace(0, 1, resolution)
        )

        self.genres = sorted(df['genre_cluster'].dropna().unique())

        palette = plt.get_cmap('tab10')
        self.genre_color_map = {}
        for i, genre in enumerate(self.genres):
            # Agafa un color de la paleta, reciclant si hi ha més gèneres que colors disponibles
            color = palette(i % palette.N)
            self.genre_color_map[genre] = color


        self.default_margins = dict(left=0.1, right=0.8, top=0.9, bottom=0.1)
        self.default_fig_size = (8, 6)

    def _compute_kde(self, data, density_threshold=0.05, weights=None):
        if data.shape[0] < 2:
            return np.zeros_like(self.x_grid)

        values = np.vstack([data[:, 0], data[:, 1]])

        if weights is None:
            weights = np.ones(values.shape[1]) / values.shape[1]

        kde = gaussian_kde(values, weights=weights)

        grid_coords = np.vstack([self.x_grid.ravel(), self.y_grid.ravel()])
        density = kde(grid_coords).reshape(self.x_grid.shape)

        max_density = density.max()
        if max_density > 0:
            density = density / max_density
        else:
            density = np.zeros_like(density)

        density[density < density_threshold] = 0

        return density

    def _dominant_genre_map_smooth(self, kde_dict):
        # Construeix una matriu amb totes les KDEs en l'ordre de self.genre_color_map
        density_list = [kde_dict.get(genre, np.zeros_like(self.x_grid)) for genre in self.genres]
        density_stack = np.stack(density_list, axis=-1)  # shape (res, res, n_genres)

        max_indices = np.argmax(density_stack, axis=-1)
        max_density = np.max(density_stack, axis=-1)

        # Obtenim els colors corresponents als gèneres
        color_array = np.array([
            mcolors.to_rgb(self.genre_color_map[genre]) for genre in self.genres
        ])

        # Creem la imatge amb el color dominant per cada pixel
        img = color_array[max_indices]

        # Suavitzar la imatge amb filtre gaussià
        img_smooth = np.zeros_like(img)
        for i in range(3):
            img_smooth[..., i] = gaussian_filter(img[..., i], sigma=self.sigma)
        
        # El clip s'ha de fer sobre el mateix array (modificar img_smooth)
        img_smooth = np.clip(img_smooth, 0, 1)
        
        max_d = max_density.max()
        if max_d == 0:
            alpha = np.zeros_like(max_density)
        else:
            alpha = max_density / max_d
        alpha = np.clip(alpha, 0, 1)
        
        return img_smooth, alpha

    def plot_dominant_map(self, df, kdes_path, output_dir):
        # Si existeixen els KDEs al disc, els carreguem
        if os.path.exists(kdes_path):
            loaded = np.load(kdes_path, allow_pickle=True)
            kde_dict = loaded['kdes'][()]

        # Si no existeixen, hem de generar-los a partir de df
        else:
            if df is None:
                raise ValueError(f"No es pot generar KDEs perquè 'df' és None i no existeix cap fitxer: {kdes_path}")

            kde_dict = {}

            # Comptar punts per gènere
            genre_point_counts = {
                genre: len(df[df['genre_cluster'] == genre])
                for genre in self.genres
            }
            genre_point_counts = {g: c for g, c in genre_point_counts.items() if c >= 2}

            # Generar KDE per a cada gènere amb prou dades
            for genre in self.genres:
                count = genre_point_counts.get(genre, 0)
                if count < 2:
                    continue
                subset = df[df['genre_cluster'] == genre][['valence', 'energy']].values
                weights = np.ones(count) / count
                dens = self._compute_kde(subset, density_threshold=0.4, weights=weights)
                kde_dict[genre] = dens

            # Guardar KDEs al disc
            os.makedirs(os.path.dirname(kdes_path), exist_ok=True)
            np.savez(kdes_path, kdes=kde_dict)

        # Generar el mapa dominant a partir dels KDEs carregats
        img, alpha = self._dominant_genre_map_smooth(kde_dict)

        # Crear carpeta de sortida si no existeix
        os.makedirs(output_dir, exist_ok=True)

        # Paràmetres de visualització
        figsize = (8, 6)
        dpi = 300
        margins = dict(left=0.1, right=0.8, top=0.9, bottom=0.1)

        # Dibuixar la capa base
        self.plot_base_layer(img, alpha, dpi, figsize, margins, output_dir)
        
    def plot_elements(self, dpi=300, figsize=None, margins=None, output_dir=None):
        if output_dir is None:
            raise ValueError("output_dir must be specified")
        if margins is None:
            margins = dict(left=0.1, right=0.8, top=0.9, bottom=0.1)
        if figsize is None:
            figsize = (8, 6)

        os.makedirs(output_dir, exist_ok=True)

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        ax.axis('off')
        fig.patch.set_alpha(0)
        fig.subplots_adjust(**margins)

        left, right, top, bottom = margins['left'], margins['right'], margins['top'], margins['bottom']

        # Posicions relatives dins figura per línies
        # vertical a x=0.5 dins eix de dades
        x_fig = left + 0.5 * (right - left)
        # horitzontal a y=0.5 dins eix de dades
        y_fig = bottom + 0.5 * (top - bottom)

        # Línia vertical: de bottom a top, a x_fig
        line_vert = mlines.Line2D([x_fig, x_fig], [bottom, top],
                                color='black', linestyle='--', linewidth=1.2,
                                transform=fig.transFigure, figure=fig)
        fig.add_artist(line_vert)

        # Línia horitzontal: de left a right, a y_fig
        start_x = left + 0.075 * (right - left)
        end_x = left + 0.925 * (right - left)
        line_horiz = mlines.Line2D([start_x, end_x], [y_fig, y_fig],
                                 color='black', linestyle='--', linewidth=1.2,
                                 transform=fig.transFigure, figure=fig)
        fig.add_artist(line_horiz)

        label_kwargs = {
            "fontsize": 10,
            "color": "black",
            "ha": "center",
            "va": "center",
            "transform": fig.transFigure,
        }

        # Posicions als 4 quadrants
        fig.text(left + 0.25 * (right - left), bottom + 0.75 * (top - bottom), "Anger", **label_kwargs)
        fig.text(left + 0.25 * (right - left), bottom + 0.25 * (top - bottom), "Peacefulness", **label_kwargs)
        fig.text(left + 0.75 * (right - left), bottom + 0.75 * (top - bottom), "Euphoria", **label_kwargs)
        fig.text(left + 0.75 * (right - left), bottom + 0.25 * (top - bottom), "Sadness", **label_kwargs)

        fig.savefig(os.path.join(output_dir, "elements.png"), transparent=True)
        plt.close(fig)


    def plot_base_layer(self, img, alpha, dpi, figsize, margins, output_dir):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.imshow(np.clip(img, 0, 1), extent=(0, 1, 0, 1), origin='lower', alpha=np.clip(alpha, 0, 1), interpolation='bilinear')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        fig.subplots_adjust(**margins)
        fig.savefig(os.path.join(output_dir, "genre_map_data.png"), transparent=True)
        plt.close(fig)


    def plot_decorators(self, dpi=300, figsize=None, margins=None, output_dir=None, decade=None):
        if output_dir is None:
            raise ValueError("output_dir must be specified")
        if margins is None:
            margins = dict(left=0.1, right=0.8, top=0.9, bottom=0.1)
        if figsize is None:
            figsize = (8, 6)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        title = "Genre Dominance Map"
        ax.set_title(title, fontsize=16, pad=15)

        ax.set_xlabel("Valence", fontsize=12)
        ax.set_ylabel("Energy", fontsize=12)

        legend_handles = [
            plt.Line2D([0], [0], marker='o', color='w', label=genre,
                       markerfacecolor=self.genre_color_map[genre], markersize=10)
            for genre in self.genre_color_map
        ]
        ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
                  fontsize=10, framealpha=0.95)
        
        if decade is not None:
            ax.text(0.95, 0.05, f"Decade {decade}", fontsize=15, color='#000078',
                ha='right', va='bottom', transform=ax.transAxes)

        fig.patch.set_alpha(0)
        ax.imshow(np.zeros((10, 10, 4)), alpha=0)  # imatge dummy per forçar escala

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "genre_map_decoration.png")
        fig.subplots_adjust(**margins)
        fig.savefig(output_path, transparent=True)
        plt.close(fig)

    def plot_all_layers(self, kdes_path, output_dir):
        if not os.path.exists(kdes_path):
            return
        
        os.makedirs(output_dir, exist_ok=True)
        loaded = np.load(kdes_path, allow_pickle=True)
        kdes = loaded['kdes'].item()

        if not kdes:
            print(f"No s'han carregat KDEs des de {kdes_path}")
            return

        for genre in self.genre_color_map:
            safe_genre = self._sanitize_filename(genre)
            plot_path = os.path.join(output_dir, f"{safe_genre}.png")
            self._plot_highlighted_layer(genre, kdes, plot_path)

    def _plot_highlighted_layer(self, genre, kdes, save_path):
        if genre not in kdes:
            print(f"Gènere '{genre}' no trobat a les KDEs.")
            return
    
        density = kdes[genre]
    
        rgba = np.zeros((self.resolution, self.resolution, 4))
        rgba[..., :3] = mcolors.to_rgb(self.genre_color_map[genre])
        rgba[..., 3] = density

        figsize = (8, 6)
        dpi = 300
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.imshow(rgba, extent=(0, 1, 0, 1), origin='lower')
        ax.axis('off')
        fig.subplots_adjust(left=0.1, right=0.8, top=0.9, bottom=0.1)
        fig.savefig(save_path, dpi=dpi, transparent=True)
        plt.close(fig)

    def _sanitize_filename(self, name):
        name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        return name
    
    def spline_interpolate_kdes(self, kde_dicts, decades, target_year, threshold=0.05, d1=None, step=None):
        if d1 == None or step == None:
            print("S'ha d'especificar d1 i step")
            return
        
        filename = f'data/kdes_data/kdes_genres_{int(d1)}_{step}.npz'

        if os.path.exists(filename):
            return
        
        interpolated = {}
        all_genres = set().union(*[k.keys() for k in kde_dicts])

        for genre in all_genres:
            # Agafa tots els KDEs per aquest gènere en ordre de dècada
            kde_stack = []
            available_decades = []
            for d, kde in zip(decades, kde_dicts):
                if genre in kde:
                    kde_stack.append(kde[genre])
                    available_decades.append(d)

            if len(kde_stack) < 2:
                continue  # No es pot interpolar
            
            kde_stack = np.array(kde_stack)  # shape: (num_decades, H, W)

            # Interpolem cada punt del grid
            H, W = kde_stack.shape[1], kde_stack.shape[2]
            interp_kde = np.zeros((H, W))

            for i in range(H):
                for j in range(W):
                    y_values = kde_stack[:, i, j]
                    cs = CubicSpline(available_decades, y_values, extrapolate=True)
                    interp_kde[i, j] = cs(target_year)

            # Tallem valors negatius i fem threshold
            interp_kde = np.where(interp_kde >= threshold, interp_kde, 0.0)
            interpolated[genre] = interp_kde
        
        np.savez(filename, kdes=interpolated)