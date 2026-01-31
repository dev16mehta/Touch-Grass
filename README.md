# 🌿 Touch Grass - Mood-Based Walking Routes

A web app that generates personalized walking routes based on your mood/vibe using AI and real-time location data.

## Features

- **4 Unique Vibes**:
  - 🌿 Chill - Relaxing walks with parks and quiet spots
  - 💕 Date - Romantic routes with cafes and scenic views
  - 🍻 Chaos - Energetic walks with bars and nightlife
  - 📸 Aesthetic - Instagram-worthy spots and viewpoints

- **AI-Powered Descriptions** using Google Gemini API
- **Interactive Maps** with Mapbox
- **Real-time Location** based route generation
- **Beautiful UI** with responsive design

## Tech Stack

- **Backend**: Python 3.11 + Flask
- **Frontend**: React + Vite + JavaScript
- **APIs**:
  - Google Gemini (AI descriptions)
  - Mapbox (Maps & Places)
- **Styling**: CSS3 with modern gradients

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

## Setup Instructions

### Prerequisites
- Python 3.11
- Node.js 18+ and npm
- Gemini API key
- Mapbox API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (already created with your keys):
```
GEMINI_API_KEY=your_gemini_key
MAPBOX_TOKEN=your_mapbox_token
```

5. Run the Flask server:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (already created):
```
VITE_MAPBOX_TOKEN=your_mapbox_token
VITE_API_URL=http://localhost:5000/api
```

4. Run the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Allow location access when prompted
4. Select your vibe (chill, date, chaos, or aesthetic)
5. Click "Generate Route"
6. Explore your personalized walking route on the map!

## API Endpoints

### GET `/api/health`
Health check endpoint

### GET `/api/vibes`
Returns available vibes with descriptions

### POST `/api/generate-route`
Generate a walking route
```json
{
  "vibe": "chill",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "radius": 2000
}
```

## Development

### Running Backend Tests
```bash
cd backend
source venv/bin/activate
python app.py
```

### Running Frontend in Dev Mode
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
cd frontend
npm run build
```

## Hackathon Notes

This project was built for a hackathon with the following team split:
- Route logic & Backend API
- UI & Map Integration
- Vibe/AI Layer

## Future Enhancements

- [ ] Spotify integration for vibe matching
- [ ] Save favorite routes
- [ ] Share routes with friends
- [ ] Weather-based recommendations
- [ ] Time-of-day optimizations
- [ ] User reviews for places
- [ ] Supabase/DigitalOcean integration

## License

MIT License - Built for hackathon fun!
