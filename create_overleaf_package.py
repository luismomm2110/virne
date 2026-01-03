#!/usr/bin/env python3
"""
Script para criar arquivo ZIP com todos os arquivos necessários para Overleaf
"""
import os
import shutil
import zipfile
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
ARTIGO_DIR = BASE_DIR / 'apresentacao' / 'artigo_conf'
TEMP_DIR = BASE_DIR / 'overleaf_package'
ZIP_FILE = BASE_DIR / 'artigo_overleaf.zip'

# Lista de arquivos necessários
FILES_TO_COPY = [
    'artigo_multiobjetivo.tex',
    'artigo_multiobjetivo_en.tex',
    'references.bib',
    # Imagens
    'tree_structure.png',
    'tree_example_path.png',
    'topologies_comparison.png',
    'waxman_16_topology.png',
    'baseline_comparison_chart.png',
    'real_performance_chart.png',
    'tree_visualization_example.png',
    'per_objective_rac.png',
    'per_objective_lrc.png',
    'per_objective_lar.png',
    'inference_latency_cdf.png',
    'algorithm_comparison_all_metrics.png',
]

def fix_image_paths(tex_file):
    """Ajusta caminhos de imagens no arquivo .tex"""
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajusta o caminho da imagem algorithm_comparison_all_metrics
    old_path = '../machine_learning/models/algorithm_comparison_all_metrics'
    new_path = 'algorithm_comparison_all_metrics'
    content = content.replace(old_path, new_path)
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Ajustado: {tex_file.name}")

def main():
    print("📦 Criando pacote para Overleaf...")
    
    # Limpa diretório temporário se existir
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copia arquivos
    print("\n📋 Copiando arquivos...")
    for file_name in FILES_TO_COPY:
        src = ARTIGO_DIR / file_name
        if src.exists():
            dst = TEMP_DIR / file_name
            shutil.copy2(src, dst)
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} (não encontrado)")
    
    # Ajusta caminhos nos arquivos .tex
    print("\n🔧 Ajustando caminhos de imagens...")
    for tex_file in TEMP_DIR.glob('*.tex'):
        fix_image_paths(tex_file)
    
    # Cria ZIP
    print("\n📦 Criando arquivo ZIP...")
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()
    
    with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in TEMP_DIR.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(TEMP_DIR)
                zipf.write(file_path, arcname)
                print(f"  ✓ {arcname}")
    
    # Limpa diretório temporário
    shutil.rmtree(TEMP_DIR)
    
    # Mostra tamanho do ZIP
    size_mb = ZIP_FILE.stat().st_size / (1024 * 1024)
    print(f"\n✅ ZIP criado com sucesso!")
    print(f"   Arquivo: {ZIP_FILE}")
    print(f"   Tamanho: {size_mb:.2f} MB")
    print(f"\n📤 Pronto para upload no Overleaf!")

if __name__ == '__main__':
    main()

