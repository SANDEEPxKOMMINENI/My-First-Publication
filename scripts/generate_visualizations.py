#!/usr/bin/env python3
"""
Create visualizations for publication
Generates charts, graphs, and figures for the research paper
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List
import seaborn as sns

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (8, 6)


def load_results(results_path: str) -> Dict:
    """Load experimental results"""
    with open(results_path, 'r') as f:
        return json.load(f)


def plot_model_comparison(results: Dict, output_dir: Path):
    """Create model comparison bar chart"""
    models = []
    accuracies = []
    hallucination_rates = []
    
    for model_name, data in results['results_by_model'].items():
        summary = data['summary']
        models.append(model_name.upper())
        accuracies.append(summary['accuracy'] * 100)
        hallucination_rates.append(summary['hallucination_rate'] * 100)
    
    x = np.arange(len(models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, accuracies, width, label='Accuracy (%)', color='#2ecc71')
    bars2 = ax.bar(x + width/2, hallucination_rates, width, label='Hallucination Rate (%)', color='#e74c3c')
    
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontweight='bold')
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'model_comparison.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")


def plot_category_performance(results: Dict, output_dir: Path):
    """Create performance by category heatmap"""
    # Collect category-wise accuracy
    for model_name, data in results['results_by_model'].items():
        category_stats = {}
        
        for result in data['detailed_results']:
            if 'category' not in result:
                continue
            
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'correct': 0, 'total': 0}
            
            category_stats[category]['total'] += 1
            if result.get('is_correct', False):
                category_stats[category]['correct'] += 1
        
        # Calculate accuracies
        categories = list(category_stats.keys())
        accuracies = [category_stats[c]['correct'] / category_stats[c]['total'] * 100 
                     if category_stats[c]['total'] > 0 else 0 
                     for c in categories]
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(categories, accuracies, color='#3498db')
        
        ax.set_xlabel('Accuracy (%)', fontweight='bold')
        ax.set_ylabel('Category', fontweight='bold')
        ax.set_title(f'{model_name.upper()} - Performance by Category', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 105)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}%',
                   ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        output_file = output_dir / f'category_performance_{model_name}.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")


def plot_difficulty_analysis(results: Dict, output_dir: Path):
    """Analyze performance by difficulty level"""
    for model_name, data in results['results_by_model'].items():
        difficulty_stats = {}
        
        for result in data['detailed_results']:
            if 'difficulty' not in result:
                continue
            
            difficulty = result['difficulty']
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {'correct': 0, 'total': 0, 'hallucinations': 0}
            
            difficulty_stats[difficulty]['total'] += 1
            if result.get('is_correct', False):
                difficulty_stats[difficulty]['correct'] += 1
            if result.get('detection', {}).get('is_hallucination', False):
                difficulty_stats[difficulty]['hallucinations'] += 1
        
        difficulties = ['easy', 'medium', 'hard']
        difficulties = [d for d in difficulties if d in difficulty_stats]
        
        accuracies = [difficulty_stats[d]['correct'] / difficulty_stats[d]['total'] * 100 
                     if difficulty_stats[d]['total'] > 0 else 0 
                     for d in difficulties]
        hallucination_rates = [difficulty_stats[d]['hallucinations'] / difficulty_stats[d]['total'] * 100 
                              if difficulty_stats[d]['total'] > 0 else 0 
                              for d in difficulties]
        
        x = np.arange(len(difficulties))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(x - width/2, accuracies, width, label='Accuracy (%)', color='#2ecc71')
        ax.bar(x + width/2, hallucination_rates, width, label='Hallucination Rate (%)', color='#e74c3c')
        
        ax.set_xlabel('Difficulty Level', fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontweight='bold')
        ax.set_title(f'{model_name.upper()} - Performance by Difficulty', fontweight='bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels([d.capitalize() for d in difficulties])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = output_dir / f'difficulty_analysis_{model_name}.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")


def plot_hallucination_triggers(results: Dict, output_dir: Path):
    """Analyze hallucination trigger questions"""
    for model_name, data in results['results_by_model'].items():
        trigger_stats = {'trigger': {'correct': 0, 'total': 0, 'hallucinations': 0},
                        'normal': {'correct': 0, 'total': 0, 'hallucinations': 0}}
        
        for result in data['detailed_results']:
            if 'hallucination_trigger' not in result:
                continue
            
            category = 'trigger' if result['hallucination_trigger'] else 'normal'
            trigger_stats[category]['total'] += 1
            
            if result.get('is_correct', False):
                trigger_stats[category]['correct'] += 1
            if result.get('detection', {}).get('is_hallucination', False):
                trigger_stats[category]['hallucinations'] += 1
        
        categories = ['Normal Questions', 'Hallucination-Prone Questions']
        accuracies = [
            trigger_stats['normal']['correct'] / trigger_stats['normal']['total'] * 100 if trigger_stats['normal']['total'] > 0 else 0,
            trigger_stats['trigger']['correct'] / trigger_stats['trigger']['total'] * 100 if trigger_stats['trigger']['total'] > 0 else 0
        ]
        hallucination_rates = [
            trigger_stats['normal']['hallucinations'] / trigger_stats['normal']['total'] * 100 if trigger_stats['normal']['total'] > 0 else 0,
            trigger_stats['trigger']['hallucinations'] / trigger_stats['trigger']['total'] * 100 if trigger_stats['trigger']['total'] > 0 else 0
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, accuracies, width, label='Accuracy (%)', color='#2ecc71')
        ax.bar(x + width/2, hallucination_rates, width, label='Hallucination Rate (%)', color='#e74c3c')
        
        ax.set_xlabel('Question Type', fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontweight='bold')
        ax.set_title(f'{model_name.upper()} - Hallucination Trigger Analysis', fontweight='bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = output_dir / f'hallucination_triggers_{model_name}.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")


def plot_latency_comparison(results: Dict, output_dir: Path):
    """Create latency comparison"""
    models = []
    latencies = []
    
    for model_name, data in results['results_by_model'].items():
        summary = data['summary']
        models.append(model_name.upper())
        latencies.append(summary['avg_latency'])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(models, latencies, color='#9b59b6')
    
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_ylabel('Average Latency (seconds)', fontweight='bold')
    ax.set_title('Model Latency Comparison', fontweight='bold', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}s',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'latency_comparison.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")


def generate_all_visualizations(results_path: str, output_dir: str = "results/figures"):
    """Generate all publication figures"""
    print(f"\n{'='*80}")
    print("GENERATING PUBLICATION FIGURES")
    print(f"{'='*80}\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = load_results(results_path)
    
    print("Creating visualizations...")
    plot_model_comparison(results, output_path)
    plot_category_performance(results, output_path)
    plot_difficulty_analysis(results, output_path)
    plot_hallucination_triggers(results, output_path)
    plot_latency_comparison(results, output_path)
    
    print(f"\n{'='*80}")
    print(f"✓ All figures saved to: {output_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_visualizations.py <results_json_file>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results/figures"
    
    generate_all_visualizations(results_file, output_dir)
