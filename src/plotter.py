import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def setup_style(settings):
    """Configura o estilo global do Matplotlib para visualização científica."""
    theme = settings.get("theme", "light")

    if theme == "dark":
        plt.style.use("dark_background")
    else:
        plt.style.use("seaborn-v0_8-whitegrid")

    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": [
            "DejaVu Serif",
            "Times New Roman",
            "Palatino",
            "serif",
        ],
        "text.usetex": settings.get("use_latex", False),
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": settings.get("dpi", 300),
        "savefig.bbox": "tight",
        "axes.grid": settings.get("show_grid", False),
        "grid.alpha": settings.get("grid_alpha", 0.3),
        "grid.linestyle": "--",
    })


def _apply_scientific_style(
    ax, config, default_title, default_xlabel, default_ylabel
):
    """Aplica ajustes estéticos e força limites/escalas dos eixos."""
    settings = config["plot_settings"]
    labels_config = config["labels"]

    # 1. Escalas (Linear ou Logarítmica)
    if settings.get("x_log", False):
        ax.set_xscale("log")
    else:
        ax.set_xscale("linear")

    if settings.get("y_log", False):
        ax.set_yscale("log")
    else:
        ax.set_yscale("linear")

    # 2. Aplicação Estrita dos Limites dos Eixos
    if "x_limits" in settings and settings["x_limits"]:
        ax.set_xlim(settings["x_limits"])
    if "y_limits" in settings and settings["y_limits"]:
        ax.set_ylim(settings["y_limits"])

    # 3. Rótulos dos Eixos (Suporta tanto 'x'/'y' quanto 'xlabel'/'ylabel')
    if labels_config.get("use_config_labels", True):
        title = labels_config.get("title", default_title)
        xlabel = (
            labels_config.get("x")
            or labels_config.get("xlabel")
            or default_xlabel
        )
        ylabel = (
            labels_config.get("y")
            or labels_config.get("ylabel")
            or default_ylabel
        )

        if title:
            ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        if default_title:
            ax.set_title(default_title)
        ax.set_xlabel(default_xlabel)
        ax.set_ylabel(default_ylabel)

    # 4. Estilo de Caixa Científica (Ticks voltados para DENTRO)
    ax.tick_params(direction="in", which="both", top=True, right=True)


def create_single_plot(df, filename, config):
    """Gera uma visualização automática para um único arquivo CSV."""
    settings = config["plot_settings"]
    setup_style(settings)
    num_cols = len(df.columns)
    base_name = os.path.basename(filename).replace(".csv", "")

    if num_cols < 2:
        print(f"    [Aviso] {base_name} possui menos de 2 colunas. Pulando.")
        return None

    fig, ax = plt.subplots(figsize=settings.get("figure_size", [7, 6]))

    if num_cols == 2:
        x_col, y_col = df.columns[0], df.columns[1]
        ax.plot(
            df[x_col],
            df[y_col],
            color=settings["colors"][0],
            linewidth=settings.get("line_width", 1.5),
            label=f"Dados: {base_name}",
        )
        ax.legend(frameon=False)
        _apply_scientific_style(ax, config, "", x_col, y_col)

    elif num_cols >= 3:
        x_col, y_col = df.columns[0], df.columns[1]
        z_col = df.columns[-1]
        s = 11 if len(df) > 5000 else 20
        sc = ax.scatter(
            df[x_col],
            df[y_col],
            c=df[z_col],
            cmap="turbo",
            s=s,
            alpha=1,
            edgecolors="none",
        )
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label(z_col)
        _apply_scientific_style(
            ax, config, f"Distribuição de {z_col} ({base_name})", x_col, y_col
        )

    plt.tight_layout()
    return fig


def create_comparison_plot(datasets, config):
    """Gera um gráfico comparativo agrupando múltiplos arquivos CSV."""
    settings = config["plot_settings"]
    setup_style(settings)

    fig, ax = plt.subplots(figsize=settings.get("figure_size", [7, 6]))

    colors = settings.get(
        "colors", ["#ff6600", "#00cc00", "#ff6600", "#00cc00"])

    x_label, y_label = None, None

    for i, (df, name) in enumerate(datasets):
        if df is None or df.empty or len(df.columns) < 2:
            continue

        x_col, y_col = df.columns[0], df.columns[1]
        if not x_label:
            x_label, y_label = x_col, y_col

        color = colors[i % len(colors)]

        # Regra por ordem alfabética da pasta data/:
        # Índices 0 e 1 (paper): Linha Tracejada (--) sem marcadores
        # Índices 2 e 3 (simulation): Linha Contínua (-) sem marcadores
        if i < 2:
            linestyle = "--"
        else:
            linestyle = "-"

        ax.plot(
            df[x_col],
            df[y_col],
            label=name,
            color=color,
            linestyle=linestyle,
            linewidth=settings.get("line_width", 1.5)
        )

    _apply_scientific_style(
        ax, config, "", x_label if x_label else "X", y_label if y_label else "Y")
    ax.legend()

    plt.tight_layout()
    return fig


def save_plot(fig, output_dir, base_name, formats):
    """Salva o gráfico nos formatos especificados."""
    if fig is None:
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for fmt in formats:
        path = os.path.join(output_dir, f"{base_name}.{fmt}")
        fig.savefig(path, format=fmt, dpi=300)
        print(f"    [Exportado] {path}")

    plt.close(fig)
