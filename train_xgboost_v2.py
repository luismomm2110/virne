#!/usr/bin/env python3
"""
Script principal para treinar XGBoost VNE Selector v2
Permite escolher configuração de score e treinar modelo
"""

import argparse
from xgboost_v2.config import ScoreConfig, TrainingConfig, XGBoostConfig, SCORE_CONFIGS
from xgboost_v2.data_processor import DataProcessor
from xgboost_v2.trainer import XGBoostTrainer


def main():
    parser = argparse.ArgumentParser(
        description='Treinar XGBoost para seleção de algoritmos VNE'
    )

    # Configuração de score
    parser.add_argument(
        '--score-config',
        type=str,
        default='balanced',
        choices=list(SCORE_CONFIGS.keys()) + ['custom'],
        help='Configuração de score pré-definida'
    )

    # Pesos customizados (se score-config=custom)
    parser.add_argument(
        '--w-acceptance',
        type=float,
        default=0.6,
        help='Peso para taxa de aceitação (0-1)'
    )
    parser.add_argument(
        '--w-time',
        type=float,
        default=0.3,
        help='Peso para tempo (penalidade, 0-1)'
    )
    parser.add_argument(
        '--w-r2c',
        type=float,
        default=0.1,
        help='Peso para R2C ratio (0-1)'
    )

    # Arquivos
    parser.add_argument(
        '--data-file',
        type=str,
        default='vnr_aggregated_data.csv',
        help='Arquivo CSV com dados de simulação'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='xgboost_v2',
        help='Diretório de saída'
    )
    parser.add_argument(
        '--model-name',
        type=str,
        default='xgboost_vne_selector',
        help='Nome do modelo'
    )

    # Treinamento
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proporção de dados para teste (0-1)'
    )
    parser.add_argument(
        '--cv-folds',
        type=int,
        default=5,
        help='Número de folds para cross-validation'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Seed para reprodutibilidade'
    )

    # XGBoost
    parser.add_argument(
        '--max-depth',
        type=int,
        default=6,
        help='Profundidade máxima das árvores'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.1,
        help='Taxa de aprendizado'
    )
    parser.add_argument(
        '--n-estimators',
        type=int,
        default=100,
        help='Número de árvores'
    )

    # Opções
    parser.add_argument(
        '--skip-data-prep',
        action='store_true',
        help='Pular preparação de dados (usar dataset existente)'
    )

    args = parser.parse_args()

    print("="*70)
    print("XGBOOST VNE SELECTOR V2 - TREINAMENTO")
    print("="*70)

    # 1. Configurar score
    if args.score_config == 'custom':
        score_config = ScoreConfig(
            w_acceptance=args.w_acceptance,
            w_time=args.w_time,
            w_r2c=args.w_r2c,
            name='custom'
        )
    else:
        score_config = SCORE_CONFIGS[args.score_config]

    print(f"\n📊 Configuração de Score: {score_config}")

    # 2. Preparar dados (se necessário)
    dataset_path = f'{args.output_dir}/training_dataset.csv'

    if not args.skip_data_prep:
        print("\n" + "="*70)
        print("ETAPA 1: PREPARAÇÃO DE DADOS")
        print("="*70)

        processor = DataProcessor(score_config)
        df = processor.create_training_dataset(
            data_file=args.data_file,
            output_file=dataset_path
        )
    else:
        print(f"\n⏭️  Pulando preparação de dados. Usando: {dataset_path}")

    # 3. Treinar modelo
    print("\n" + "="*70)
    print("ETAPA 2: TREINAMENTO DO MODELO")
    print("="*70)

    training_config = TrainingConfig(
        test_size=args.test_size,
        cv_folds=args.cv_folds,
        random_state=args.random_seed
    )

    xgboost_config = XGBoostConfig(
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        n_estimators=args.n_estimators,
        random_state=args.random_seed
    )

    trainer = XGBoostTrainer(training_config, xgboost_config)
    results = trainer.train_full_pipeline(
        dataset_path=dataset_path,
        model_name=args.model_name,
        output_dir=args.output_dir
    )

    # 4. Resumo final
    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Configuração de Score: {score_config}")
    print(f"Dataset: {results['n_train'] + results['n_test']} VNRs")
    print(f"  - Treino: {results['n_train']}")
    print(f"  - Teste:  {results['n_test']}")
    print(f"\nResultados:")
    print(f"  - CV Accuracy:   {results['cv_stats']['mean']:.2%} ± {results['cv_stats']['std']:.2%}")
    print(f"  - Test Accuracy: {results['eval_results']['accuracy']:.2%}")
    print(f"\nModelo salvo em: {args.output_dir}/models/{args.model_name}")
    print("="*70)


if __name__ == '__main__':
    main()
