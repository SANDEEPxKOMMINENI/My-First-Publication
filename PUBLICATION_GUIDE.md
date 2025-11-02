# LLM Hallucination Detection Research - Publication Guide

## 📚 Research Paper Information

**Title:** Detecting and Analyzing Hallucinations in Large Language Models: A Comprehensive Study

**Authors:** [Your Name], Prof. P.V.R. Prasad  
**Institution:** KL University  
**Submission Target:** arXiv  

## 🎯 Project Overview

This research investigates hallucination detection mechanisms in Large Language Models (LLMs) through:
- Comprehensive evaluation across 130+ diverse test cases
- Multi-model comparison (Gemini, Groq/LLaMA, HuggingFace)
- Multiple detection methods (factual verification, self-consistency, contradiction detection)
- Analysis of hallucination triggers and failure patterns

## 📁 Repository Structure

```
llm-hallucination-research/
├── paper/
│   ├── main.tex              # LaTeX paper (arXiv-ready)
│   ├── references.bib        # Bibliography
│   └── figures/              # Paper figures (auto-generated)
├── src/
│   ├── models/
│   │   └── llm_wrapper.py    # Unified LLM API interface
│   ├── detection/
│   │   └── hallucination_detector.py  # Detection algorithms
│   └── evaluation/
│       └── metrics.py        # Evaluation metrics
├── experiments/
│   ├── run_comprehensive_experiment.py  # Main experiment script
│   ├── factual_qa/
│   └── compare_models.py
├── data/
│   └── comprehensive_qa_dataset.json  # 130 test questions
├── scripts/
│   ├── generate_visualizations.py  # Create charts/graphs
│   └── generate_latex_tables.py    # Create LaTeX tables
└── results/
    ├── comprehensive/        # Experimental results
    ├── figures/              # Generated figures
    └── latex_tables.tex      # LaTeX tables for paper
```

## 🚀 Quick Start - Running Experiments

### Prerequisites
```bash
# Python environment (conda recommended)
conda create -n llm_research python=3.13
conda activate llm_research

# Install dependencies
pip install numpy pandas matplotlib seaborn
pip install google-generativeai groq huggingface-hub requests
```

### API Configuration
1. Get API keys:
   - Gemini: https://makersuite.google.com/app/apikey
   - Groq: https://console.groq.com/keys
   - HuggingFace: https://huggingface.co/settings/tokens

2. Configure `configs/api_keys.json`:
```json
{
  "gemini": {
    "api_key": "YOUR_GEMINI_KEY",
    "model": "gemini-1.5-flash",
    "rate_limit_rpm": 15
  },
  "groq": {
    "api_key": "YOUR_GROQ_KEY",
    "model": "llama-3.3-70b-versatile",
    "rate_limit_rpm": 30
  }
}
```

### Run Experiments

```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run full experiment (130 questions, all models)
python experiments/run_comprehensive_experiment.py \
    --models groq,gemini \
    --output results/comprehensive

# Run with sample size for testing
python experiments/run_comprehensive_experiment.py \
    --models groq \
    --sample 50 \
    --output results/comprehensive
```

### Generate Visualizations

```bash
# Create all charts and figures
python scripts/generate_visualizations.py \
    results/comprehensive/comprehensive_results_*.json \
    results/figures

# Generate LaTeX tables
python scripts/generate_latex_tables.py \
    results/comprehensive/comprehensive_results_*.json \
    results/latex_tables.tex
```

## 📊 Dataset Information

**Total Questions:** 130  
**Categories:**
- Factual Geography (10 questions)
- Factual History (10 questions)
- Science - Physics (10 questions)
- Science - Chemistry (10 questions)
- Science - Biology (10 questions)
- Mathematics - Basic (10 questions)
- Mathematics - Advanced (10 questions)
- Arts - Literature (10 questions)
- Arts - Visual (10 questions)
- Technology (10 questions)
- Hallucination-Prone - Counting (5 questions)
- Hallucination-Prone - Recent Events (5 questions)
- Hallucination-Prone - Ambiguous (5 questions)
- Hallucination-Prone - False Premises (5 questions)
- Reasoning - Logical (5 questions)
- Reasoning - Commonsense (5 questions)

**Difficulty Levels:** Easy, Medium, Hard  
**Special Features:** Hallucination trigger questions, false premise questions

## 🔬 Detection Methods Implemented

1. **Factual Verification**: Compare model outputs against ground truth
2. **Self-Consistency**: Sample multiple times and check agreement
3. **Contradiction Detection**: Identify internal contradictions
4. **Temporal Error Detection**: Verify chronological accuracy
5. **Entity Verification**: Validate named entities

## 📈 Metrics Tracked

- **Accuracy**: Percentage of correct answers
- **Hallucination Rate**: Percentage of hallucinated responses
- **Latency**: Response time per question
- **Token Usage**: Average tokens per response
- **Category-wise Performance**: Breakdown by question category
- **Difficulty Analysis**: Performance across difficulty levels

## 📝 Compiling the Paper

```bash
cd paper/

# Compile LaTeX
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Output: main.pdf
```

### Before Submission to arXiv

1. ✅ Run all experiments with full dataset
2. ✅ Generate all figures and save as PDF/PNG
3. ✅ Copy figures to `paper/figures/`
4. ✅ Insert LaTeX tables from `results/latex_tables.tex` into main.tex
5. ✅ Fill in results section with actual experimental data
6. ✅ Verify all references in references.bib
7. ✅ Check arXiv submission guidelines
8. ✅ Validate PDF output
9. ✅ Create arXiv submission package

## 📦 Creating arXiv Submission Package

```bash
# Create submission directory
mkdir arxiv_submission
cd paper/

# Copy necessary files
cp main.tex references.bib ../arxiv_submission/
cp figures/*.png ../arxiv_submission/
cp figures/*.pdf ../arxiv_submission/

# Create tarball
cd ../arxiv_submission
tar -czf llm_hallucination_paper.tar.gz *

# Upload llm_hallucination_paper.tar.gz to arXiv
```

## 🎯 Publication Checklist

### Research Completion
- [x] Comprehensive dataset created (130+ questions)
- [x] Multiple models tested (Groq, Gemini, HuggingFace)
- [x] Detection algorithms implemented
- [x] Evaluation metrics calculated
- [ ] Full experimental results collected
- [ ] Statistical analysis completed

### Paper Completion
- [x] LaTeX template created
- [x] References compiled (20+ papers)
- [ ] Abstract written with results
- [ ] Introduction completed
- [ ] Related work section filled
- [ ] Methodology section complete
- [ ] Results section with tables/figures
- [ ] Discussion section written
- [ ] Conclusion written
- [ ] All figures generated and included

### Pre-Submission
- [ ] Paper reviewed by supervisor (Prof. P.V.R. Prasad)
- [ ] All experiments replicated successfully
- [ ] Figures are publication quality (300 DPI)
- [ ] All tables formatted correctly
- [ ] References verified and complete
- [ ] LaTeX compiles without errors
- [ ] PDF meets arXiv requirements

## 📧 Contact

**Student:** [Your Name]  
**Email:** [Your Email]  
**Supervisor:** Prof. P.V.R. Prasad  
**Institution:** KL University  

## 📄 License

This research code is provided for academic and educational purposes.

## 🙏 Acknowledgments

- Prof. P.V.R. Prasad (Research Supervisor)
- KL University
- Google Gemini API (Free Tier)
- Groq API (Free Tier)
- HuggingFace Inference API

---

**Last Updated:** November 2, 2025  
**Paper Status:** In Progress  
**Expected Submission:** [Your Target Date]
