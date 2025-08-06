# 🚀 Git Workflow - Safe Development & Deployment

## 🛡️ **Waarom deze workflow?**

Nu je een werkende automatische deployment hebt, is het cruciaal om **master branch** altijd stabiel te houden. Deze workflow voorkomt dat je per ongeluk broken code naar production pusht.

## 🌿 **Branch Structure**

```
master (production)
├── develop (testing/staging)
│   ├── feature/new-feature
│   ├── feature/bug-fix
│   └── feature/documentation
```

### **Branches:**
- **`master`** → Production (auto-deploy naar server)
- **`develop`** → Testing/Staging (veilige testing)
- **`feature/*`** → Individuele features/bugfixes

## 📋 **Workflow Commands**

### **Quick Aliases (beschikbaar na `source ~/.bashrc`):**

```bash
# Check status
gitstatus

# Create feature branch
gitfeature <feature-name>

# Merge to develop
gitmerge

# Safe deploy to production
gitdeploy

# Show all commands
gitflow help
```

### **Full Commands:**

```bash
# Check current status
python3 scripts/git_workflow.py status

# Create feature branch
python3 scripts/git_workflow.py feature <name>

# Merge current branch to develop
python3 scripts/git_workflow.py merge-develop

# Safe deploy to master (with confirmation)
python3 scripts/git_workflow.py deploy
```

## 🚀 **Typische Workflow**

### **1. Nieuwe Feature Ontwikkelen**

```bash
# 1. Check status
gitstatus

# 2. Create feature branch
gitfeature new-chat-feature

# 3. Make changes and commit
git add .
git commit -m "Add new chat feature"

# 4. Merge to develop for testing
gitmerge

# 5. Test on develop branch
# ... test your changes ...

# 6. When ready, deploy to production
gitdeploy
```

### **2. Bug Fix**

```bash
# 1. Create bug fix branch
gitfeature fix-login-issue

# 2. Fix the bug and commit
git add .
git commit -m "Fix login authentication issue"

# 3. Merge to develop
gitmerge

# 4. Test the fix
# ... test thoroughly ...

# 5. Deploy to production
gitdeploy
```

## 🛡️ **Safety Features**

### **Safe Deploy (`gitdeploy`)**
- ✅ Checks if you're on master branch
- ✅ Checks for uncommitted changes
- ✅ Checks if local is behind remote
- ✅ Asks for confirmation before pushing
- ⚠️ Warns that this will trigger production deployment

### **Status Check (`gitstatus`)**
- 📍 Shows current branch
- 📝 Shows uncommitted changes
- ✅ Confirms working directory is clean

### **Feature Branch Creation (`gitfeature`)**
- 🌿 Automatically switches to develop first
- 🚀 Creates properly named feature branch
- ✅ Checks out the new branch

## ⚠️ **Wat NOOIT te doen**

### ❌ **Direct naar master committen**
```bash
# DON'T DO THIS:
git checkout master
git add .
git commit -m "quick fix"
git push origin master  # This breaks production!
```

### ❌ **Uncommitted changes naar master pushen**
```bash
# DON'T DO THIS:
git checkout master
git add .
git push origin master  # Uncommitted changes!
```

### ❌ **Feature branches direct naar master mergen**
```bash
# DON'T DO THIS:
git checkout master
git merge feature/my-feature  # Skip testing!
```

## ✅ **Wat WEL te doen**

### ✅ **Altijd via develop testen**
```bash
# DO THIS:
gitfeature my-feature
# ... make changes ...
gitmerge  # Test on develop first
gitdeploy  # Only when tested
```

### ✅ **Descriptive commit messages**
```bash
# DO THIS:
git commit -m "Add WhatsApp message encryption"
git commit -m "Fix user authentication timeout"
git commit -m "Update API documentation"
```

### ✅ **Kleine, gefocuste changes**
```bash
# DO THIS:
gitfeature small-fix
# Make one small change
git commit -m "Fix typo in error message"
gitmerge
```

## 🔄 **Emergency Procedures**

### **Hotfix (als master broken is)**
```bash
# 1. Create hotfix branch from master
git checkout master
git checkout -b hotfix/critical-fix

# 2. Fix the issue
# ... make minimal fix ...

# 3. Test locally
python3 tests/run_tests.py

# 4. Deploy immediately
git checkout master
git merge hotfix/critical-fix
git push origin master

# 5. Clean up
git branch -d hotfix/critical-fix
```

### **Rollback (als deployment failed)**
```bash
# 1. Check previous commit
git log --oneline -5

# 2. Revert to previous working commit
git revert HEAD
git push origin master
```

## 📊 **Monitoring**

### **Check Deployment Status**
```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs --tail=20

# Check GitHub Actions
# Go to: GitHub → Actions tab
```

### **Check Branch Status**
```bash
# See all branches
git branch -a

# See branch differences
git log --oneline --graph --all
```

## 🎯 **Best Practices**

1. **Test altijd op develop** voordat je naar master pusht
2. **Gebruik descriptive branch names**: `feature/user-authentication`, `fix/login-bug`
3. **Commit vaak** met duidelijke messages
4. **Keep branches small** - één feature per branch
5. **Delete feature branches** na succesvolle merge
6. **Monitor deployments** via GitHub Actions
7. **Backup belangrijke data** voordat grote changes

## 🚨 **Troubleshooting**

### **Merge Conflicts**
```bash
# 1. Resolve conflicts in your editor
# 2. Add resolved files
git add .

# 3. Complete merge
git commit -m "Resolve merge conflicts"
```

### **Wrong Branch**
```bash
# If you accidentally committed to master:
git reset --soft HEAD~1  # Undo last commit
git stash  # Save changes
git checkout develop
git stash pop  # Apply changes to develop
```

### **Deployment Failed**
```bash
# 1. Check GitHub Actions logs
# 2. Check server logs
docker-compose logs

# 3. Fix the issue and redeploy
gitdeploy
```

---

**💡 Remember: Master branch = Production = Always working!** 