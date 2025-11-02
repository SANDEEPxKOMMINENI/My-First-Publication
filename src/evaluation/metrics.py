"""
Evaluation Metrics for Hallucination Detection
"""

from typing import List, Dict, Any
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """
    Calculate various metrics for hallucination detection evaluation
    """
    
    @staticmethod
    def accuracy(predictions: List[bool], ground_truth: List[bool]) -> float:
        """Calculate accuracy"""
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        correct = sum(p == g for p, g in zip(predictions, ground_truth))
        return correct / len(predictions) if predictions else 0.0
    
    @staticmethod
    def precision_recall_f1(
        predictions: List[bool],
        ground_truth: List[bool]
    ) -> Dict[str, float]:
        """
        Calculate precision, recall, and F1 score
        True = hallucination, False = no hallucination
        """
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        tp = sum(p and g for p, g in zip(predictions, ground_truth))
        fp = sum(p and not g for p, g in zip(predictions, ground_truth))
        fn = sum(not p and g for p, g in zip(predictions, ground_truth))
        tn = sum(not p and not g for p, g in zip(predictions, ground_truth))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'tn': tn
        }
    
    @staticmethod
    def hallucination_rate(predictions: List[bool]) -> float:
        """Calculate proportion of detected hallucinations"""
        if not predictions:
            return 0.0
        return sum(predictions) / len(predictions)
    
    @staticmethod
    def confidence_calibration(
        confidences: List[float],
        correct: List[bool],
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate calibration metrics
        Measures if confidence scores match actual accuracy
        
        Args:
            confidences: Model confidence scores [0, 1]
            correct: Whether predictions were correct
            num_bins: Number of bins for calibration plot
        
        Returns:
            Dictionary with calibration metrics and bin data
        """
        if len(confidences) != len(correct):
            raise ValueError("Confidences and correct must have same length")
        
        if not confidences:
            return {'ece': 0.0, 'bins': []}
        
        # Create bins
        bins = np.linspace(0, 1, num_bins + 1)
        bin_indices = np.digitize(confidences, bins[:-1]) - 1
        bin_indices = np.clip(bin_indices, 0, num_bins - 1)
        
        # Calculate metrics per bin
        bin_data = []
        total_ece = 0.0
        total_samples = len(confidences)
        
        for i in range(num_bins):
            mask = bin_indices == i
            if not np.any(mask):
                continue
            
            bin_confidences = np.array(confidences)[mask]
            bin_correct = np.array(correct)[mask]
            
            avg_confidence = np.mean(bin_confidences)
            accuracy = np.mean(bin_correct)
            count = len(bin_confidences)
            
            # Expected Calibration Error contribution
            ece_contribution = (count / total_samples) * abs(avg_confidence - accuracy)
            total_ece += ece_contribution
            
            bin_data.append({
                'bin': i,
                'range': (bins[i], bins[i+1]),
                'avg_confidence': float(avg_confidence),
                'accuracy': float(accuracy),
                'count': int(count),
                'gap': float(abs(avg_confidence - accuracy))
            })
        
        return {
            'ece': float(total_ece),  # Expected Calibration Error
            'bins': bin_data,
            'num_bins': num_bins
        }
    
    @staticmethod
    def error_analysis_by_type(
        predictions: List[bool],
        ground_truth: List[bool],
        hallucination_types: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze errors by hallucination type
        
        Args:
            predictions: Detection predictions
            ground_truth: Ground truth labels
            hallucination_types: Type of each sample
        
        Returns:
            Dictionary of metrics per type
        """
        if not (len(predictions) == len(ground_truth) == len(hallucination_types)):
            raise ValueError("All inputs must have same length")
        
        # Group by type
        type_data = defaultdict(lambda: {'preds': [], 'truth': []})
        
        for pred, truth, h_type in zip(predictions, ground_truth, hallucination_types):
            type_data[h_type]['preds'].append(pred)
            type_data[h_type]['truth'].append(truth)
        
        # Calculate metrics per type
        results = {}
        for h_type, data in type_data.items():
            preds = data['preds']
            truth = data['truth']
            
            metrics = EvaluationMetrics.precision_recall_f1(preds, truth)
            metrics['accuracy'] = EvaluationMetrics.accuracy(preds, truth)
            metrics['count'] = len(preds)
            
            results[h_type] = metrics
        
        return results
    
    @staticmethod
    def compare_methods(
        method_results: Dict[str, List[bool]],
        ground_truth: List[bool]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple detection methods
        
        Args:
            method_results: Dict mapping method name to predictions
            ground_truth: Ground truth labels
        
        Returns:
            Dictionary of metrics per method
        """
        comparison = {}
        
        for method_name, predictions in method_results.items():
            if len(predictions) != len(ground_truth):
                logger.warning(f"Skipping {method_name}: length mismatch")
                continue
            
            metrics = EvaluationMetrics.precision_recall_f1(predictions, ground_truth)
            metrics['accuracy'] = EvaluationMetrics.accuracy(predictions, ground_truth)
            metrics['hallucination_rate'] = EvaluationMetrics.hallucination_rate(predictions)
            
            comparison[method_name] = metrics
        
        return comparison
    
    @staticmethod
    def model_comparison(
        model_responses: Dict[str, List[str]],
        ground_truths: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare different LLM models
        
        Args:
            model_responses: Dict mapping model name to list of responses
            ground_truths: List of correct answers
        
        Returns:
            Dictionary of metrics per model
        """
        comparison = {}
        
        for model_name, responses in model_responses.items():
            if len(responses) != len(ground_truths):
                logger.warning(f"Skipping {model_name}: length mismatch")
                continue
            
            # Check exact matches
            exact_matches = [
                r.strip().lower() == g.strip().lower()
                for r, g in zip(responses, ground_truths)
            ]
            
            # Check token overlap
            overlaps = []
            for response, truth in zip(responses, ground_truths):
                r_tokens = set(response.lower().split())
                g_tokens = set(truth.lower().split())
                if g_tokens:
                    overlap = len(r_tokens & g_tokens) / len(g_tokens)
                    overlaps.append(overlap)
                else:
                    overlaps.append(0.0)
            
            comparison[model_name] = {
                'exact_match_rate': sum(exact_matches) / len(exact_matches),
                'avg_token_overlap': np.mean(overlaps),
                'hallucination_rate': 1 - (sum(exact_matches) / len(exact_matches)),
                'num_samples': len(responses)
            }
        
        return comparison
    
    @staticmethod
    def mitigation_effectiveness(
        baseline_hallucinations: List[bool],
        mitigated_hallucinations: List[bool]
    ) -> Dict[str, Any]:
        """
        Measure effectiveness of hallucination mitigation
        
        Args:
            baseline_hallucinations: Hallucinations in baseline
            mitigated_hallucinations: Hallucinations after mitigation
        
        Returns:
            Dictionary with effectiveness metrics
        """
        if len(baseline_hallucinations) != len(mitigated_hallucinations):
            raise ValueError("Inputs must have same length")
        
        baseline_rate = sum(baseline_hallucinations) / len(baseline_hallucinations)
        mitigated_rate = sum(mitigated_hallucinations) / len(mitigated_hallucinations)
        
        # Reduction metrics
        absolute_reduction = baseline_rate - mitigated_rate
        relative_reduction = (absolute_reduction / baseline_rate * 100) if baseline_rate > 0 else 0.0
        
        # Count improvements, degradations, unchanged
        improvements = sum(
            b and not m
            for b, m in zip(baseline_hallucinations, mitigated_hallucinations)
        )
        degradations = sum(
            not b and m
            for b, m in zip(baseline_hallucinations, mitigated_hallucinations)
        )
        unchanged = len(baseline_hallucinations) - improvements - degradations
        
        return {
            'baseline_hallucination_rate': baseline_rate,
            'mitigated_hallucination_rate': mitigated_rate,
            'absolute_reduction': absolute_reduction,
            'relative_reduction_percent': relative_reduction,
            'improvements': improvements,
            'degradations': degradations,
            'unchanged': unchanged,
            'net_improvement': improvements - degradations
        }


# Example usage
if __name__ == "__main__":
    # Example data
    predictions = [True, False, True, False, False, True, False, True]
    ground_truth = [True, False, False, False, True, True, False, True]
    
    print("Evaluation Metrics - Example")
    print("=" * 50)
    
    # Accuracy
    acc = EvaluationMetrics.accuracy(predictions, ground_truth)
    print(f"Accuracy: {acc:.3f}")
    
    # Precision, Recall, F1
    prf = EvaluationMetrics.precision_recall_f1(predictions, ground_truth)
    print(f"Precision: {prf['precision']:.3f}")
    print(f"Recall: {prf['recall']:.3f}")
    print(f"F1: {prf['f1']:.3f}")
    
    # Hallucination rate
    h_rate = EvaluationMetrics.hallucination_rate(predictions)
    print(f"Hallucination Rate: {h_rate:.3f}")
