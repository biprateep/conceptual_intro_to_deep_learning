import matplotlib.pyplot as plt

# set some rc params and set globa variables


# figure defaults for AASTEX AJ

COLUMN_WIDTH = 242.26653 / 72.27  # in inches
TEXT_WIDTH = 513.11743 / 72.27
SMALL_SIZE = 9  # in pts
NORMAL_SIZE = 10
BIG_SIZE = 12
FONT_FAMILY = "Nimbus Roman No9 L"


params = {
    "font.family": FONT_FAMILY,
    "font.size": NORMAL_SIZE,
    "axes.titlesize": NORMAL_SIZE,
    "axes.labelsize": NORMAL_SIZE,
    "xtick.labelsize": SMALL_SIZE,
    "ytick.labelsize": SMALL_SIZE,
    "xtick.top": True,
    "ytick.right": True,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "legend.fontsize": NORMAL_SIZE,
    "figure.facecolor": "w",
    "figure.dpi": 300,
    "mathtext.fontset": "cm",
}

plt.rcParams.update(params)


def plot_kiel_scatter_density(teff_data, logg_data, feh_data, scatter=False, **kwargs):
    """
    Plots a Kiel diagram (Teff vs. log g) using scatter_density, colored by a third quantity (e.g., Fe/H).

    Args:
        teff_data (array-like): Effective temperature data.
        logg_data (array-like): Surface gravity data.
        feh_data (array-like): Data for color-coding the points (e.g., metallicity).
        **kwargs: Additional keyword arguments for plot customization.
            figsize (tuple): Figure size. Default uses TEXT_WIDTH if available, else (7,7).
            vmin (float): Minimum value for the color scale. Default: -2.
            vmax (float): Maximum value for the color scale. Default: 0.5.
            dpi (int): Dots per inch for the scatter density plot. Default: 120.
            cmap (str): Colormap for the scatter density plot. Default: 'viridis'.
            xlabel (str): Label for the x-axis. Default: 'Effective Temperature (Teff) [K]'.
            ylabel (str): Label for the y-axis. Default: 'Surface Gravity (log(g))'.
            title (str): Title for the plot. Default: 'Kiel Diagram of APOGEE DR17 Stars'.
            colorbar_label (str): Label for the colorbar. Default: '[Fe/H]'.

    Returns:
        tuple: (fig, ax, density_map)
            fig (matplotlib.figure.Figure): The figure object.
            ax (matplotlib.axes.Axes): The axes object with the scatter density plot.
            density_map (matplotlib.collections.PathCollection): The scatter density plot object.
    """
    # Default figsize depends on TEXT_WIDTH if it's globally defined
    default_figsize = (7, 7)
    if "TEXT_WIDTH" in globals():
        try:
            # Ensure TEXT_WIDTH is a number if it exists
            if isinstance(globals()["TEXT_WIDTH"], (int, float)):
                default_figsize = (
                    globals()["TEXT_WIDTH"] * 0.8,
                    globals()["TEXT_WIDTH"] * 0.8,
                )
        except TypeError:  # Handles if TEXT_WIDTH is not a number
            pass  # Keeps default_figsize as (7,7)

    figsize = kwargs.get("figsize", default_figsize)

    fig = plt.figure(figsize=figsize)
    if scatter:
        ax = fig.add_subplot(1, 1, 1,)
        scatter = ax.scatter(teff_data,
            logg_data,
            c=feh_data,
            vmin=kwargs.get("vmin", -2),
            vmax=kwargs.get("vmax", 0.5),
    
            cmap=kwargs.get("cmap", "viridis"),)
    else:
        ax = fig.add_subplot(1, 1, 1, projection="scatter_density")

        scatter = ax.scatter_density(
            teff_data,
            logg_data,
            c=feh_data,
            vmin=kwargs.get("vmin", -2),
            vmax=kwargs.get("vmax", 0.5),
            dpi=kwargs.get("dpi", 120),
            cmap=kwargs.get("cmap", "viridis"),
        )

    cbar = fig.colorbar(
        scatter, ax=ax, label=kwargs.get("colorbar_label", "[Fe/H]")
    )

    ax.set_xlabel(kwargs.get("xlabel", "Effective Temperature (Teff) [K]"))
    ax.set_ylabel(kwargs.get("ylabel", "Surface Gravity (log(g))"))  # Matched original
    ax.set_title(
        kwargs.get("title", "Kiel Diagram of APOGEE DR17 Stars")
    )  # Matched original

    ax.invert_xaxis()
    ax.invert_yaxis()

    return fig, ax
