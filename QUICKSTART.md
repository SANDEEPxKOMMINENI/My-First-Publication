# Quick Start Guide

Get your LLM Hallucination Research Project up and running in 15 minutes!

## 📋 Prerequisites

- Python 3.6+ (you have 3.6.8 ✓)
- Internet connection for API calls
- Text editor or IDE

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd "/home/2200031970/Working Directory/Local Disk D/Publication/Publication/llm-hallucination-research"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note:** This will take 5-10 minutes. If you encounter any errors:
- Some packages might fail on Python 3.6.8
- You can install them individually or skip optional ones
- Core packages needed: `google-generativeai`, `groq`, `pandas`, `numpy`

### Step 4: Get Free API Keys

#### 🔑 Google Gemini (Recommended - Start Here!)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

**Free Tier:** 15 requests/minute, perfect for research!

#### 🔑 Groq (Fast & Free!)

1. Go to: https://console.groq.com/
2. Sign up with email
3. Navigate to **API Keys** section
4. Click **"Create API Key"**
5. Copy the key (starts with `gsk_...`)

**Free Tier:** 30 requests/minute with Llama 3 70B!

#### 🔑 HuggingFace (Optional)

1. Go to: https://huggingface.co/settings/tokens
2. Sign up if needed
3. Click **"New token"**
4. Copy the token (starts with `hf_...`)

**Free Tier:** Rate limited but usable

### Step 5: Configure API Keys

```bash
# Copy example config
cp configs/api_keys.example.json configs/api_keys.json

# Edit with your keys
nano configs/api_keys.json
# or
vi configs/api_keys.json
```

**Edit the file to add your API keys:**

```json
{
  "gemini": {
    "api_key": "YOUR_GEMINI_KEY_HERE",
    "model": "gemini-1.5-flash",
    "rate_limit_rpm": 15
  },
  "groq": {
    "api_key": "YOUR_GROQ_KEY_HERE",
    "model": "llama3-70b-8192",
    "rate_limit_rpm": 30
  },
  "huggingface": {
    "api_key": "YOUR_HF_TOKEN_HERE",
    "rate_limit_rpm": 10
  }
}
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X in nano)

### Step 6: Test Your Setup

```bash
# Test API connections
python src/models/llm_wrapper.py
```

Expected output:
```
Available providers: ['gemini', 'groq', 'huggingface']

Test generation with gemini:
Response: Paris
Tokens: 23
Latency: 1.23s
```

If you see this, you're ready! 🎉

## 🧪 Run Your First Experiment

### Test 1: Basic Factual QA

```bash
# Run with Gemini
python experiments/factual_qa/run_factual_test.py --model gemini

# Run with Groq (Llama 3)
python experiments/factual_qa/run_factual_test.py --model groq
```

This will:
- Test 15 factual questions
- Detect hallucinations
- Save results to `results/factual_qa/`
- Take ~3-5 minutes

### Test 2: Compare Multiple Models

```bash
# Create comparison script
python experiments/compare_models.py
```

### Test 3: Test Hallucination Detection

```bash
# Run detection analysis
python src/detection/hallucination_detector.py
```

## 📊 View Your Results

Results are saved in JSON format:

```bash
# View results
cat results/factual_qa/gemini_results.json | python -m json.tool

# Or use less for easier reading
cat results/factual_qa/gemini_results.json | python -m json.tool | less
```

## 🎯 Next Steps

### 1. Collect More Data

Create custom test cases in `data/benchmarks/`:

```bash
mkdir -p data/benchmarks
nano data/benchmarks/custom_factual.json
```

### 2. Run Full Experiments

```bash
# Run all experiments
bash experiments/run_all_experiments.sh
```

### 3. Analyze Results

```bash
# Generate plots and tables
python src/evaluation/analyze_results.py
```

### 4. Start Writing Paper

The LaTeX template is ready at `paper/main.tex`:

```bash
# If you have LaTeX installed
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or use **Overleaf** (online LaTeX editor):
1. Go to https://www.overleaf.com/
2. Upload `paper/main.tex` and `paper/references.bib`
3. Compile online!

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution:**
```bash
pip install google-generativeai
```

### Problem: "API key not found"

**Solution:**
- Make sure you copied `api_keys.example.json` to `api_keys.json`
- Verify your keys are correct (no extra spaces)
- Check file location: `configs/api_keys.json`

### Problem: "Rate limit exceeded"

**Solution:**
- Wait 60 seconds
- The code has built-in rate limiting
- Free tiers have limits: Gemini (15/min), Groq (30/min)

### Problem: Python package installation fails

**Solution:**
```bash
# Install minimal required packages
pip install google-generativeai groq pandas numpy matplotlib

# Try without optional packages
pip install -r requirements.txt --ignore-installed
```

### Problem: "Permission denied"

**Solution:**
```bash
# Make sure you're in the right directory
pwd

# Check file permissions
ls -la configs/

# If needed, add read permissions
chmod +r configs/api_keys.json
```

## 💡 Tips for Success

1. **Start with Gemini**: It's the easiest to set up and most reliable
2. **Test incrementally**: Run small experiments first
3. **Monitor rate limits**: Don't exceed free tier limits
4. **Save everything**: Results are in JSON, easy to analyze later
5. **Document as you go**: Add notes to your experiments

## 📚 Learning Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Groq Documentation**: https://console.groq.com/docs
- **arXiv Submission**: https://arxiv.org/help/submit
- **LaTeX Tutorial**: https://www.overleaf.com/learn

## 🎓 Research Timeline

**Week 1-2**: Setup + Baseline Experiments
- ✅ Setup environment (you're here!)
- Run factual QA tests
- Collect initial results

**Week 3-4**: Extended Experiments
- Test more models
- Try different domains
- Analyze patterns

**Week 5-6**: Detection Methods
- Implement detection
- Validate accuracy
- Compare methods

**Week 7-8**: Mitigation Strategies
- Test RAG, CoT, etc.
- Measure effectiveness
- Optimize strategies

**Week 9-12**: Analysis & Writing
- Create visualizations
- Write paper sections
- Prepare for submission

## 🆘 Need Help?

If you run into issues:

1. Check this guide again
2. Read error messages carefully
3. Google the specific error
4. Check API documentation
5. Ask Prof. Prasad for guidance

## ✅ Checklist

Before running experiments, make sure:

- [ ] Python 3.6+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` to check)
- [ ] API keys obtained (Gemini minimum)
- [ ] `configs/api_keys.json` configured
- [ ] Test script runs successfully
- [ ] Results directory created

## 🎉 You're Ready!

You now have:
- ✅ Complete research framework
- ✅ LLM API integrations
- ✅ Hallucination detection system
- ✅ Experiment scripts
- ✅ Paper template

**Start experimenting and good luck with your publication!** 🚀

---

**Questions?** Review the main README.md for more details.
