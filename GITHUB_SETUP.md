# 📦 GitHub Repository Setup Instructions

## Step 1: Create Private GitHub Repository

Since the GitHub token doesn't have repo creation permissions, please create the repository manually:

### Option A: Via GitHub Website
1. Go to: https://github.com/new
2. Repository name: `whatsapp-automation`
3. Select: **Private**
4. Don't initialize with README
5. Click "Create repository"

### Option B: Via GitHub CLI
```bash
gh repo create whatsapp-automation --private
```

---

## Step 2: Push Code to GitHub

Once you create the repository, run these commands:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-automation.git

# Push to GitHub
git push -u origin master
```

Or if you want to use the token directly:
```bash
git remote set-url origin https://${GITHUB_TOKEN}@github.com/YOUR_USERNAME/whatsapp-automation.git
git push -u origin master
```

---

## Step 3: Verify Repository

1. Go to your GitHub profile
2. Find `whatsapp-automation` repository
3. It should be **Private** (🔒 icon)
4. All files should be visible

---

## Step 4: Add as OpenHands Skill

Once the repository is created, you can add it as a skill using:

```
/add-skill https://github.com/YOUR_USERNAME/whatsapp-automation
```

Or add it manually to `.agents/skills/whatsapp-automation/`

---

## 📥 Alternative: Download as ZIP

You can download the entire project as a ZIP file:
1. Go to your GitHub repository
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract and use

---

## 🔄 Updating Your Repository

After making changes locally:
```bash
git add .
git commit -m "Your update message"
git push origin master
```

---

## 🚀 Share Your Work

Want to make it public later? You can change visibility in:
Repository Settings → Danger Zone → Change visibility

---

**Need Help?**
- GitHub Docs: https://docs.github.com
- GitHub CLI: https://cli.github.com
