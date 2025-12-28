"""
Configuração do XGBoost VNE Selector v2
Sistema de seleção de algoritmos baseado em score customizável
"""

class ScoreConfig:
    """
    Configuração dos pesos para calcular o score de cada algoritmo

    Score = w_acceptance * acceptance_rate - w_time * normalized_time + w_r2c * r2c_ratio

    Exemplos de uso:
    - Priorizar aceitação: w_acceptance=1.0, w_time=0.0, w_r2c=0.0
    - Balanceado: w_acceptance=0.5, w_time=0.3, w_r2c=0.2
    - Rápido: w_acceptance=0.3, w_time=0.6, w_r2c=0.1
    """

    def __init__(
        self,
        w_acceptance: float = 0.6,
        w_time: float = 0.3,
        w_r2c: float = 0.1,
        time_normalization: str = 'minmax',  # 'minmax', 'log', 'inverse'
        name: str = 'balanced'
    ):
        """
        Args:
            w_acceptance: Peso para taxa de aceitação (0-1)
            w_time: Peso para tempo (penalidade, 0-1)
            w_r2c: Peso para revenue-to-cost ratio (0-1)
            time_normalization: Método de normalização do tempo
            name: Nome descritivo desta configuração
        """
        self.w_acceptance = w_acceptance
        self.w_time = w_time
        self.w_r2c = w_r2c
        self.time_normalization = time_normalization
        self.name = name

        # Validar pesos
        total = w_acceptance + w_time + w_r2c
        if abs(total - 1.0) > 0.01:
            print(f"⚠️  Aviso: Pesos não somam 1.0 (soma = {total:.2f})")

    def __str__(self):
        return (
            f"ScoreConfig('{self.name}'): "
            f"acc={self.w_acceptance:.1%}, "
            f"time={self.w_time:.1%}, "
            f"r2c={self.w_r2c:.1%}"
        )


# Configurações pré-definidas
SCORE_CONFIGS = {
    'acceptance_only': ScoreConfig(
        w_acceptance=1.0,
        w_time=0.0,
        w_r2c=0.0,
        name='acceptance_only'
    ),

    'balanced': ScoreConfig(
        w_acceptance=0.6,
        w_time=0.3,
        w_r2c=0.1,
        name='balanced'
    ),

    'fast': ScoreConfig(
        w_acceptance=0.3,
        w_time=0.6,
        w_r2c=0.1,
        name='fast'
    ),

    'quality': ScoreConfig(
        w_acceptance=0.4,
        w_time=0.1,
        w_r2c=0.5,
        name='quality'
    ),

    'acceptance_speed': ScoreConfig(
        w_acceptance=0.7,
        w_time=0.3,
        w_r2c=0.0,
        name='acceptance_speed'
    ),
}


class TrainingConfig:
    """Configuração do treinamento do XGBoost"""

    def __init__(
        self,
        test_size: float = 0.2,
        cv_folds: int = 5,
        random_state: int = 42,
        stratify: bool = True
    ):
        self.test_size = test_size
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.stratify = stratify


class XGBoostConfig:
    """Configuração do modelo XGBoost"""

    def __init__(
        self,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 1,
        gamma: float = 0,
        reg_alpha: float = 0,
        reg_lambda: float = 1,
        n_jobs: int = -1,
        random_state: int = 42
    ):
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_weight = min_child_weight
        self.gamma = gamma
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.n_jobs = n_jobs
        self.random_state = random_state

    def to_dict(self):
        """Converter para dicionário para usar no XGBoost"""
        return {
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'n_estimators': self.n_estimators,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'min_child_weight': self.min_child_weight,
            'gamma': self.gamma,
            'reg_alpha': self.reg_alpha,
            'reg_lambda': self.reg_lambda,
            'n_jobs': self.n_jobs,
            'random_state': self.random_state,
            'objective': 'multi:softprob',
            'eval_metric': 'mlogloss',
        }


class FeatureConfig:
    """Configuração das features a serem usadas"""

    # Features de topologia da VNR
    VNR_TOPOLOGY = [
        'v_net_num_nodes',
        'v_net_num_egdes',
    ]

    # Features de demanda da VNR
    VNR_DEMAND = [
        'v_net_demand',
        'v_net_node_demand',
        'v_net_link_demand',
    ]

    # Features da rede física
    PNET_STATE = [
        'p_net_available_resource',
        'p_net_node_available_resource',
        'p_net_link_available_resource',
        'p_net_node_resource_utilization',
        'p_net_link_resource_utilization',
    ]

    # Features temporais
    TEMPORAL = [
        'v_net_lifetime',
        'v_net_arrival_time',
        'inservice_count',
    ]

    @classmethod
    def get_all_features(cls):
        """Retorna todas as features disponíveis"""
        return (
            cls.VNR_TOPOLOGY +
            cls.VNR_DEMAND +
            cls.PNET_STATE +
            cls.TEMPORAL
        )

    @classmethod
    def get_feature_groups(cls):
        """Retorna dicionário de grupos de features"""
        return {
            'topology': cls.VNR_TOPOLOGY,
            'demand': cls.VNR_DEMAND,
            'pnet': cls.PNET_STATE,
            'temporal': cls.TEMPORAL,
        }
