"""
Comparator - Compara performance do XGBoost vs algoritmos fixos
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List
from pathlib import Path

from .predictor import VNEPredictor


class PerformanceComparator:
    """Compara XGBoost selector vs algoritmos fixos"""

    def __init__(self, model_path: str):
        """
        Args:
            model_path: Caminho do modelo treinado
        """
        self.predictor = VNEPredictor()
        self.predictor.load_model(model_path)
        self.algorithms = [
            'mip', 'mcts', 'pl_rank', 'rw_rank_bfs',
            'ga_meta', 'sa_meta', 'd_round', 'r_round'
        ]

    def load_simulation_data(self, filepath: str = 'vnr_aggregated_data.csv') -> pd.DataFrame:
        """Carrega dados de simulação"""
        print(f"\n📂 Carregando dados de simulação: {filepath}")
        df = pd.read_csv(filepath)
        df = df[df['event_type'] == 1].copy()  # Apenas eventos de chegada
        print(f"   Total de registros: {len(df):,}")
        return df

    def simulate_xgboost_selection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simula o XGBoost escolhendo algoritmos para cada VNR

        Para cada VNR única:
        1. Extrai features
        2. Prediz melhor algoritmo
        3. Pega resultado desse algoritmo dos dados reais

        Returns:
            DataFrame com resultados do XGBoost
        """
        print("\n🎯 Simulando XGBoost selector...")

        # Identificar VNRs únicas
        df['vnr_uid'] = (
            df['v_net_id'].astype(str) + '_' +
            df['seed'].astype(str) + '_' +
            df['event_time'].astype(int).astype(str)
        )

        # Get algorithms that the model knows
        known_algorithms = set(self.predictor.label_encoder.classes_)
        print(f"   Algoritmos conhecidos pelo modelo: {known_algorithms}")

        results = []
        vnr_groups = df.groupby('vnr_uid')
        total_vnrs = len(vnr_groups)
        skipped = 0

        for i, (vnr_uid, group) in enumerate(vnr_groups, 1):
            if i % 500 == 0:
                print(f"   Processando: {i}/{total_vnrs} VNRs...")

            # Extrair features (mesmas para todos os algoritmos)
            vnr_features = group.iloc[0]
            features_dict = {
                'v_net_num_nodes': vnr_features['v_net_num_nodes'],
                'v_net_num_egdes': vnr_features['v_net_num_egdes'],
                'v_net_demand': vnr_features['v_net_demand'],
                'v_net_node_demand': vnr_features['v_net_node_demand'],
                'v_net_link_demand': vnr_features['v_net_link_demand'],
                'v_net_lifetime': vnr_features['v_net_lifetime'],
                'v_net_arrival_time': vnr_features['v_net_arrival_time'],
                'p_net_available_resource': vnr_features['p_net_available_resource'],
                'p_net_node_available_resource': vnr_features['p_net_node_available_resource'],
                'p_net_link_available_resource': vnr_features['p_net_link_available_resource'],
                'p_net_node_resource_utilization': vnr_features['p_net_node_resource_utilization'],
                'p_net_link_resource_utilization': vnr_features['p_net_link_resource_utilization'],
                'inservice_count': vnr_features['inservice_count'],
            }

            # Check if this VNR has results for all known algorithms
            tested_algorithms = set(group['algorithm'].unique())
            if not known_algorithms.issubset(tested_algorithms):
                # Skip VNRs that don't have results for all algorithms the model knows
                skipped += 1
                continue

            # Predizer algoritmo
            selected_algo, confidence, _ = self.predictor.predict_single(features_dict)

            # Pegar resultado desse algoritmo nos dados reais
            algo_result = group[group['algorithm'] == selected_algo]

            if len(algo_result) == 0:
                # Should not happen since we checked above
                skipped += 1
                continue

            algo_result = algo_result.iloc[0]

            results.append({
                'vnr_uid': vnr_uid,
                'v_net_id': vnr_features['v_net_id'],
                'seed': vnr_features['seed'],
                'selected_algorithm': selected_algo,
                'confidence': confidence,
                'result': algo_result['result'],
                'solving_time': algo_result['solving_time'],
                'v_net_r2c_ratio': algo_result['v_net_r2c_ratio'],
            })

        result_df = pd.DataFrame(results)
        print(f"   ✓ Simulação concluída: {len(result_df)} VNRs")
        print(f"   ⚠ Ignoradas: {skipped} VNRs (não têm resultados para todos os algoritmos conhecidos)")
        return result_df

    def calculate_metrics(
        self,
        df: pd.DataFrame,
        algorithm: str = None
    ) -> Dict[str, float]:
        """
        Calcula métricas de performance

        Args:
            df: DataFrame com resultados
            algorithm: Nome do algoritmo (None para XGBoost)

        Returns:
            Dicionário com métricas
        """
        if algorithm:
            df = df[df['algorithm'] == algorithm].copy()

        # Taxa de aceitação
        acceptance_rate = df['result'].mean()

        # Tempo médio (apenas aceitas)
        accepted = df[df['result'] == True]
        if len(accepted) > 0:
            avg_time = accepted['solving_time'].mean()
            avg_r2c = accepted['v_net_r2c_ratio'].mean()
        else:
            avg_time = 0.0
            avg_r2c = 0.0

        return {
            'acceptance_rate': acceptance_rate,
            'avg_time': avg_time,
            'avg_r2c': avg_r2c,
            'n_total': len(df),
            'n_accepted': len(accepted),
        }

    def compare_all_algorithms(
        self,
        data_file: str = 'vnr_aggregated_data.csv',
        output_file: str = 'xgboost_v2/outputs/comparison_results.csv'
    ) -> pd.DataFrame:
        """
        Compara XGBoost com todos os algoritmos fixos

        Returns:
            DataFrame com comparação
        """
        print("\n" + "="*70)
        print("COMPARAÇÃO: XGBoost vs Algoritmos Fixos")
        print("="*70)

        # 1. Carregar dados
        df = self.load_simulation_data(data_file)

        # 2. Simular XGBoost
        xgb_results = self.simulate_xgboost_selection(df)
        xgb_metrics = self.calculate_metrics(xgb_results)

        print("\n📊 Performance do XGBoost:")
        print(f"   Taxa de Aceitação: {xgb_metrics['acceptance_rate']:.2%}")
        print(f"   Tempo Médio:       {xgb_metrics['avg_time']:.2f}s")
        print(f"   R2C Médio:         {xgb_metrics['avg_r2c']:.4f}")

        # 3. Calcular métricas de cada algoritmo fixo
        print("\n📊 Performance dos Algoritmos Fixos:")

        # Filter to only VNRs that XGBoost tested
        tested_vnr_uids = set(xgb_results['vnr_uid'])
        df_filtered = df[df['vnr_uid'].isin(tested_vnr_uids)]
        print(f"   Comparando em {len(tested_vnr_uids)} VNRs (mesmas testadas pelo XGBoost)")

        comparisons = []

        for algo in self.algorithms:
            algo_df = df_filtered[df_filtered['algorithm'] == algo]
            if len(algo_df) == 0:
                continue

            algo_metrics = self.calculate_metrics(df_filtered, algo)

            # Diferença vs XGBoost
            acc_diff = xgb_metrics['acceptance_rate'] - algo_metrics['acceptance_rate']
            acc_diff_pct = (acc_diff / algo_metrics['acceptance_rate'] * 100) if algo_metrics['acceptance_rate'] > 0 else 0

            # Teste estatístico (t-test)
            xgb_results_bool = xgb_results['result'].astype(int)
            algo_results_bool = algo_df['result'].astype(int)

            # Garantir mesmo tamanho para teste
            min_len = min(len(xgb_results_bool), len(algo_results_bool))
            t_stat, p_value = stats.ttest_ind(
                xgb_results_bool.iloc[:min_len],
                algo_results_bool.iloc[:min_len]
            )

            # Cohen's d (tamanho do efeito)
            cohens_d = (
                (xgb_metrics['acceptance_rate'] - algo_metrics['acceptance_rate']) /
                np.sqrt((xgb_results_bool.std()**2 + algo_results_bool.std()**2) / 2)
            )

            comparisons.append({
                'algorithm': algo,
                'fixed_acceptance': algo_metrics['acceptance_rate'],
                'fixed_time': algo_metrics['avg_time'],
                'fixed_r2c': algo_metrics['avg_r2c'],
                'xgb_acceptance': xgb_metrics['acceptance_rate'],
                'xgb_time': xgb_metrics['avg_time'],
                'xgb_r2c': xgb_metrics['avg_r2c'],
                'acc_diff_abs': acc_diff,
                'acc_diff_pct': acc_diff_pct,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'significant': p_value < 0.05,
            })

            # Imprimir
            sign = '+' if acc_diff > 0 else ''
            sig_mark = '✓' if p_value < 0.05 else '✗'
            print(f"   {algo:15s}: {algo_metrics['acceptance_rate']:.2%} → "
                  f"{sign}{acc_diff:.2%} ({sign}{acc_diff_pct:+.1f}%) "
                  f"[p={p_value:.4f}] {sig_mark}")

        # 4. Criar DataFrame de comparação
        comparison_df = pd.DataFrame(comparisons)
        comparison_df = comparison_df.sort_values('acc_diff_abs', ascending=False)

        # 5. Salvar
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        comparison_df.to_csv(output_file, index=False)
        print(f"\n💾 Resultados salvos em: {output_file}")

        # 6. Resumo
        print("\n" + "="*70)
        print("RESUMO")
        print("="*70)

        wins = (comparison_df['acc_diff_abs'] > 0).sum()
        losses = (comparison_df['acc_diff_abs'] <= 0).sum()
        sig_wins = ((comparison_df['acc_diff_abs'] > 0) & (comparison_df['significant'])).sum()
        sig_losses = ((comparison_df['acc_diff_abs'] <= 0) & (comparison_df['significant'])).sum()

        print(f"XGBoost vs Algoritmos Fixos:")
        print(f"  Vitórias: {wins}/{len(comparisons)} ({sig_wins} estatisticamente significativas)")
        print(f"  Derrotas: {losses}/{len(comparisons)} ({sig_losses} estatisticamente significativas)")

        best_fixed = comparison_df.iloc[-1]  # Último (menor diferença ou negativo)
        print(f"\nMelhor algoritmo fixo: {best_fixed['algorithm']}")
        print(f"  Aceitação: {best_fixed['fixed_acceptance']:.2%}")
        print(f"  XGBoost:   {best_fixed['xgb_acceptance']:.2%}")
        print(f"  Diferença: {best_fixed['acc_diff_abs']:+.2%}")

        print("="*70)

        return comparison_df


if __name__ == '__main__':
    # Exemplo de uso
    comparator = PerformanceComparator('xgboost_v2/models/xgboost_vne_selector')
    results = comparator.compare_all_algorithms()
