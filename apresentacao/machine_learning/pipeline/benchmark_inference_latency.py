#!/usr/bin/env python3
"""
Benchmark de latência de inferência para os modelos de decision trees
Mede tempo médio, percentis e compara com diferentes objetivos
"""

import pickle
import numpy as np
import time
import statistics
from pathlib import Path

def benchmark_model_inference(model_path='../models/decision_trees_per_topology.pkl', n_iterations=10000):
    """
    Mede latência de inferência dos modelos.
    
    Args:
        model_path: Caminho para o arquivo pickle com os modelos
        n_iterations: Número de iterações para benchmark
    """
    
    print("="*80)
    print("BENCHMARK DE LATÊNCIA DE INFERÊNCIA")
    print("="*80)
    
    # Carregar modelos
    print(f"\nCarregando modelos de: {model_path}")
    with open(model_path, 'rb') as f:
        models = pickle.load(f)
    
    print(f"✓ Modelos carregados")
    
    # Criar dados de teste sintéticos (features aleatórias mas realistas)
    np.random.seed(42)
    
    # Obter features de um modelo qualquer para saber o tamanho
    first_topo = list(models.keys())[0]
    first_obj = list(models[first_topo].keys())[0]
    features = models[first_topo][first_obj]['features']
    n_features = len(features)
    
    print(f"\nNúmero de features: {n_features}")
    print(f"Iterações de benchmark: {n_iterations}")
    
    # Gerar dados de teste
    X_test = np.random.rand(n_iterations, n_features).astype(np.float32)
    
    results = {}
    
    # Testar cada topologia e objetivo
    for topo_name in sorted(models.keys()):
        results[topo_name] = {}
        
        for obj_key in sorted(models[topo_name].keys()):
            model_info = models[topo_name][obj_key]
            model = model_info['model']
            features_list = model_info.get('features', features)
            
            # Ajustar X_test se necessário
            if len(features_list) != n_features:
                X_test_obj = np.random.rand(n_iterations, len(features_list)).astype(np.float32)
            else:
                X_test_obj = X_test
            
            # Warm-up (primeiras predições são mais lentas)
            _ = model.predict(X_test_obj[:100])
            
            # Medir latência
            latencies = []
            
            for i in range(n_iterations):
                start = time.perf_counter()
                _ = model.predict(X_test_obj[i:i+1])
                end = time.perf_counter()
                latencies.append((end - start) * 1000)  # Converter para ms
            
            # Calcular estatísticas
            latencies_sorted = sorted(latencies)
            mean_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            p999_latency = np.percentile(latencies, 99.9)
            min_latency = min(latencies)
            max_latency = max(latencies)
            std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
            
            results[topo_name][obj_key] = {
                'mean': mean_latency,
                'median': median_latency,
                'p95': p95_latency,
                'p99': p99_latency,
                'p999': p999_latency,
                'min': min_latency,
                'max': max_latency,
                'std': std_latency
            }
            
            print(f"\n{topo_name.upper()} / {obj_key.upper()}:")
            print(f"  Média:     {mean_latency:.4f} ms")
            print(f"  Mediana:   {median_latency:.4f} ms")
            print(f"  P95:       {p95_latency:.4f} ms")
            print(f"  P99:       {p99_latency:.4f} ms")
            print(f"  P99.9:     {p999_latency:.4f} ms")
            print(f"  Min:       {min_latency:.4f} ms")
            print(f"  Max:       {max_latency:.4f} ms")
            print(f"  Std Dev:   {std_latency:.4f} ms")
    
    # Resumo geral
    print("\n" + "="*80)
    print("RESUMO GERAL (média entre todos os modelos)")
    print("="*80)
    
    all_means = []
    all_p99s = []
    
    for topo_name in results.keys():
        for obj_key in results[topo_name].keys():
            all_means.append(results[topo_name][obj_key]['mean'])
            all_p99s.append(results[topo_name][obj_key]['p99'])
    
    overall_mean = statistics.mean(all_means)
    overall_p99 = statistics.mean(all_p99s)
    overall_max_p99 = max(all_p99s)
    
    print(f"\nTempo médio (média entre modelos): {overall_mean:.4f} ms")
    print(f"P99 médio (média entre modelos):    {overall_p99:.4f} ms")
    print(f"P99 máximo (pior caso):             {overall_max_p99:.4f} ms")
    
    # Salvar resultados
    import json
    output_file = '../results/inference_latency_benchmark.json'
    Path('../results').mkdir(exist_ok=True)
    
    # Converter para formato serializável
    results_serializable = {}
    for topo in results:
        results_serializable[topo] = {}
        for obj in results[topo]:
            results_serializable[topo][obj] = {
                k: float(v) for k, v in results[topo][obj].items()
            }
    
    results_serializable['summary'] = {
        'overall_mean_ms': float(overall_mean),
        'overall_p99_ms': float(overall_p99),
        'overall_max_p99_ms': float(overall_max_p99),
        'n_iterations': n_iterations
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_serializable, f, indent=2)
    
    print(f"\n✓ Resultados salvos em: {output_file}")
    
    return results

if __name__ == '__main__':
    benchmark_model_inference(n_iterations=10000)

