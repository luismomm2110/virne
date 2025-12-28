"""
Predictor - Usa modelo treinado para prever melhor algoritmo
"""

import numpy as np
import xgboost as xgb
import pickle
import json
from pathlib import Path
from typing import Dict, Tuple, List


class VNEPredictor:
    """Prediz melhor algoritmo para uma VNR usando modelo treinado"""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.metadata = None

    def load_model(self, model_path: str):
        """
        Carrega modelo treinado

        Args:
            model_path: Caminho base do modelo (sem extensão)
        """
        print(f"📂 Carregando modelo: {model_path}")

        # Carregar modelo XGBoost
        self.model = xgb.XGBClassifier()
        self.model.load_model(f"{model_path}.json")

        # Carregar label encoder
        with open(f"{model_path}_label_encoder.pkl", 'rb') as f:
            self.label_encoder = pickle.load(f)

        # Carregar metadados
        with open(f"{model_path}_metadata.json", 'r') as f:
            self.metadata = json.load(f)
            self.feature_names = self.metadata['feature_names']

        print(f"   ✓ Modelo carregado")
        print(f"   Classes: {self.label_encoder.classes_}")
        print(f"   Features: {len(self.feature_names)}")

    def predict_single(
        self,
        vnr_features: Dict[str, float],
        return_probabilities: bool = False
    ) -> Tuple[str, float, Dict]:
        """
        Prediz melhor algoritmo para uma VNR

        Args:
            vnr_features: Dicionário com features da VNR
            return_probabilities: Se True, retorna probabilidades de todas as classes

        Returns:
            (algoritmo, confiança, info)
        """
        # Extrair features na ordem correta
        X = np.array([[vnr_features[f] for f in self.feature_names]])

        # Predizer
        y_pred = self.model.predict(X)[0]
        y_proba = self.model.predict_proba(X)[0]

        # Decodificar
        algorithm = self.label_encoder.inverse_transform([y_pred])[0]
        confidence = y_proba[y_pred]

        # Info adicional
        info = {
            'predicted_class_id': int(y_pred),
            'confidence': float(confidence),
        }

        if return_probabilities:
            info['algorithm_probabilities'] = {
                algo: float(prob)
                for algo, prob in zip(self.label_encoder.classes_, y_proba)
            }

        return algorithm, confidence, info

    def predict_batch(
        self,
        vnr_features_list: List[Dict[str, float]]
    ) -> List[Tuple[str, float]]:
        """
        Prediz para múltiplas VNRs

        Args:
            vnr_features_list: Lista de dicionários com features

        Returns:
            Lista de (algoritmo, confiança)
        """
        # Preparar features
        X = np.array([
            [vnr[f] for f in self.feature_names]
            for vnr in vnr_features_list
        ])

        # Predizer
        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X)

        # Decodificar
        results = []
        for i, pred in enumerate(y_pred):
            algorithm = self.label_encoder.inverse_transform([pred])[0]
            confidence = y_proba[i][pred]
            results.append((algorithm, confidence))

        return results


if __name__ == '__main__':
    # Exemplo de uso
    predictor = VNEPredictor()
    predictor.load_model('xgboost_v2/models/xgboost_vne_selector')

    # Exemplo de VNR
    vnr = {
        'v_net_num_nodes': 5,
        'v_net_num_egdes': 6,
        'v_net_demand': 150,
        'v_net_node_demand': 75,
        'v_net_link_demand': 75,
        'v_net_lifetime': 500,
        'v_net_arrival_time': 1000,
        'p_net_available_resource': 5000,
        'p_net_node_available_resource': 2500,
        'p_net_link_available_resource': 2500,
        'p_net_node_resource_utilization': 0.4,
        'p_net_link_resource_utilization': 0.5,
        'inservice_count': 10,
    }

    algo, conf, info = predictor.predict_single(vnr, return_probabilities=True)

    print(f"\n✨ Predição:")
    print(f"   Algoritmo: {algo}")
    print(f"   Confiança: {conf:.2%}")
    print(f"   Probabilidades: {info['algorithm_probabilities']}")
