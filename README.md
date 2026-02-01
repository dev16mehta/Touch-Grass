# 🌿 Touch Grass

Stop doomscrolling, start exploring. Touch Grass transforms your mood into personalized walking routes, guiding you through adventures tailored to your vibe.

## Overview

Touch Grass is a mood-based walking route generator that uses AI to understand how you're feeling and creates real walking routes with actual footpaths, POIs, and turn-by-turn directions. Whether you want a peaceful stroll through parks or a chaotic bar-hopping adventure, we've got you covered.

## Key Features

**🤖 AI Mood Detection**
- Type how you're feeling in natural language
- Gemini AI extracts your vibe and optional location mentions
- 4 unique vibes: Chill, Date, Chaos, Aesthetic

**🗺️ Smart Route Generation**
- Real walking routes using Google Maps Directions API
- Duration-based planning (10-120 minutes)
- Circular routes (return to start) or one-way routes
- Custom destination input for one-way routes
- POI selection based on your vibe (parks, cafes, bars, landmarks)

**📍 Interactive Maps**
- Beautiful map visualization with Mapbox GL
- Directional arrows showing your path
- Place markers with details and ratings
- Auto-fit to route bounds

**🎨 Nature-Themed UI**
- Consistent icon system with Lucide React
- Plant-growth animations for loading states
- Vibe-specific color schemes
- Responsive design for mobile and desktop

## Tech Stack

**Backend**
- Python 3.11 + Flask
- Google Gemini AI (mood detection)
- Google Maps Directions API (real walking routes)
- Google Places API (POI discovery)

**Frontend**
- React + Vite
- Mapbox GL (map visualization)
- Lucide React (icons)
- CSS3 with animations

## Project Structure

```
Touch-Grass/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # API keys (not in git)
│   └── venv/              # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # Styles
│   │   └── index.css      # Global styles
│   ├── .env               # Frontend config (not in git)
│   └── package.json       # Node dependencies
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Google Gemini API key
- Google Maps API key (with Directions & Places APIs enabled)
- Mapbox access token

### Backend Setup

1. **Navigate to backend and create virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file in `backend/` directory:**
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```
   Backend runs on `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend and install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env` file in `frontend/` directory:**
   ```env
   VITE_MAPBOX_TOKEN=your_mapbox_token_here
   VITE_API_URL=http://localhost:5001/api
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

## Usage

1. **Start both servers** (backend and frontend)
2. **Open** `http://localhost:5173` in your browser
3. **Allow location access** when prompted
4. **Describe your mood** in the text box (e.g., "I want to relax in Central Park")
5. **Click "Detect Vibe"** to let AI understand your mood
6. **Set duration** (10-120 minutes) and route type (circular or one-way)
7. **For one-way routes:** optionally specify a destination
8. **Click "Start Exploring"** to generate your route
9. **View your route** on the map with turn-by-turn directions!

## How It Works

1. **Mood Detection**: Gemini AI analyzes your text to determine your vibe and extract any location mentions
2. **Route Calculation**: Based on duration and vibe, we calculate target distance using pace multipliers (chill walks slower, chaos walks faster)
3. **POI Selection**: Google Places API finds relevant spots matching your vibe within the search radius
4. **Route Optimization**: For circular routes, waypoints are positioned at ~120° intervals to create true loops. For one-way routes, we select intermediates between start and destination
5. **Directions**: Google Directions API generates real walking routes with actual footpaths
6. **Visualization**: Mapbox renders the route with directional arrows and place markers

## Project Structure

```
Touch-Grass/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── config.py                 # Vibe configurations
│   ├── services/
│   │   ├── ai_service.py         # Gemini mood detection
│   │   ├── maps_service.py       # Google Maps integration
│   │   ├── place_service.py      # POI filtering
│   │   └── route_service.py      # Route optimization
│   ├── utils/
│   │   └── geo_utils.py          # Distance & angle calculations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main component
│   │   ├── components/           # UI components
│   │   ├── hooks/                # Custom React hooks
│   │   └── services/             # API client
│   └── package.json
└── README.md
```

## Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

## Future Enhancements

- Social features (share routes, see popular routes)
- Route history and favorites
- Weather integration (covered paths when raining)
- Accessibility options (wheelchair-friendly routes)
- Gamification (badges, streaks)
- Multi-day route planning

---

**Built with ❤️ for a hackathon** - Stop doomscrolling, start exploring! 🌿
