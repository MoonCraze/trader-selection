"""
Trader Analysis Package

A research-grade framework for statistical evaluation and segmentation of crypto wallet addresses.
"""

__version__ = "3.0.0"
__author__ = "MoonCraze"

from .feature_engineering import FeatureEngineer
from .clustering import TraderSegmentation
from .prediction import HighPotentialPredictor
from .adaptive_personas import AdaptivePersonaLearner
from .temporal_evolution import TemporalEvolutionTracker
from .hybrid_persona_system import HybridPersonaSystem, PersonaDefinition
from .evaluation import ModelEvaluator

# Legacy support (deprecated)
from .personas import PersonaAssigner

__all__ = [
    'FeatureEngineer',
    'TraderSegmentation',
    'HighPotentialPredictor',
    'AdaptivePersonaLearner',
    'TemporalEvolutionTracker',
    'HybridPersonaSystem',
    'PersonaDefinition',
    'ModelEvaluator',
    'PersonaAssigner'  # Deprecated - use HybridPersonaSystem
]
