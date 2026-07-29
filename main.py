from src.plotter import create_single_plot, create_comparison_plot, save_plot
from src.parser import load_csv_data, get_all_csvs
import shutil
import sys
import json
import os
import matplotlib
matplotlib.use('Agg')  # Evita dependência do Tkinter / interface gráfica


# Adiciona o diretório atual ao path para importações funcionarem no executável
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path):
    """Carrega o arquivo de configuração JSON."""
    if not os.path.exists(config_path):
        return {
            "data_dir": "data",
            "output_dir": "output",
            "plot_settings": {
                "theme": "light",
                "figure_size": [7, 6],
                "line_width": 1.5,
                "dpi": 300,
                "show_grid": False,
                "grid_alpha": 0.2,
                "x_log": False,
                "y_log": True,
                "x_limits": [-0.01, 0.1],
                "y_limits": [1e1, 1e4],
                "colors": ["#ff7f0e", "#00cc00"],
                "formats": ["png", "pdf", "svg"]
            },
            "labels": {
                "use_config_labels": True,
                "title": "",
                "x": "Y (m)",
                "y": "D95 (um)",
                "xlabel": "Y (m)",
                "ylabel": "D95 (um)"
            }
        }

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config.json: {e}")
        sys.exit(1)


def clear_output_dir(output_dir):
    """Remove todos os arquivos e subpastas dentro do diretório de output."""
    if os.path.exists(output_dir):
        print(f"[*] Limpando arquivos antigos em: {output_dir}...")
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"    [Aviso] Não foi possível deletar {item}: {e}")
        print("[+] Pasta output limpa com sucesso!\n")


def main():
    print("\n" + "="*45)
    print("    ANSYSPOST")
    print("="*45 + "\n")

    base_dir = os.getcwd()
    config_path = os.path.join(base_dir, 'config.json')
    config = load_config(config_path)

    data_dir = os.path.join(base_dir, config.get("data_dir", "data"))
    output_dir = os.path.join(base_dir, config.get("output_dir", "output"))

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    clear_output_dir(output_dir)

    args = sys.argv[1:]
    formats = config["plot_settings"].get("formats", ["png", "pdf", "svg"])

    if args:
        print(f"[+] Modo Comparação: Processando {len(args)} arquivos...")
        datasets = []
        for arg in args:
            path = arg if os.path.exists(arg) else os.path.join(data_dir, arg)
            if not os.path.exists(path):
                print(f"    [Aviso] Arquivo não encontrado: {arg}")
                continue

            df = load_csv_data(path)
            if df is not None:
                datasets.append(
                    (df, os.path.basename(path).replace('.csv', '')))

        if len(datasets) > 1:
            fig = create_comparison_plot(datasets, config)
            save_plot(fig, output_dir, "comparacao_resultados", formats)
            print(f"[OK] Gráfico comparativo gerado com sucesso.")
        elif len(datasets) == 1:
            df, name = datasets[0]
            fig = create_single_plot(df, name, config)
            save_plot(fig, output_dir, name, formats)
            print(f"[OK] Gráfico individual gerado para {name}.")
        else:
            print("[-] Nenhum dado válido encontrado para comparação.")

    else:
        csv_files = get_all_csvs(data_dir)

        if not csv_files:
            print(f"[-] Nenhum arquivo CSV encontrado em: {data_dir}")
            input("\nPressione Enter para sair...")
            return

        print(
            f"[+] Modo Automático: Processando {len(csv_files)} arquivos da pasta data...\n")

        success_count = 0
        for f in csv_files:
            file_name = os.path.basename(f)
            print(f"[*] Processando: {file_name}")

            try:
                df = load_csv_data(f)
                if df is not None:
                    fig = create_single_plot(df, f, config)
                    base_name = file_name.replace('.csv', '')
                    save_plot(fig, output_dir, base_name, formats)
                    success_count += 1
                else:
                    print(f"    [Erro] Falha ao ler dados de {file_name}")
            except Exception as e:
                print(f"    [Erro] Falha ao processar {file_name}: {e}")

        print(
            f"\n[OK] Concluído! {success_count} arquivos processados com sucesso.")

    print(f"[>] Verifique os resultados em: {output_dir}")
    print("\n" + "="*45)

    if not args:
        input("Pressione Enter para fechar.")


if __name__ == "__main__":
    main()
