"""
Factual Question Answering Experiment
Tests hallucination on factual knowledge questions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import json
import logging
from pathlib import Path
from typing import Dict, List
import argparse

from src.models.llm_wrapper import LLMWrapper
from src.detection.hallucination_detector import HallucinationDetector
from src.evaluation.metrics import EvaluationMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample factual questions with ground truth
FACTUAL_QA_DATASET = [
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "category": "geography",
        "difficulty": "easy"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "answer": "William Shakespeare",
        "category": "literature",
        "difficulty": "easy"
    },
    {
        "question": "In what year did World War II end?",
        "answer": "1945",
        "category": "history",
        "difficulty": "easy"
    },
    {
        "question": "What is the speed of light in vacuum?",
        "answer": "299,792,458 meters per second",
        "category": "science",
        "difficulty": "medium"
    },
    {
        "question": "Who was the first person to walk on the moon?",
        "answer": "Neil Armstrong",
        "category": "history",
        "difficulty": "easy"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "answer": "Au",
        "category": "science",
        "difficulty": "easy"
    },
    {
        "question": "How many continents are there on Earth?",
        "answer": "7",
        "category": "geography",
        "difficulty": "easy"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "answer": "Jupiter",
        "category": "science",
        "difficulty": "easy"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "answer": "Leonardo da Vinci",
        "category": "art",
        "difficulty": "easy"
    },
    {
        "question": "What is the smallest prime number?",
        "answer": "2",
        "category": "mathematics",
        "difficulty": "easy"
    },
    {
        "question": "In what year was the United Nations founded?",
        "answer": "1945",
        "category": "history",
        "difficulty": "medium"
    },
    {
        "question": "What is the boiling point of water at sea level in Celsius?",
        "answer": "100",
        "category": "science",
        "difficulty": "easy"
    },
    {
        "question": "Who developed the theory of relativity?",
        "answer": "Albert Einstein",
        "category": "science",
        "difficulty": "easy"
    },
    {
        "question": "What is the capital of Japan?",
        "answer": "Tokyo",
        "category": "geography",
        "difficulty": "easy"
    },
    {
        "question": "How many legs does a spider have?",
        "answer": "8",
        "category": "biology",
        "difficulty": "easy"
    },
]


def run_factual_qa_experiment(
    model_name: str = "gemini",
    output_dir: str = "results/factual_qa",
    run_detection: bool = True
):
    """
    Run factual QA experiment
    
    Args:
        model_name: LLM provider to test
        output_dir: Directory to save results
        run_detection: Whether to run hallucination detection
    """
    logger.info(f"Starting Factual QA Experiment with {model_name}")
    logger.info(f"Dataset size: {len(FACTUAL_QA_DATASET)} questions")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize LLM wrapper
    try:
        llm = LLMWrapper()
        if model_name not in llm.get_available_providers():
            logger.error(f"Model {model_name} not available. Available: {llm.get_available_providers()}")
            return
    except Exception as e:
        logger.error(f"Failed to initialize LLM wrapper: {e}")
        return
    
    # Initialize detector if needed
    detector = HallucinationDetector(llm) if run_detection else None
    
    # Run experiment
    results = []
    
    for i, qa in enumerate(FACTUAL_QA_DATASET):
        logger.info(f"\n{'='*60}")
        logger.info(f"Question {i+1}/{len(FACTUAL_QA_DATASET)}")
        logger.info(f"Q: {qa['question']}")
        logger.info(f"Expected: {qa['answer']}")
        
        try:
            # Generate response
            response = llm.generate(
                qa['question'],
                provider=model_name,
                temperature=0.7,
                max_tokens=100
            )
            
            logger.info(f"Model: {response.text}")
            
            # Check if correct
            is_correct = qa['answer'].lower() in response.text.lower()
            
            result = {
                'question_id': i,
                'question': qa['question'],
                'ground_truth': qa['answer'],
                'model_response': response.text,
                'model': response.model,
                'provider': response.provider,
                'category': qa['category'],
                'difficulty': qa['difficulty'],
                'is_correct': is_correct,
                'tokens_used': response.tokens_used,
                'latency': response.latency
            }
            
            # Run detection if enabled
            if detector and run_detection:
                detection_result = detector.detect_factual_error(
                    response.text,
                    qa['answer']
                )
                
                result['detection'] = {
                    'is_hallucination': detection_result.is_hallucination,
                    'confidence': detection_result.confidence,
                    'hallucination_type': detection_result.hallucination_type,
                    'evidence': detection_result.evidence
                }
                
                logger.info(f"Detection: Hallucination={detection_result.is_hallucination}, "
                          f"Confidence={detection_result.confidence:.3f}")
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error processing question {i+1}: {e}")
            results.append({
                'question_id': i,
                'question': qa['question'],
                'error': str(e)
            })
    
    # Calculate overall metrics
    logger.info(f"\n{'='*60}")
    logger.info("RESULTS SUMMARY")
    logger.info(f"{'='*60}")
    
    valid_results = [r for r in results if 'is_correct' in r]
    
    if valid_results:
        accuracy = sum(r['is_correct'] for r in valid_results) / len(valid_results)
        hallucination_rate = 1 - accuracy
        
        logger.info(f"Total Questions: {len(valid_results)}")
        logger.info(f"Correct Answers: {sum(r['is_correct'] for r in valid_results)}")
        logger.info(f"Accuracy: {accuracy:.3f}")
        logger.info(f"Hallucination Rate: {hallucination_rate:.3f}")
        
        # Calculate by category
        categories = {}
        for r in valid_results:
            cat = r['category']
            if cat not in categories:
                categories[cat] = {'correct': 0, 'total': 0}
            categories[cat]['total'] += 1
            if r['is_correct']:
                categories[cat]['correct'] += 1
        
        logger.info(f"\nAccuracy by Category:")
        for cat, stats in categories.items():
            cat_acc = stats['correct'] / stats['total']
            logger.info(f"  {cat}: {cat_acc:.3f} ({stats['correct']}/{stats['total']})")
        
        # Average tokens and latency
        avg_tokens = sum(r['tokens_used'] for r in valid_results) / len(valid_results)
        avg_latency = sum(r['latency'] for r in valid_results) / len(valid_results)
        
        logger.info(f"\nPerformance:")
        logger.info(f"  Avg Tokens: {avg_tokens:.1f}")
        logger.info(f"  Avg Latency: {avg_latency:.2f}s")
    
    # Save results
    output_file = output_path / f"{model_name}_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'experiment': 'factual_qa',
            'model': model_name,
            'num_questions': len(FACTUAL_QA_DATASET),
            'results': results,
            'summary': {
                'accuracy': accuracy if valid_results else 0,
                'hallucination_rate': hallucination_rate if valid_results else 0,
                'categories': categories if valid_results else {}
            }
        }, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Run Factual QA Experiment")
    parser.add_argument('--model', type=str, default='gemini',
                       help='LLM provider to test (gemini, groq, huggingface)')
    parser.add_argument('--output-dir', type=str, default='results/factual_qa',
                       help='Output directory for results')
    parser.add_argument('--no-detection', action='store_true',
                       help='Disable hallucination detection')
    
    args = parser.parse_args()
    
    run_factual_qa_experiment(
        model_name=args.model,
        output_dir=args.output_dir,
        run_detection=not args.no_detection
    )


if __name__ == "__main__":
    main()
