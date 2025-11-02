"""
LLM Hallucination Research Project
Core package initialization
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.models.llm_wrapper import LLMWrapper
from src.detection.hallucination_detector import HallucinationDetector
from src.evaluation.metrics import EvaluationMetrics

__all__ = [
    "LLMWrapper",
    "HallucinationDetector",
    "EvaluationMetrics",
]
