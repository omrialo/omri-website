# Omri's Website

A simple, modern website developed with Flask and AI assistance.

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python app.py
```

5. Visit `http://localhost:5000` in your browser

## Deployment Options

### Option 1: GitHub Pages (Free)
1. Create a new repository on GitHub
2. Push your code to the repository
3. Go to repository Settings > Pages
4. Select the main branch as the source
5. Your site will be available at `https://[your-username].github.io/[repository-name]`

### Option 2: Render (Free tier available)
1. Create an account on [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy!

### Option 3: Heroku (Free tier discontinued, but still popular)
1. Create an account on [Heroku](https://heroku.com)
2. Install the Heroku CLI
3. Run:
```bash
heroku create
git push heroku main
```

## Technologies Used
- Python
- Flask
- HTML/CSS
- Gunicorn (for production deployment) 