# 🚀 Cloudflare Worker Setup Guide

This guide will help you set up the secure voting backend for the Lunch Map.

## Step 1: Create Cloudflare Account & Worker (5 mins)

1. Go to [workers.cloudflare.com](https://workers.cloudflare.com)
2. Sign up (free - no credit card required)
3. Click **"Create a Service"** → name it `lunch-votes`
4. Click **"Quick Edit"**
5. Delete all the default code
6. Copy and paste the contents of `cloudflare-worker.js` from this repo
7. Click **"Save and Deploy"**
8. Copy your worker URL (e.g., `https://lunch-votes.yourname.workers.dev`)

## Step 2: Add Your GitHub Token (2 mins)

1. **Create a GitHub Personal Access Token:**
   - Go to [github.com/settings/tokens](https://github.com/settings/tokens)
   - Click **"Generate new token (classic)"**
   - Give it a name like `lunch-votes`
   - Select the `repo` scope (full control of private repositories)
   - Click **"Generate token"**
   - Copy the token (starts with `ghp_`)

2. **Add the token to Cloudflare:**
   - In Cloudflare dashboard, go to your worker → **Settings** → **Variables**
   - Click **"Add Variable"**
   - Name: `GITHUB_TOKEN`
   - Value: `ghp_yourActualToken`
   - Click **"Encrypt"** ⚠️ (important for security!)
   - Click **"Save"**

## Step 3: Update the HTML Files

Replace the placeholder URL in both files with your actual worker URL:

### In `lunch_map.html` (~line 690):
```javascript
const WORKER_URL = 'https://lunch-votes.yourname.workers.dev';
```

### In `ranking.html` (~line 413):
```javascript
const WORKER_URL = 'https://lunch-votes.yourname.workers.dev';
```

## Step 4: Deploy

1. Commit and push your changes to GitHub
2. Wait for GitHub Pages to update (~1 min)
3. Test by voting on the map!

---

## ✅ Done!

Your voting system is now secure:
- ✅ GitHub token is stored on Cloudflare's servers (encrypted)
- ✅ Token is never exposed in client-side code
- ✅ Users just enter their name and vote
- ✅ Votes are saved directly to `votes.json` in the repo

---

## Troubleshooting

### "Failed to save vote" error
- Check that your GitHub token has `repo` scope
- Verify the token is correctly added to Cloudflare Variables
- Make sure the token is not expired

### CORS errors
- The worker is configured to allow requests from `https://nsushant.github.io`
- If testing locally, `localhost:5500` and `127.0.0.1:5500` are also allowed

### Votes not showing
- GitHub Pages can take 1-2 minutes to update after a vote
- Try hard-refreshing the page (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

---

## Free Tier Limits

Cloudflare Workers free tier includes:
- **100,000 requests/day** - more than enough for a lunch voting app!
- No credit card required
