# Manual GitHub Upload Guide for Large Projects

## Problem Analysis
Your project is approximately **1.3GB** total, with the main issues being:
- Virtual environment folders (`venv/`) - ~1.2GB
- Database files (`bnpl_simulator.db`) - 10MB+
- Large CSV datasets (`bnpl_dataset_v2.csv`) - 5.7MB
- Python cache files (`__pycache__/`) - scattered throughout

## Solution: Upload Only Source Code (Recommended)

### Step 1: Create a Clean Source Code Archive

1. **Create a new folder** for your source code only:
   ```cmd
   mkdir bnpl_simulator_source
   ```

2. **Copy only essential source files** (excluding venv, __pycache__, large data files):
   ```cmd
   # Copy main Python files
   copy bnpl_simulator\*.py bnpl_simulator_source\
   copy run_application.py bnpl_simulator_source\
   copy check_database.py bnpl_simulator_source\
   copy find_*.py bnpl_simulator_source\
   
   # Copy frontend files
   copy frontend\*.py bnpl_simulator_source\
   copy frontend\package.json bnpl_simulator_source\
   copy frontend\requirements.txt bnpl_simulator_source\
   xcopy frontend\src bnpl_simulator_source\src /E /I
   
   # Copy documentation and config
   copy *.md bnpl_simulator_source\
   copy requirements.txt bnpl_simulator_source\
   copy .gitignore bnpl_simulator_source\
   ```

3. **Create a requirements.txt** if it doesn't exist:
   ```cmd
   echo flask> bnpl_simulator_source\requirements.txt
   echo streamlit>> bnpl_simulator_source\requirements.txt
   echo pandas>> bnpl_simulator_source\requirements.txt
   echo numpy>> bnpl_simulator_source\requirements.txt
   echo scikit-learn>> bnpl_simulator_source\requirements.txt
   echo plotly>> bnpl_simulator_source\requirements.txt
   ```

4. **Create a README.md** explaining the project:
   ```cmd
   echo # BNPL Simulator Application> bnpl_simulator_source\README.md
   echo.>> bnpl_simulator_source\README.md
   echo This is a Buy Now Pay Later simulation application.>> bnpl_simulator_source\README.md
   echo.>> bnpl_simulator_source\README.md
   echo ## Installation>> bnpl_simulator_source\README.md
   echo ```>> bnpl_simulator_source\README.md
   echo pip install -r requirements.txt>> bnpl_simulator_source\README.md
   echo ```>> bnpl_simulator_source\README.md
   ```

### Step 2: Upload via GitHub Web Interface

1. **Go to GitHub.com** and log in to your account
2. **Create a new repository**:
   - Click "+" in top right → "New repository"
   - Repository name: `bnpl-simulator`
   - Description: "BNPL Simulation Application"
   - Keep it **Public** (easier to share)
   - **Uncheck** "Add a README file" (we'll add it manually)
   - Click "Create repository"

3. **Upload files manually**:
   - In your new repository, click "Add file" → "Upload files"
   - Drag and drop your `bnpl_simulator_source` folder contents
   - **Important**: Upload files in batches of 25MB or less
   - Add commit message: "Initial commit - source code"
   - Click "Commit changes"

### Step 3: Handle Large Files (Alternative Methods)

#### Option A: Use Git LFS (Large File Storage)
If you need to include large data files:

1. **Install Git LFS** on a personal computer:
   ```bash
   # Download from https://git-lfs.com/
   git lfs install
   git lfs track "*.csv"
   git lfs track "*.db"
   ```

2. **Clone repository** to personal computer:
   ```bash
   git clone https://github.com/yourusername/bnpl-simulator.git
   cd bnpl-simulator
   ```

3. **Add large files**:
   ```bash
   git lfs track "*.csv" "*.db"
   cp path/to/bnpl_dataset_v2.csv .
   cp path/to/bnpl_simulator.db .
   git add .gitattributes
   git add bnpl_dataset_v2.csv bnpl_simulator.db
   git commit -m "Add large data files via LFS"
   git push origin main
   ```

#### Option B: Use GitHub Desktop (No Command Line)
1. Download GitHub Desktop from https://desktop.github.com/
2. Clone your repository
3. Copy files to the local folder
4. Commit and push changes

#### Option C: Use Third-Party Tools
- **SmartGit**: Free Git client with GUI
- **SourceTree**: Atlassian's Git client
- **TortoiseGit**: Windows shell interface for Git

### Step 4: Handle Data Files Separately

Since your data files are large, consider these alternatives:

#### Option A: Google Drive/Dropbox
1. Upload large files to Google Drive or Dropbox
2. Share with "Anyone with link can view"
3. Add download links to your README.md

#### Option B: Kaggle Datasets
1. Create account at kaggle.com
2. Upload your CSV files as a dataset
3. Reference in your README.md

#### Option C: Generate Sample Data
Create a script to generate smaller sample data:
```python
# create_sample_data.py
import pandas as pd
import numpy as np

# Generate smaller sample dataset
data = {
    'user_id': range(1, 1001),
    'age': np.random.randint(18, 65, 1000),
    'income': np.random.randint(20000, 100000, 1000),
    'credit_score': np.random.randint(300, 850, 1000)
}

df = pd.DataFrame(data)
df.to_csv('sample_data.csv', index=False)
print("Sample data created: sample_data.csv")
```

## Complete Manual Upload Steps Summary

### For Source Code Only (Recommended):
1. ✅ Create clean source folder (exclude venv, __pycache__, large files)
2. ✅ Create GitHub repository
3. ✅ Upload files via web interface in batches
4. ✅ Add README.md with installation instructions

### For Including Data Files:
1. ✅ Use personal computer with Git LFS
2. ✅ Or upload data files separately to cloud storage
3. ✅ Reference data files in README.md

## File Size Limits
- **GitHub upload limit**: 25MB per file via web interface
- **Repository size limit**: 1GB (soft limit), 5GB (hard limit)
- **Recommended**: Keep repository under 100MB for best performance

## Essential Files to Include
```
bnpl_simulator/
├── __init__.py
├── affordability_engine.py
├── cache_utils.py
├── comparison_engine.py
├── config.py
├── data_loader.py
├── database.py
├── main.py
├── ml_model.py
├── models.py
└── risk_engine.py

frontend/
├── app.py
├── package.json
├── requirements.txt
└── src/

run_application.py
requirements.txt
README.md
.gitignore
```

## Files to Exclude
- `venv/` folders (virtual environments)
- `__pycache__/` folders (Python cache)
- Large data files (>25MB)
- `.pyc` files (compiled Python)
- IDE configuration files

## Next Steps
1. Follow the source code upload method above
2. Test that your application works with the uploaded code
3. Consider creating a separate repository for data files if needed
4. Document data file sources and generation methods in README.md

This approach will give you a clean, manageable repository that others can easily clone and use.