# Deployment Guide – PythonAnywhere
# AI-Based Income Stability Score for Gig Workers

## STEP 1: Upload Project Files

1. Login at https://www.pythonanywhere.com
2. Go to Files tab
3. Create folder: /home/<your-username>/gigscore/
4. Upload:
   - backend/app.py
   - models/ (all .pkl files)
   - backend/requirements.txt

## STEP 2: Set Up Virtual Environment

Open a Bash console on PythonAnywhere:

    mkvirtualenv gigscore --python=python3.10
    workon gigscore
    pip install -r /home/<your-username>/gigscore/requirements.txt

## STEP 3: Configure Web App

1. Go to Web tab → Add new web app
2. Choose: Manual Configuration → Python 3.10
3. Set Source code: /home/<your-username>/gigscore/backend
4. Set Working directory: /home/<your-username>/gigscore/backend

In the WSGI configuration file, replace content with:

    import sys
    sys.path.insert(0, '/home/<your-username>/gigscore/backend')
    from app import app as application

5. Set Virtualenv path: /home/<your-username>/.virtualenvs/gigscore
6. Click Reload

## STEP 4: Test the API

Your API will be live at:
    https://<your-username>.pythonanywhere.com/api/health
    https://<your-username>.pythonanywhere.com/api/predict  (POST)

## STEP 5: Deploy React Frontend

Option A – GitHub Pages (Free):
    cd frontend
    npm run build
    npm install -g gh-pages
    # Add to package.json: "homepage": "https://<username>.github.io/gigscore"
    npm run deploy

Option B – Netlify (Free, easiest):
    1. Go to netlify.com → Import from Git
    2. Build command: npm run build
    3. Publish directory: build
    4. Set env variable: REACT_APP_API_URL = https://<username>.pythonanywhere.com

## STEP 6: Connect Frontend to Backend

In frontend/.env file:
    REACT_APP_API_URL=https://<your-username>.pythonanywhere.com

Rebuild React app after updating .env.

## NOTES:
- Free PythonAnywhere allows 1 web app + 512 MB storage
- The API is accessible from anywhere after deployment
- PythonAnywhere restarts your app daily (free tier)
- For always-on, upgrade to a paid plan (~$5/month)
