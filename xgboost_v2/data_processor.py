"""
Processamento de dados para treinamento do XGBoost
Calcula scores e identifica o melhor algoritmo para cada VNR
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from .config import ScoreConfig, FeatureConfig


class DataProcessor:
    """Processa dados de simulação e calcula scores"""

    def __init__(self, score_config: ScoreConfig):
        """
        Args:
            score_config: Configuração de pesos para calcular score
        """
        self.score_config = score_config
        self.algorithms = [
            'mip', 'mcts', 'pl_rank', 'rw_rank_bfs',
            'ga_meta', 'sa_meta', 'd_round', 'r_round'
        ]

    def load_data(self, filepath: str = 'vnr_aggregated_data.csv') -> pd.DataFrame:
        """
        Carrega dados de simulação

        Args:
            filepath: Caminho para o arquivo CSV

        Returns:
            DataFrame com todos os registros
        """
        print(f"📂 Carregando dados de: {filepath}")
        df = pd.read_csv(filepath)

        # Filtrar apenas eventos de chegada (event_type == 1)
        df = df[df['event_type'] == 1].copy()

        print(f"   Total de registros: {len(df):,}")
        print(f"   Algoritmos: {sorted(df['algorithm'].unique())}")
        print(f"   Seeds: {sorted(df['seed'].unique())}")

        return df

    def calculate_algorithm_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score de cada algoritmo baseado na configuração

        Args:
            df: DataFrame com dados brutos

        Returns:
            DataFrame com scores por algoritmo
        """
        print(f"\n📊 Calculando scores com configuração: {self.score_config}")

        results = []

        for algo in self.algorithms:
            algo_df = df[df['algorithm'] == algo]

            if len(algo_df) == 0:
                continue

            # 1. Taxa de aceitação
            acceptance_rate = algo_df['result'].mean()

            # 2. Tempo médio (apenas das aceitas)
            accepted = algo_df[algo_df['result'] == True]
            if len(accepted) > 0:
                avg_time = accepted['solving_time'].mean()
            else:
                avg_time = float('inf')

            # 3. R2C médio (apenas das aceitas)
            if len(accepted) > 0:
                avg_r2c = accepted['v_net_r2c_ratio'].mean()
            else:
                avg_r2c = 0.0

            results.append({
                'algorithm': algo,
                'acceptance_rate': acceptance_rate,
                'avg_time': avg_time,
                'avg_r2c': avg_r2c,
                'n_total': len(algo_df),
                'n_accepted': len(accepted),
            })

        return pd.DataFrame(results)

    def normalize_time(self, times: np.ndarray) -> np.ndarray:
        """
        Normaliza tempos segundo configuração

        Args:
            times: Array de tempos

        Returns:
            Array de tempos normalizados (0-1, menor é melhor)
        """
        method = self.score_config.time_normalization

        if method == 'minmax':
            # Min-max normalization
            min_time = times.min()
            max_time = times.max()
            if max_time > min_time:
                return (times - min_time) / (max_time - min_time)
            return np.zeros_like(times)

        elif method == 'log':
            # Log normalization
            log_times = np.log1p(times)  # log(1 + x) para evitar log(0)
            min_log = log_times.min()
            max_log = log_times.max()
            if max_log > min_log:
                return (log_times - min_log) / (max_log - min_log)
            return np.zeros_like(times)

        elif method == 'inverse':
            # Inverse: 1 / (1 + time)
            return 1.0 / (1.0 + times)

        else:
            raise ValueError(f"Método de normalização desconhecido: {method}")

    def compute_score(self, algo_stats: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula score final para cada algoritmo

        Args:
            algo_stats: DataFrame com estatísticas por algoritmo

        Returns:
            DataFrame com scores calculados
        """
        df = algo_stats.copy()

        # Normalizar tempo (substituir inf por valor alto)
        times = df['avg_time'].replace(float('inf'), 1e6).values
        norm_times = self.normalize_time(times)

        # Calcular score
        df['norm_time'] = norm_times
        df['score'] = (
            self.score_config.w_acceptance * df['acceptance_rate'] -
            self.score_config.w_time * df['norm_time'] +
            self.score_config.w_r2c * df['avg_r2c']
        )

        return df.sort_values('score', ascending=False)

    def select_best_algorithm_per_vnr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Para cada VNR, identifica qual algoritmo teve o melhor score

        Args:
            df: DataFrame com todos os registros

        Returns:
            DataFrame com uma linha por VNR e o melhor algoritmo
        """
        print("\n🎯 Identificando melhor algoritmo para cada VNR...")

        # Calcular estatísticas globais de cada algoritmo (para normalização)
        algo_stats = self.calculate_algorithm_scores(df)
        algo_stats_with_scores = self.compute_score(algo_stats)

        print("\n   Scores globais por algoritmo:")
        for _, row in algo_stats_with_scores.iterrows():
            print(f"   {row['algorithm']:15s}: score={row['score']:.4f} "
                  f"(acc={row['acceptance_rate']:.1%}, time={row['avg_time']:.2f}s)")

        # Criar identificador único de VNR
        df['vnr_uid'] = (
            df['v_net_id'].astype(str) + '_' +
            df['seed'].astype(str) + '_' +
            df['event_time'].astype(int).astype(str)
        )

        # Para cada VNR, calcular score de cada algoritmo que tentou
        vnr_data = []

        for vnr_uid, group in df.groupby('vnr_uid'):
            if len(group) < 2:
                # Precisa de pelo menos 2 algoritmos para comparar
                continue

            # Calcular score local para cada algoritmo neste VNR
            algos_in_vnr = []

            for _, row in group.iterrows():
                algo = row['algorithm']

                # Taxa de aceitação: 1.0 se aceita, 0.0 se não
                acceptance = 1.0 if row['result'] else 0.0

                # Tempo: usar o tempo real deste VNR
                time = row['solving_time'] if row['result'] else float('inf')

                # R2C: usar o R2C real deste VNR
                r2c = row['v_net_r2c_ratio'] if row['result'] else 0.0

                algos_in_vnr.append({
                    'algorithm': algo,
                    'acceptance': acceptance,
                    'time': time,
                    'r2c': r2c,
                })

            # Converter para DataFrame para facilitar cálculos
            algos_df = pd.DataFrame(algos_in_vnr)

            # Normalizar tempo apenas entre os algoritmos deste VNR
            times = algos_df['time'].replace(float('inf'), 1e6).values
            norm_times = self.normalize_time(times)
            algos_df['norm_time'] = norm_times

            # Calcular score para cada algoritmo neste VNR
            # Usar sempre aceitação LOCAL (se aceitou ESTA VNR especificamente)
            algos_df['score'] = (
                self.score_config.w_acceptance * algos_df['acceptance'] -
                self.score_config.w_time * algos_df['norm_time'] +
                self.score_config.w_r2c * algos_df['r2c']
            )

            # Selecionar o melhor
            best_idx = algos_df['score'].idxmax()
            best_algo = algos_df.loc[best_idx, 'algorithm']

            # Pegar features da VNR (mesmo para todos os algoritmos)
            vnr_features = group.iloc[0]

            vnr_data.append({
                'vnr_uid': vnr_uid,
                'best_algorithm': best_algo,
                'v_net_id': vnr_features['v_net_id'],
                'seed': vnr_features['seed'],
                'event_time': vnr_features['event_time'],
                'result': vnr_features['result'],
                # Features para o modelo
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
                'num_algorithms_tested': len(group),
            })

        result_df = pd.DataFrame(vnr_data)

        print(f"\n   ✓ Processadas {len(result_df)} VNRs únicas")
        print(f"\n   Distribuição de 'melhor algoritmo':")
        best_algo_counts = result_df['best_algorithm'].value_counts()
        for algo, count in best_algo_counts.items():
            pct = count / len(result_df) * 100
            print(f"   {algo:15s}: {count:5d} ({pct:5.1f}%)")

        return result_df

    def create_training_dataset(
        self,
        data_file: str = 'vnr_aggregated_data.csv',
        output_file: str = 'xgboost_v2/training_dataset.csv'
    ) -> pd.DataFrame:
        """
        Pipeline completo: carregar dados, calcular scores, criar dataset

        Args:
            data_file: Arquivo de entrada com dados brutos
            output_file: Arquivo de saída com dataset de treino

        Returns:
            DataFrame pronto para treino
        """
        print("="*70)
        print("CRIANDO DATASET DE TREINAMENTO")
        print("="*70)

        # 1. Carregar dados
        df = self.load_data(data_file)

        # 2. Identificar melhor algoritmo para cada VNR
        training_df = self.select_best_algorithm_per_vnr(df)

        # 3. Salvar
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        training_df.to_csv(output_file, index=False)
        print(f"\n💾 Dataset salvo em: {output_file}")
        print(f"   Total de VNRs: {len(training_df)}")
        print(f"   Features: {len(FeatureConfig.get_all_features())}")

        print("\n" + "="*70)
        return training_df


if __name__ == '__main__':
    # Exemplo de uso
    from config import SCORE_CONFIGS

    # Testar com configuração balanceada
    score_config = SCORE_CONFIGS['acceptance_only']
    processor = DataProcessor(score_config)

    # Criar dataset
    df = processor.create_training_dataset()

    print("\n✅ Dataset criado com sucesso!")
    print(f"   Configuração: {score_config}")
    print(f"   Shape: {df.shape}")
