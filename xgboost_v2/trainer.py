"""
Treinamento do modelo XGBoost com train/test split e cross-validation
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import json
from typing import Tuple, Dict

from .config import TrainingConfig, XGBoostConfig, FeatureConfig


class XGBoostTrainer:
    """Treina modelo XGBoost para seleção de algoritmos"""

    def __init__(
        self,
        training_config: TrainingConfig,
        xgboost_config: XGBoostConfig
    ):
        self.training_config = training_config
        self.xgboost_config = xgboost_config
        self.model = None
        self.label_encoder = None
        self.feature_names = None

    def load_dataset(self, filepath: str) -> pd.DataFrame:
        """Carrega dataset de treinamento"""
        print(f"📂 Carregando dataset: {filepath}")
        df = pd.read_csv(filepath)
        print(f"   Total de VNRs: {len(df)}")
        print(f"   Colunas: {len(df.columns)}")
        return df

    def prepare_data(
        self,
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, LabelEncoder]:
        """
        Prepara dados para treinamento

        Returns:
            X_train, X_test, y_train, y_test, label_encoder
        """
        print("\n📊 Preparando dados...")

        # Features
        self.feature_names = FeatureConfig.get_all_features()
        X = df[self.feature_names].values

        # Labels (algoritmos)
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(df['best_algorithm'])

        print(f"   Features: {len(self.feature_names)}")
        print(f"   Classes: {len(self.label_encoder.classes_)}")
        print(f"   Distribuição de classes:")
        for i, algo in enumerate(self.label_encoder.classes_):
            count = (y == i).sum()
            pct = count / len(y) * 100
            print(f"     {algo:15s}: {count:5d} ({pct:5.1f}%)")

        # Train/test split
        stratify_y = y if self.training_config.stratify else None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.training_config.test_size,
            random_state=self.training_config.random_state,
            stratify=stratify_y
        )

        print(f"\n   Train: {len(X_train)} samples")
        print(f"   Test:  {len(X_test)} samples")

        return X_train, X_test, y_train, y_test, self.label_encoder

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> xgb.XGBClassifier:
        """
        Treina modelo XGBoost

        Returns:
            Modelo treinado
        """
        print("\n🚀 Treinando XGBoost...")
        print(f"   Configuração: {self.xgboost_config.to_dict()}")

        # Criar modelo
        params = self.xgboost_config.to_dict()
        # Adicionar num_class baseado nos dados
        n_classes = len(np.unique(y_train))
        if n_classes == 2:
            # Binary classification
            params['objective'] = 'binary:logistic'
            params['eval_metric'] = 'logloss'
            if 'num_class' in params:
                del params['num_class']
        else:
            # Multi-class classification
            params['num_class'] = n_classes
        self.model = xgb.XGBClassifier(**params)

        # Treinar
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        # Avaliar no treino
        y_train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, y_train_pred)

        # Avaliar no teste
        y_test_pred = self.model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)

        print(f"\n   ✓ Treinamento concluído!")
        print(f"   Acurácia no treino: {train_acc:.2%}")
        print(f"   Acurácia no teste:  {test_acc:.2%}")

        return self.model

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, float]:
        """
        Realiza validação cruzada

        Returns:
            Dicionário com estatísticas de CV
        """
        print(f"\n🔄 Validação cruzada ({self.training_config.cv_folds} folds)...")

        # Criar modelo para CV
        params = self.xgboost_config.to_dict()
        # Adicionar num_class baseado nos dados
        n_classes = len(np.unique(y))
        if n_classes == 2:
            # Binary classification
            params['objective'] = 'binary:logistic'
            params['eval_metric'] = 'logloss'
            if 'num_class' in params:
                del params['num_class']
        else:
            # Multi-class classification
            params['num_class'] = n_classes
        model = xgb.XGBClassifier(**params)

        # CV estratificado
        cv = StratifiedKFold(
            n_splits=self.training_config.cv_folds,
            shuffle=True,
            random_state=self.training_config.random_state
        )

        # Executar CV
        scores = cross_val_score(
            model, X, y,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1
        )

        cv_stats = {
            'mean': scores.mean(),
            'std': scores.std(),
            'min': scores.min(),
            'max': scores.max(),
            'scores': scores.tolist()
        }

        print(f"   Média:  {cv_stats['mean']:.2%} ± {cv_stats['std']:.2%}")
        print(f"   Range:  [{cv_stats['min']:.2%}, {cv_stats['max']:.2%}]")

        return cv_stats

    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        Avalia modelo em detalhes

        Returns:
            Dicionário com métricas
        """
        print("\n📈 Avaliação detalhada...")

        # Predições
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        # Acurácia
        acc = accuracy_score(y_test, y_pred)

        # Report
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            output_dict=True,
            zero_division=0
        )

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        print(f"\n   Acurácia: {acc:.2%}")
        print(f"\n   Classification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        ))

        return {
            'accuracy': acc,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
        }

    def plot_feature_importance(self, output_dir: str = 'xgboost_v2/outputs'):
        """Plota importância das features"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        importance = self.model.feature_importances_
        indices = np.argsort(importance)[::-1]

        plt.figure(figsize=(10, 6))
        plt.title('Feature Importance')
        plt.bar(range(len(importance)), importance[indices])
        plt.xticks(
            range(len(importance)),
            [self.feature_names[i] for i in indices],
            rotation=45,
            ha='right'
        )
        plt.tight_layout()
        plt.savefig(f'{output_dir}/feature_importance.png', dpi=300)
        plt.close()

        print(f"   ✓ Feature importance salvo em: {output_dir}/feature_importance.png")

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        output_dir: str = 'xgboost_v2/outputs'
    ):
        """Plota matriz de confusão"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.label_encoder.classes_,
            yticklabels=self.label_encoder.classes_
        )
        plt.title('Confusion Matrix')
        plt.ylabel('True')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/confusion_matrix.png', dpi=300)
        plt.close()

        print(f"   ✓ Confusion matrix salvo em: {output_dir}/confusion_matrix.png")

    def save_model(
        self,
        model_name: str = 'xgboost_vne_selector',
        output_dir: str = 'xgboost_v2/models'
    ):
        """Salva modelo treinado"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Salvar modelo XGBoost
        model_path = f'{output_dir}/{model_name}.json'
        self.model.save_model(model_path)

        # Salvar label encoder
        encoder_path = f'{output_dir}/{model_name}_label_encoder.pkl'
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)

        # Salvar metadados
        metadata = {
            'feature_names': self.feature_names,
            'classes': self.label_encoder.classes_.tolist(),
            'n_features': len(self.feature_names),
            'n_classes': len(self.label_encoder.classes_),
            'xgboost_config': self.xgboost_config.to_dict(),
        }
        metadata_path = f'{output_dir}/{model_name}_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n💾 Modelo salvo:")
        print(f"   - {model_path}")
        print(f"   - {encoder_path}")
        print(f"   - {metadata_path}")

    def train_full_pipeline(
        self,
        dataset_path: str,
        model_name: str = 'xgboost_vne_selector',
        output_dir: str = 'xgboost_v2'
    ) -> Dict:
        """
        Pipeline completo de treinamento

        Returns:
            Dicionário com resultados
        """
        print("="*70)
        print("TREINAMENTO XGBOOST - PIPELINE COMPLETO")
        print("="*70)

        # 1. Carregar dados
        df = self.load_dataset(dataset_path)

        # 2. Preparar dados
        X_train, X_test, y_train, y_test, label_encoder = self.prepare_data(df)

        # 3. Cross-validation
        X_full = np.vstack([X_train, X_test])
        y_full = np.concatenate([y_train, y_test])
        cv_stats = self.cross_validate(X_full, y_full)

        # 4. Treinar modelo
        model = self.train(X_train, y_train, X_test, y_test)

        # 5. Avaliar
        eval_results = self.evaluate(X_test, y_test)

        # 6. Visualizações
        print("\n📊 Gerando visualizações...")
        self.plot_feature_importance(f'{output_dir}/outputs')
        self.plot_confusion_matrix(
            np.array(eval_results['confusion_matrix']),
            f'{output_dir}/outputs'
        )

        # 7. Salvar modelo
        self.save_model(model_name, f'{output_dir}/models')

        # Resultado final
        results = {
            'cv_stats': cv_stats,
            'eval_results': eval_results,
            'n_train': len(X_train),
            'n_test': len(X_test),
        }

        # Salvar resultados
        results_path = f'{output_dir}/outputs/training_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "="*70)
        print("✅ TREINAMENTO CONCLUÍDO!")
        print("="*70)
        print(f"   Acurácia (CV):   {cv_stats['mean']:.2%} ± {cv_stats['std']:.2%}")
        print(f"   Acurácia (Test): {eval_results['accuracy']:.2%}")
        print(f"   Modelo salvo em: {output_dir}/models/")
        print("="*70)

        return results


if __name__ == '__main__':
    from config import TrainingConfig, XGBoostConfig

    # Configurações
    training_config = TrainingConfig(
        test_size=0.2,
        cv_folds=5,
        random_state=42
    )

    xgboost_config = XGBoostConfig(
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100
    )

    # Treinar
    trainer = XGBoostTrainer(training_config, xgboost_config)
    results = trainer.train_full_pipeline(
        dataset_path='xgboost_v2/training_dataset.csv'
    )
