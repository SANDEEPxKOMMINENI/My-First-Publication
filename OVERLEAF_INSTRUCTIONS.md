# 📝 Overleaf Compilation Instructions

**Status**: All files ready for upload ✅  
**Location**: `paper/overleaf_upload/` directory  
**Files**: 1 .tex, 1 .bib, 5 .png figures

---

## Step 1: Download Files from Server (2 minutes)

### Option A: Download Individual Files
In VS Code file explorer, navigate to:
```
paper/overleaf_upload/
```

Download these files:
- ✅ `main.tex` (23 KB)
- ✅ `references.bib` (6.5 KB)
- ✅ `figures/` folder (5 PNG files, 588 KB total)

### Option B: Download the Tarball (Recommended)
Navigate to:
```
paper/arxiv_submission.tar.gz (424 KB)
```
Right-click → Download → Extract on your local computer

---

## Step 2: Create Overleaf Account (3 minutes)

1. Go to **https://www.overleaf.com/**
2. Click **"Register"** (top right)
3. Sign up with:
   - Email address
   - Or Google/ORCID account
4. Verify your email
5. Log in

**Note**: Free account is sufficient! No payment required.

---

## Step 3: Create New Project (5 minutes)

1. Click **"New Project"** (green button)
2. Select **"Upload Project"**
3. Choose one of:
   - **Option A**: Upload the extracted `arxiv_submission.tar.gz`
   - **Option B**: Drag & drop the `overleaf_upload` folder
   - **Option C**: Click "Select a .zip file" → create a ZIP from overleaf_upload folder first

4. Overleaf will extract and show the file structure:
   ```
   main.tex
   references.bib
   figures/
     ├── category_performance_groq.png
     ├── difficulty_analysis_groq.png
     ├── hallucination_triggers_groq.png
     ├── latency_comparison.png
     └── model_comparison.png
   ```

---

## Step 4: Compile the Paper (2 minutes)

1. Overleaf will auto-compile when you upload
2. If not, click **"Recompile"** (green button at top)
3. Wait 30-60 seconds for compilation
4. PDF preview appears on the right side

### Expected Compilation Process:
```
Running pdflatex...
Running bibtex...
Running pdflatex...
Running pdflatex...
✅ Success! PDF generated
```

---

## Step 5: Review the PDF (10 minutes)

### ✅ Check These Items:

**Page 1 - Title & Abstract**
- [ ] Title appears correctly
- [ ] Authors and affiliations shown
- [ ] Abstract with real numbers (80.8% accuracy, 14.6% hallucination)
- [ ] Keywords listed

**Pages 2-4 - Introduction & Related Work**
- [ ] Section numbering correct
- [ ] Citations appear as [1], [2], etc.
- [ ] No red "?" marks for missing references

**Pages 5-6 - Methodology**
- [ ] Figure references work (e.g., "Figure 1")
- [ ] Table references work (e.g., "Table 1")
- [ ] Equations formatted correctly

**Pages 7-10 - Results Section (MOST IMPORTANT)**
- [ ] **Table 1**: Overall performance metrics
  - [ ] Shows: GROQ, 80.8% accuracy, 14.6% hallucination, 2.16s latency
  - [ ] Formatted with horizontal lines (booktabs style)
- [ ] **Table 2**: Category breakdown
  - [ ] Shows all 15 categories
  - [ ] Accuracy and hallucination counts visible
  - [ ] No text overflow
- [ ] **Table 3**: Difficulty analysis
  - [ ] Easy, Medium, Hard rows
  - [ ] Percentages displayed correctly
- [ ] **Figure 1**: Difficulty analysis chart (should show bar graph)
- [ ] **Figure 2**: Category performance chart (should show horizontal bars)
- [ ] **Figure 3**: Hallucination triggers chart (should show comparison bars)
- [ ] All captions appear below figures/tables

**Pages 11-12 - Discussion**
- [ ] 5 key findings numbered correctly
- [ ] Implications section formatted
- [ ] Limitations section present

**Pages 13-14 - Conclusion**
- [ ] 5 contributions enumerated
- [ ] Future work listed
- [ ] Acknowledgments section

**Page 15+ - References**
- [ ] Bibliography appears
- [ ] 40+ references listed
- [ ] No "?" marks or missing citations
- [ ] Formatted consistently

---

## Step 6: Fix Any Issues (if needed)

### Common Issues & Solutions:

**Issue 1: Figures don't appear**
```latex
Solution: Check figures/ directory is uploaded
Verify filenames match exactly in main.tex
```

**Issue 2: Bibliography missing**
```latex
Solution: Click Menu → Recompile from scratch
Or: Settings → Set compiler to pdfLaTeX
```

**Issue 3: Table overflow**
```latex
Solution: In main.tex, add \small before table
Or: Adjust column widths
```

**Issue 4: Missing packages**
```latex
Solution: Overleaf auto-installs packages
If error persists, check LaTeX error log
```

---

## Step 7: Download the PDF (1 minute)

Once satisfied with the PDF:

1. Click **"Download PDF"** button (top right, next to Recompile)
2. Save as: `llm_hallucination_paper_v1.pdf`
3. **Also download source**: Menu → Download → Source (ZIP)
   - This gives you a backup of the compiled project

---

## Step 8: Final Validation (5 minutes)

Open the downloaded PDF and verify:

### Content Checklist
- [ ] 15+ pages total
- [ ] All sections present
- [ ] 3 tables rendered correctly
- [ ] 3 figures visible and clear
- [ ] Bibliography complete
- [ ] No LaTeX errors or warnings visible in text

### Visual Quality Check
- [ ] Figures are high quality (not pixelated)
- [ ] Text is readable at 100% zoom
- [ ] Tables fit within page margins
- [ ] Equations look professional
- [ ] No overlapping text or images

### Data Accuracy Check
- [ ] Abstract says "130 questions"
- [ ] Abstract says "14.6% hallucination rate"
- [ ] Table 1 shows "80.8%" accuracy
- [ ] Table 2 has 15 category rows
- [ ] Table 3 shows easy/medium/hard breakdown
- [ ] Discussion mentions "6-fold increase"

---

## Troubleshooting

### If Compilation Fails:

1. **Check the error log**:
   - Click on the red error icon
   - Read the error message
   - Common: Missing file, syntax error, package issue

2. **Verify file structure**:
   ```
   main.tex          ← Must be at root level
   references.bib    ← Must be at root level
   figures/          ← Must be a folder
     └── *.png       ← All PNG files inside
   ```

3. **Re-upload if needed**:
   - Delete project
   - Start fresh with Step 3

### If Tables Look Wrong:

1. Open `main.tex` in Overleaf editor
2. Search for the problematic table
3. Adjust column widths or add `\small`
4. Recompile

### If Figures Are Missing:

1. Check "Files" panel in Overleaf (left sidebar)
2. Verify all 5 PNG files are there
3. If missing, upload manually:
   - Click "Upload" button
   - Select the PNG files
   - Put them in `figures/` folder

---

## Next Steps After Successful Compilation

Once you have a clean PDF with no errors:

### ✅ You're Ready for arXiv!

Proceed to: **ARXIV_SUBMISSION.md** for submission instructions

Or follow these quick steps:

1. **Create arXiv account**: https://arxiv.org/
2. **Submit new paper**:
   - Category: cs.CL (Computation and Language)
   - Upload: Either PDF only, or source files (tarball)
   - Abstract: Copy from paper
   - Title: Copy from paper
3. **Submit for moderation**
4. **Wait 1-2 business days**
5. **Get arXiv ID** (e.g., arXiv:2411.xxxxx)
6. **Celebrate!** 🎉

---

## Summary

**Time Required**: ~30 minutes total
- Download files: 2 min
- Create Overleaf account: 3 min
- Upload & compile: 5 min
- Review PDF: 10 min
- Fixes (if any): 5 min
- Final checks: 5 min

**What You'll Have**:
- ✅ Compiled PDF ready for arXiv
- ✅ Source files backed up on Overleaf
- ✅ Confidence that everything renders correctly

**Support**:
- Overleaf Help: https://www.overleaf.com/learn
- LaTeX Help: https://www.latex-project.org/help/
- arXiv Help: https://info.arxiv.org/help/

---

**Good luck with your submission! 🚀**

Your research makes real contributions to understanding LLM hallucinations. You should be proud of this work!
