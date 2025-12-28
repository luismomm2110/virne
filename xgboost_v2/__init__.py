"""
XGBoost VNE Selector v2
Sistema de seleção de algoritmos VNE baseado em score customizável
"""

from .config import (
    ScoreConfig,
    TrainingConfig,
    XGBoostConfig,
    FeatureConfig,
    SCORE_CONFIGS,
)

__version__ = '2.0.0'
__all__ = [
    'ScoreConfig',
    'TrainingConfig',
    'XGBoostConfig',
    'FeatureConfig',
    'SCORE_CONFIGS',
]
