# 🚀 Deployment Guide: Eshopbox Meeting Scheduler on Vercel

This guide will walk you through deploying your fully optimized Flask application with a persistent database on Vercel.

---

## 📋 Prerequisites

1.  **GitHub Account**: To host your code.
2.  **Vercel Account**: To deploy the application (linked to your GitHub).

---

## 🛠️ Step 1: Upload to GitHub

1.  **Open GitHub Desktop** (or use the command line).
2.  **Create a New Repository**:
    *   Name it `eshopbox-scheduler-production` (or similar).
    *   **Important**: Do not upload the entire desktop; only upload the contents of the `Meeting Scheduler - Vercel` folder.
3.  **Add Files**:
    *   Drag and drop all files from your `Meeting Scheduler - Vercel` folder into this new repository.
    *   *Ensure `api/`, `static/`, `templates/`, `app.py`, `database.py`, `requirements.txt`, and `vercel.json` are present.*
4.  **Commit and Push**:
    *   Message: "Initial commit for Vercel deployment".
    *   Publish the repository.

---

## 🗄️ Step 2: Create a Database on Vercel

Since serverless functions don't save files locally, we need a database service. Vercel provides one for free.

1.  Log in to your **Vercel Dashboard**.
2.  Click on the **Storage** tab (top menu).
3.  Click **Create Database**.
4.  Select **Postgres** (Vercel Postgres).
5.  Give it a name (e.g., `eshopbox-db`) and a region (e.g., `Mumbai` or `Singapore` for speed).
6.  Click **Create**.
7.  Once created, look for the **".env.local"** tab or **"Connection Strings"** section.
8.  **Copy** the standard connection string. It looks like:
    `postgres://default:password@ep-url.region.postgres.vercel-storage.com:5432/verceldb`
    *Keep this safe, you will need it in Step 4.*

---

## ☁️ Step 3: Import Project to Vercel

1.  Go to the **Vercel Dashboard** (Overview).
2.  Click **Add New...** > **Project**.
3.  **Import Git Repository**: Find the `eshopbox-scheduler-production` repo you just created and click **Import**.

---

## ⚙️ Step 4: Configure Project & Deploy

1.  **Framework Preset**: Select **Other**.
    *   *Note: Vercel might auto-detect Python/Flask, but "Other" is safe if we use our own `vercel.json`.*
2.  **Root Directory**: Leave as `./`.
3.  **Environment Variables**:
    *   Expand the "Environment Variables" section.
    *   **Key**: `DATABASE_URL`
    *   **Value**: Paste the connection string you copied in Step 2.
    *   *Note: This variable tells your code to switch from SQLite (local) to Postgres (production).*
4.  **Deploy**:
    *   Click **Deploy**.

---

## ✅ Step 5: Verification

1.  Wait for the deployment to finish (1-2 minutes).
2.  Click on the **Domain** link provided by Vercel (e.g., `https://eshopbox-scheduler.vercel.app`).
3.  **test it**:
    *   The first load might take a few seconds (cold start).
    *   Submit a test booking.
    *   **Check the logs**: Go to Vercel Dashboard > Project > Logs. You should see "✅ Database initialized successfully (PostgreSQL)".

---

## 🔄 Updates & Maintenance

*   To update the code, simply modify files in your local `Meeting Scheduler - Vercel` folder, commit, and push to GitHub. Vercel will **automatically redeploy**.
*   Your database data is safe and persistent, unaffected by new deployments.
