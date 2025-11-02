"""
Compare multiple LLM models on hallucination tasks
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
import logging
from pathlib import Path
from typing import List, Dict
import argparse

from src.models.llm_wrapper import LLMWrapper
from src.detection.hallucination_detector import HallucinationDetector
from src.evaluation.metrics import EvaluationMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test questions with ground truth
TEST_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "category": "geography"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "answer": "William Shakespeare",
        "category": "literature"
    },
    {
        "question": "What is 15 × 7?",
        "answer": "105",
        "category": "math"
    },
    {
        "question": "In what year did World War II end?",
        "answer": "1945",
        "category": "history"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "answer": "Au",
        "category": "science"
    },
]


def compare_models(
    models: List[str],
    output_dir: str = "results/model_comparison"
):
    """
    Compare multiple LLM models
    
    Args:
        models: List of model names to compare
        output_dir: Directory to save results
    """
    logger.info(f"Comparing models: {models}")
    logger.info(f"Test questions: {len(TEST_QUESTIONS)}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize LLM wrapper
    try:
        llm = LLMWrapper()
        available = llm.get_available_providers()
        
        # Filter to available models
        models = [m for m in models if m in available]
        if not models:
            logger.error(f"No models available. Please configure API keys.")
            return
        
        logger.info(f"Testing models: {models}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM wrapper: {e}")
        return
    
    # Initialize detector
    detector = HallucinationDetector(llm)
    
    # Store all results
    all_results = {}
    
    # Test each model
    for model_name in models:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing Model: {model_name.upper()}")
        logger.info(f"{'='*60}")
        
        model_results = []
        
        for i, qa in enumerate(TEST_QUESTIONS):
            logger.info(f"\nQuestion {i+1}/{len(TEST_QUESTIONS)}: {qa['question']}")
            
            try:
                # Generate response
                response = llm.generate(
                    qa['question'],
                    provider=model_name,
                    temperature=0.7,
                    max_tokens=50
                )
                
                logger.info(f"Answer: {response.text}")
                logger.info(f"Expected: {qa['answer']}")
                
                # Check correctness
                is_correct = qa['answer'].lower() in response.text.lower()
                
                # Detect hallucination
                detection = detector.detect_factual_error(
                    response.text,
                    qa['answer']
                )
                
                result = {
                    'question': qa['question'],
                    'ground_truth': qa['answer'],
                    'model_response': response.text,
                    'category': qa['category'],
                    'is_correct': is_correct,
                    'is_hallucination': detection.is_hallucination,
                    'detection_confidence': detection.confidence,
                    'tokens_used': response.tokens_used,
                    'latency': response.latency
                }
                
                model_results.append(result)
                
                logger.info(f"✓ Correct: {is_correct}")
                logger.info(f"✗ Hallucination: {detection.is_hallucination}")
                
            except Exception as e:
                logger.error(f"Error: {e}")
                model_results.append({
                    'question': qa['question'],
                    'error': str(e)
                })
        
        all_results[model_name] = model_results
        
        # Calculate metrics for this model
        valid_results = [r for r in model_results if 'is_correct' in r]
        if valid_results:
            accuracy = sum(r['is_correct'] for r in valid_results) / len(valid_results)
            hallucination_rate = sum(r['is_hallucination'] for r in valid_results) / len(valid_results)
            avg_latency = sum(r['latency'] for r in valid_results) / len(valid_results)
            
            logger.info(f"\n{model_name.upper()} Summary:")
            logger.info(f"  Accuracy: {accuracy:.3f}")
            logger.info(f"  Hallucination Rate: {hallucination_rate:.3f}")
            logger.info(f"  Avg Latency: {avg_latency:.2f}s")
    
    # Overall comparison
    logger.info(f"\n{'='*60}")
    logger.info("OVERALL COMPARISON")
    logger.info(f"{'='*60}")
    
    comparison_table = []
    for model_name, results in all_results.items():
        valid_results = [r for r in results if 'is_correct' in r]
        if valid_results:
            comparison_table.append({
                'model': model_name,
                'accuracy': sum(r['is_correct'] for r in valid_results) / len(valid_results),
                'hallucination_rate': sum(r['is_hallucination'] for r in valid_results) / len(valid_results),
                'avg_latency': sum(r['latency'] for r in valid_results) / len(valid_results),
                'num_samples': len(valid_results)
            })
    
    # Sort by accuracy
    comparison_table.sort(key=lambda x: x['accuracy'], reverse=True)
    
    # Print comparison table
    logger.info(f"\n{'Model':<15} {'Accuracy':<12} {'Halluc.Rate':<15} {'Latency(s)':<12}")
    logger.info("-" * 60)
    for row in comparison_table:
        logger.info(
            f"{row['model']:<15} "
            f"{row['accuracy']:<12.3f} "
            f"{row['hallucination_rate']:<15.3f} "
            f"{row['avg_latency']:<12.2f}"
        )
    
    # Save results
    output_file = output_path / "comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'models': models,
            'num_questions': len(TEST_QUESTIONS),
            'detailed_results': all_results,
            'comparison_summary': comparison_table
        }, f, indent=2)
    
    logger.info(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Compare Multiple LLM Models")
    parser.add_argument(
        '--models',
        type=str,
        default='gemini,groq',
        help='Comma-separated list of models to compare (e.g., gemini,groq,huggingface)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results/model_comparison',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    models = [m.strip() for m in args.models.split(',')]
    
    compare_models(
        models=models,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
