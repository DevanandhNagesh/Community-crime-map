# Real-Time Community Crime Alert & Safety Map

## Features

- Register/Login
- Report incidents (with map, media)
- Live map of incidents
- Community chat
- SOS button
- Admin panel for verification

## Local Setup

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```
   pip install -r backend/requirements.txt
   ```
3. **Run the app:**
   ```
   cd backend
   python app.py
   ```
4. **Open your browser:**  
   Go to [http://127.0.0.1:10000](http://127.0.0.1:10000)

- **Admin login:**  
  Email: `admin@admin.com`  
  Password: `admin123`

## Deploy to Render.com

1. Push your code to GitHub.
2. Go to [https://dashboard.render.com/](https://dashboard.render.com/), create a free account.
3. Click **"New Web Service"** → **"Connect your GitHub repo"**.
4. Select your repo, set root directory to `/backend` if needed.
5. Render will auto-detect Flask and deploy.
6. After a few minutes, you’ll get a public URL like `https://crime-alert-app.onrender.com`.

## Notes

- Media uploads are stored in `backend/static/uploads/`
- For real SMS/email in SOS, integrate with Twilio/SMTP in `app.py`
- For production, use a real database and secure secret keys