# 🚀 Quick Start Guide

## Starting the Application

### Terminal 1 - Backend (Flask API)

```bash
cd backend
source venv/bin/activate
python app.py
```

Or use the run script:
```bash
cd backend
./run.sh
```

Backend will be available at: `http://localhost:5001`

### Terminal 2 - Frontend (React)

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Test the Backend API

Health check:
```bash
curl http://localhost:5001/api/health
```

Get vibes:
```bash
curl http://localhost:5001/api/vibes
```

Generate a route:
```bash
curl -X POST http://localhost:5001/api/generate-route \
  -H "Content-Type: application/json" \
  -d '{"vibe":"chill","latitude":37.7749,"longitude":-122.4194,"radius":2000}'
```

## Usage Flow

1. Open browser to `http://localhost:5173`
2. Allow location access when prompted (or it will default to San Francisco)
3. Select a vibe:
   - 🌿 **Chill** - Parks and quiet spots
   - 💕 **Date** - Romantic cafes and views
   - 🍻 **Chaos** - Bars and nightlife
   - 📸 **Aesthetic** - Instagram-worthy locations
4. Click "Generate Route"
5. View your personalized route on the map!
6. Click on markers to see place details

## Troubleshooting

### Port 5000 Already in Use
- We're using port 5001 to avoid conflicts with macOS AirTunes
- If you need to change ports, update:
  - `backend/app.py` (last line)
  - `frontend/.env` (`VITE_API_URL`)

### Virtual Environment Not Activated
Make sure to run `source venv/bin/activate` before running the Flask app

### Location Not Working
- Check browser permissions for location access
- Default location (San Francisco) will be used if geolocation fails

### Gemini API Errors
- Check that your API key is correct in `backend/.env`
- The app will use fallback descriptions if Gemini is unavailable

## API Configuration

All API keys are stored in `.env` files (not committed to git):

### Backend `.env`
```
GEMINI_API_KEY=your_key_here
MAPBOX_TOKEN=your_token_here
```

### Frontend `.env`
```
VITE_MAPBOX_TOKEN=your_token_here
VITE_API_URL=http://localhost:5001/api
```

## Project Status

✅ Backend API running on port 5001
✅ Frontend UI complete with React + Vite
✅ Mapbox integration for maps
✅ Gemini AI integration
✅ All 4 vibes implemented
✅ Route generation working
✅ Responsive design

## Next Steps for Hackathon

- [ ] Add more place types (landmarks, viewpoints)
- [ ] Improve Gemini prompts for better descriptions
- [ ] Add route distance/time estimates
- [ ] Implement route sharing
- [ ] Add user preferences (avoid hills, prefer shade, etc.)
- [ ] Integrate Spotify for vibe-based playlists
- [ ] Deploy to production

## Demo Script

1. "Hey everyone, this is Touch Grass - it generates walking routes based on your mood"
2. "Let's say I just finished an exam and want a chaos walk"
3. *Select chaos vibe*
4. *Click generate*
5. "The app finds nearby bars, pubs, and entertainment spots"
6. "It uses AI to create a fun description"
7. "And maps out a route that brings me back to my starting point"
8. *Show different vibes* - "Each vibe has different place types and colors"

Good luck with your hackathon! 🎉
