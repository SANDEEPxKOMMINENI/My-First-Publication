#!/usr/bin/env python3
"""
Comprehensive Hallucination Detection Experiment
Tests multiple models on large dataset with all detection methods
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.llm_wrapper import LLMWrapper
from src.detection.hallucination_detector import HallucinationDetector
from src.evaluation.metrics import EvaluationMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_dataset(dataset_path: str) -> List[Dict]:
    """Load and flatten the comprehensive dataset"""
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # Flatten the dataset
    questions = []
    for category_data in data:
        category = category_data['category']
        difficulty = category_data['difficulty']
        for q in category_data['questions']:
            questions.append({
                'question': q['question'],
                'answer': q['answer'],
                'category': category,
                'difficulty': difficulty,
                'type': q.get('type', 'factual'),
                'hallucination_trigger': q.get('hallucination_trigger', False)
            })
    
    return questions


def run_experiment(
    models: List[str],
    dataset_path: str,
    output_dir: str = "results/comprehensive",
    sample_size: int = None,
    temperature: float = 0.7
):
    """
    Run comprehensive experiment across models and dataset
    
    Args:
        models: List of model providers to test
        dataset_path: Path to dataset JSON
        output_dir: Directory for results
        sample_size: Limit number of questions (None = all)
        temperature: LLM temperature
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load dataset
    logger.info(f"Loading dataset from {dataset_path}")
    questions = load_dataset(dataset_path)
    
    if sample_size:
        questions = questions[:sample_size]
    
    logger.info(f"Dataset size: {len(questions)} questions")
    
    # Initialize LLM and detector
    try:
        llm = LLMWrapper()
        available = llm.get_available_providers()
        logger.info(f"Available providers: {available}")
        
        # Filter to available models
        models = [m for m in models if m in available]
        if not models:
            logger.error("No models available. Please configure API keys.")
            return
        
        logger.info(f"Testing models: {models}")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        return
    
    detector = HallucinationDetector(llm)
    
    # Store all results
    all_results = {
        'timestamp': timestamp,
        'dataset': dataset_path,
        'num_questions': len(questions),
        'models': models,
        'temperature': temperature,
        'results_by_model': {}
    }
    
    # Test each model
    for model_name in models:
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing Model: {model_name.upper()}")
        logger.info(f"{'='*80}\n")
        
        model_results = []
        correct_count = 0
        hallucination_count = 0
        error_count = 0
        
        for i, qa in enumerate(questions):
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(questions)} questions")
            
            try:
                # Generate response
                response = llm.generate(
                    qa['question'],
                    provider=model_name,
                    temperature=temperature,
                    max_tokens=150
                )
                
                # Check correctness (simple contains check)
                is_correct = qa['answer'].lower() in response.text.lower()
                
                # Detect hallucination using factual verification
                detection = detector.detect_factual_error(
                    response.text,
                    qa['answer']
                )
                
                result = {
                    'question_id': i,
                    'question': qa['question'],
                    'ground_truth': qa['answer'],
                    'model_response': response.text,
                    'category': qa['category'],
                    'difficulty': qa['difficulty'],
                    'type': qa['type'],
                    'hallucination_trigger': qa['hallucination_trigger'],
                    'is_correct': is_correct,
                    'detection': {
                        'is_hallucination': detection.is_hallucination,
                        'confidence': detection.confidence,
                        'type': detection.hallucination_type,
                        'method': detection.detection_method
                    },
                    'tokens_used': response.tokens_used,
                    'latency': response.latency
                }
                
                if is_correct:
                    correct_count += 1
                if detection.is_hallucination:
                    hallucination_count += 1
                
                model_results.append(result)
                
            except Exception as e:
                logger.warning(f"Error on question {i+1}: {e}")
                error_count += 1
                model_results.append({
                    'question_id': i,
                    'question': qa['question'],
                    'error': str(e)
                })
        
        # Calculate metrics
        total_answered = len(questions) - error_count
        accuracy = correct_count / total_answered if total_answered > 0 else 0
        hallucination_rate = hallucination_count / total_answered if total_answered > 0 else 0
        
        avg_latency = sum(r.get('latency', 0) for r in model_results if 'latency' in r) / total_answered if total_answered > 0 else 0
        avg_tokens = sum(r.get('tokens_used', 0) for r in model_results if 'tokens_used' in r) / total_answered if total_answered > 0 else 0
        
        summary = {
            'model': model_name,
            'total_questions': len(questions),
            'answered': total_answered,
            'errors': error_count,
            'correct': correct_count,
            'accuracy': accuracy,
            'hallucinations_detected': hallucination_count,
            'hallucination_rate': hallucination_rate,
            'avg_latency': avg_latency,
            'avg_tokens': avg_tokens
        }
        
        all_results['results_by_model'][model_name] = {
            'summary': summary,
            'detailed_results': model_results
        }
        
        logger.info(f"\n{model_name.upper()} Summary:")
        logger.info(f"  Answered: {total_answered}/{len(questions)}")
        logger.info(f"  Accuracy: {accuracy:.3f}")
        logger.info(f"  Hallucination Rate: {hallucination_rate:.3f}")
        logger.info(f"  Avg Latency: {avg_latency:.2f}s")
        logger.info(f"  Avg Tokens: {avg_tokens:.1f}")
    
    # Save results
    output_file = output_path / f"comprehensive_results_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"✓ Results saved to: {output_file}")
    logger.info(f"{'='*80}")
    
    # Create summary report
    create_summary_report(all_results, output_path / f"summary_{timestamp}.txt")
    
    return all_results


def create_summary_report(results: Dict, output_file: Path):
    """Create a text summary report"""
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("COMPREHENSIVE HALLUCINATION DETECTION EXPERIMENT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Dataset: {results['dataset']}\n")
        f.write(f"Total Questions: {results['num_questions']}\n")
        f.write(f"Models Tested: {', '.join(results['models'])}\n\n")
        
        f.write("="*80 + "\n")
        f.write("MODEL COMPARISON\n")
        f.write("="*80 + "\n\n")
        
        # Create comparison table
        f.write(f"{'Model':<20} {'Accuracy':<12} {'Halluc.Rate':<15} {'Latency(s)':<12} {'Tokens':<10}\n")
        f.write("-"*80 + "\n")
        
        for model_name, data in results['results_by_model'].items():
            summary = data['summary']
            f.write(f"{model_name:<20} "
                   f"{summary['accuracy']:<12.3f} "
                   f"{summary['hallucination_rate']:<15.3f} "
                   f"{summary['avg_latency']:<12.2f} "
                   f"{summary['avg_tokens']:<10.1f}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("DETAILED STATISTICS\n")
        f.write("="*80 + "\n\n")
        
        for model_name, data in results['results_by_model'].items():
            summary = data['summary']
            f.write(f"\n{model_name.upper()}:\n")
            f.write(f"  Total Questions: {summary['total_questions']}\n")
            f.write(f"  Answered: {summary['answered']}\n")
            f.write(f"  Errors: {summary['errors']}\n")
            f.write(f"  Correct: {summary['correct']}\n")
            f.write(f"  Accuracy: {summary['accuracy']:.1%}\n")
            f.write(f"  Hallucinations: {summary['hallucinations_detected']}\n")
            f.write(f"  Hallucination Rate: {summary['hallucination_rate']:.1%}\n")
            f.write(f"  Avg Latency: {summary['avg_latency']:.2f}s\n")
            f.write(f"  Avg Tokens: {summary['avg_tokens']:.1f}\n")
    
    logger.info(f"✓ Summary report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive hallucination detection experiment')
    parser.add_argument('--models', type=str, default='groq',
                       help='Comma-separated list of models (e.g., groq,gemini,huggingface)')
    parser.add_argument('--dataset', type=str,
                       default='data/comprehensive_qa_dataset.json',
                       help='Path to dataset JSON file')
    parser.add_argument('--output', type=str, default='results/comprehensive',
                       help='Output directory for results')
    parser.add_argument('--sample', type=int, default=None,
                       help='Sample size (use subset of dataset)')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='LLM temperature')
    
    args = parser.parse_args()
    
    models = [m.strip() for m in args.models.split(',')]
    
    run_experiment(
        models=models,
        dataset_path=args.dataset,
        output_dir=args.output,
        sample_size=args.sample,
        temperature=args.temperature
    )


if __name__ == "__main__":
    main()
