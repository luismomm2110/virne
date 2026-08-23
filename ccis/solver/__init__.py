"""
Registro dos solucionadores do pacote CCIS.

A importação deste módulo dispara o decorador ``SolverRegistry.register`` de
``greedy_oracle``, tornando o nome ``greedy_oracle`` utilizável no campo de
configuração ``solver.solver_name``.
"""

from .greedy_oracle import GreedyOracleSolver

__all__ = ['GreedyOracleSolver']
