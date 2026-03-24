# Git Installation Guide for Restricted Company Laptops

## Can You Install Git on a Restricted Laptop?

**Short Answer**: It depends on your company's IT policies, but there are several workarounds you can try.

## Method 1: Portable Git (No Installation Required)

### Download Portable Git
1. **Download PortableGit** from https://github.com/git-for-windows/git/releases/
   - Look for files named `PortableGit-*-32-bit.7z.exe` or `PortableGit-*-64-bit.7z.exe`
   - Example: `PortableGit-2.44.0-64-bit.7z.exe`

2. **Extract to a user-accessible location**:
   ```cmd
   # Extract to your Documents folder
   # No admin rights needed
   ```

3. **Use Git directly**:
   ```cmd
   # Navigate to the extracted folder
   cd C:\Users\YourName\Documents\PortableGit\bin
   
   # Use git commands
   git --version
   git clone https://github.com/username/repository.git
   ```

4. **Add to PATH temporarily** (optional):
   ```cmd
   # Add to current session only
   set PATH=C:\Users\YourName\Documents\PortableGit\bin;%PATH%
   ```

## Method 2: Git via Python (No Installation)

### Use GitPython Library
```python
# Install GitPython (if pip works)
pip install GitPython

# Create a Python script to handle Git operations
import git
import os

# Clone a repository
repo = git.Repo.clone_from('https://github.com/username/repository.git', 'local_folder')

# Make changes and commit
repo.git.add('.')
repo.index.commit('Your commit message')
origin = repo.remote(name='origin')
origin.push()
```

## Method 3: Alternative Git Clients

### GitHub Desktop (May Work)
- Download from https://desktop.github.com/
- Sometimes bypasses restrictions
- GUI-based, easier to use

### SourceTree
- Download from https://www.sourcetreeapp.com/
- Atlassian's free Git client
- May have different permission requirements

### SmartGit
- Download from https://www.syntevo.com/smartgit/
- Free for non-commercial use
- Often works where standard Git fails

## Method 4: Command Line Workarounds

### Use Windows Subsystem for Linux (WSL)
If WSL is available:
```bash
# Install Git in WSL
sudo apt update
sudo apt install git

# Use Git from WSL
git clone https://github.com/username/repository.git
```

### Use PowerShell with Alternative Methods
```powershell
# Download files using PowerShell
Invoke-WebRequest -Uri "https://github.com/username/repository/archive/main.zip" -OutFile "repo.zip"

# Extract and work with files
Expand-Archive -Path "repo.zip" -DestinationPath "."
```

## Method 5: Browser-Based Solutions

### GitHub Web Interface
- Use GitHub's web interface for basic operations
- Upload files directly through browser
- Limited functionality but no installation needed

### GitHub Codespaces
- Cloud-based development environment
- Access through browser
- Full Git functionality available

## Method 6: IT Department Approaches

### Request Temporary Access
1. **Submit a ticket** to IT department
2. **Explain your need** for Git (development, collaboration)
3. **Request temporary installation** or portable version approval
4. **Offer to follow security guidelines**

### Request Proxy Configuration
If Git is blocked by firewall:
1. Ask IT for proxy settings
2. Configure Git to use proxy:
   ```bash
   git config --global http.proxy http://proxy.company.com:8080
   git config --global https.proxy https://proxy.company.com:8080
   ```

## Method 7: Alternative Version Control

### Use Other Platforms
- **Bitbucket**: Alternative to GitHub
- **GitLab**: Self-hosted or cloud options
- **Azure DevOps**: Microsoft's solution

### Use Cloud Storage with Manual Versioning
- **Google Drive/Dropbox**: Manual file versioning
- **OneDrive**: Built into Windows
- **SharePoint**: Corporate solution

## Troubleshooting Common Issues

### Issue: "Access Denied" Errors
**Solutions**:
- Use user directories (Documents, Desktop)
- Try portable applications
- Request elevated permissions

### Issue: "Command Not Found"
**Solutions**:
- Use full paths to executables
- Add to PATH temporarily
- Use batch files/scripts

### Issue: Firewall/Proxy Blocking
**Solutions**:
- Configure proxy settings
- Use HTTPS instead of SSH
- Request firewall exceptions

### Issue: Antivirus Blocking
**Solutions**:
- Add exceptions to antivirus
- Use whitelisted applications
- Contact IT for approval

## Recommended Approach for Your Situation

Given your BNPL simulator project:

1. **Try PortableGit first** - No installation required
2. **Use GitHub Desktop** - GUI-based, may bypass restrictions
3. **Fallback to manual upload** - Use the guide I provided earlier
4. **Request IT assistance** - Explain your development needs

## Quick Test Script

Create a file called `test_git_access.py`:
```python
import subprocess
import os

def test_git_access():
    methods = [
        ['git', '--version'],
        ['C:\\Program Files\\Git\\bin\\git.exe', '--version'],
        ['where', 'git'],
        ['which', 'git']
    ]
    
    for method in methods:
        try:
            result = subprocess.run(method, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"SUCCESS: {method[0]} works")
                print(f"Output: {result.stdout}")
                return True
        except:
            print(f"FAILED: {method[0]}")
    
    print("No Git installation found. Try portable version or manual upload.")
    return False

if __name__ == "__main__":
    test_git_access()
```

Run it to check what Git options are available on your system.

## Final Recommendation

For immediate needs with your BNPL simulator:
1. **Use the manual upload method** I provided earlier
2. **Try PortableGit** for future Git operations
3. **Request IT support** for permanent solution

This gives you both immediate results and long-term Git access options.