#!/usr/bin/env python3
"""
Generate LaTeX tables for research paper
"""

import json
from pathlib import Path
from typing import Dict


def load_results(results_path: str) -> Dict:
    """Load experimental results"""
    with open(results_path, 'r') as f:
        return json.load(f)


def generate_model_comparison_table(results: Dict) -> str:
    """Generate LaTeX table comparing models"""
    latex = r"""\begin{table}[h]
\centering
\caption{Model Performance Comparison}
\label{tab:model_comparison}
\begin{tabular}{lcccc}
\toprule
\textbf{Model} & \textbf{Accuracy (\%)} & \textbf{Halluc. Rate (\%)} & \textbf{Latency (s)} & \textbf{Tokens} \\
\midrule
"""
    
    for model_name, data in results['results_by_model'].items():
        summary = data['summary']
        latex += f"{model_name.upper():15s} & "
        latex += f"{summary['accuracy']*100:5.1f} & "
        latex += f"{summary['hallucination_rate']*100:5.1f} & "
        latex += f"{summary['avg_latency']:5.2f} & "
        latex += f"{summary['avg_tokens']:5.1f} \\\\\n"
    
    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    return latex


def generate_category_breakdown_table(results: Dict) -> str:
    """Generate LaTeX table with category-wise performance"""
    for model_name, data in results['results_by_model'].items():
        category_stats = {}
        
        for result in data['detailed_results']:
            if 'category' not in result:
                continue
            
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'correct': 0, 'total': 0, 'hallucinations': 0}
            
            category_stats[category]['total'] += 1
            if result.get('is_correct', False):
                category_stats[category]['correct'] += 1
            if result.get('detection', {}).get('is_hallucination', False):
                category_stats[category]['hallucinations'] += 1
        
        latex = f"""\\begin{{table}}[h]
\\centering
\\caption{{{model_name.upper()} - Performance by Category}}
\\label{{tab:category_{model_name}}}
\\begin{{tabular}}{{lccc}}
\\toprule
\\textbf{{Category}} & \\textbf{{Accuracy (\\%)}} & \\textbf{{Halluc. Rate (\\%)}} & \\textbf{{Sample Size}} \\\\
\\midrule
"""
        
        for category in sorted(category_stats.keys()):
            stats = category_stats[category]
            accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
            halluc_rate = stats['hallucinations'] / stats['total'] * 100 if stats['total'] > 0 else 0
            
            latex += f"{category.replace('_', ' ').title():30s} & "
            latex += f"{accuracy:5.1f} & "
            latex += f"{halluc_rate:5.1f} & "
            latex += f"{stats['total']:3d} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}

"""
        return latex


def generate_difficulty_table(results: Dict) -> str:
    """Generate LaTeX table with difficulty analysis"""
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
        
        latex = f"""\\begin{{table}}[h]
\\centering
\\caption{{{model_name.upper()} - Performance by Difficulty Level}}
\\label{{tab:difficulty_{model_name}}}
\\begin{{tabular}}{{lccc}}
\\toprule
\\textbf{{Difficulty}} & \\textbf{{Accuracy (\\%)}} & \\textbf{{Halluc. Rate (\\%)}} & \\textbf{{Sample Size}} \\\\
\\midrule
"""
        
        for difficulty in ['easy', 'medium', 'hard']:
            if difficulty not in difficulty_stats:
                continue
            stats = difficulty_stats[difficulty]
            accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
            halluc_rate = stats['hallucinations'] / stats['total'] * 100 if stats['total'] > 0 else 0
            
            latex += f"{difficulty.capitalize():15s} & "
            latex += f"{accuracy:5.1f} & "
            latex += f"{halluc_rate:5.1f} & "
            latex += f"{stats['total']:3d} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}

"""
        return latex


def generate_all_tables(results_path: str, output_file: str = "results/latex_tables.tex"):
    """Generate all LaTeX tables"""
    print(f"\n{'='*80}")
    print("GENERATING LATEX TABLES FOR PAPER")
    print(f"{'='*80}\n")
    
    results = load_results(results_path)
    
    output = []
    output.append("% Generated LaTeX tables for research paper\n")
    output.append("% Insert these into your paper/main.tex file\n\n")
    
    print("Generating model comparison table...")
    output.append("% Model Comparison Table\n")
    output.append(generate_model_comparison_table(results))
    output.append("\n")
    
    print("Generating category breakdown tables...")
    output.append("% Category Performance Tables\n")
    output.append(generate_category_breakdown_table(results))
    output.append("\n")
    
    print("Generating difficulty analysis tables...")
    output.append("% Difficulty Level Tables\n")
    output.append(generate_difficulty_table(results))
    output.append("\n")
    
    # Save to file
    with open(output_file, 'w') as f:
        f.writelines(output)
    
    print(f"\n{'='*80}")
    print(f"✓ LaTeX tables saved to: {output_file}")
    print(f"{'='*80}\n")
    print("Copy these tables into your paper/main.tex file in the results section.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_latex_tables.py <results_json_file>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "results/latex_tables.tex"
    
    generate_all_tables(results_file, output_file)
