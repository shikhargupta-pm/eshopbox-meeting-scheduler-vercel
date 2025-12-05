# 🚀 Eshopbox Meeting Scheduler - Vercel Optimized

## Architecture

This version is specifically optimized for Vercel deployment with proper database support.

### Tech Stack

- **Backend**: Flask (Python 3.9+)
- **Database**: PostgreSQL (Vercel Postgres for production, SQLite for local testing)
- **Deployment**: Vercel Serverless Functions
- **Environment**: Python runtime on Vercel

### Key Features

1. **Dual Database Support**:
   - PostgreSQL for Vercel (persistent, multi-user)
   - SQLite fallback for local development
   - Automatic detection based on environment

2. **Serverless Optimized**:
   - Proper WSGI configuration
   - Environment variable management
   - Stateless function design

3. **Multi-User Ready**:
   - Central database for all users
   - Round-robin assignment tracking
   - Booking history persistence

## Local Development Setup

### 1. Install Dependencies

```bash
cd "Meeting Scheduler - Vercel"
pip install -r requirements.txt
```

### 2. Set Up Environment

Create `.env` file:
```env
# For local development (SQLite)
ENVIRONMENT=development

# For Vercel (PostgreSQL) - you'll get these from Vercel
# DATABASE_URL=postgres://...
```

### 3. Run Locally

```bash
python app.py
```

Visit: `http://localhost:5000`

## Vercel Deployment

### 1. Create Vercel Postgres Database

1. Go to https://vercel.com/dashboard
2. Storage → Create Database → Postgres
3. Copy the connection string
4. Add as environment variable `DATABASE_URL`

### 2. Deploy

```bash
# Push to GitHub
# Import to Vercel
# Framework: Other
# Deploy!
```

## Database Schema

### Tables

**bookings**
- Stores all confirmed meetings
- Fields: id, ae_name, ae_email, booking_date, time_slot, volume, service, team, created_at

**assignment_counts**
- Tracks round-robin state
- Fields: ae_name, team, assignment_count

## Features

✅ Smart expert routing (LST/FST teams)
✅ Volume-based assignment (< 3000 = LST, ≥ 3000 = FST)
✅ Round-robin distribution
✅ Database persistence
✅ Multi-user support
✅ Booking confirmation workflow
✅ Google Calendar integration

## File Structure

```
Meeting Scheduler - Vercel/
├── api/
│   └── index.py          # Vercel serverless entry point
├── app.py                # Flask application (local + Vercel)
├── database.py           # Database abstraction layer
├── templates/
│   └── index.html        # Frontend
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── .env                 # Environment variables (local)
└── README.md            # This file
```

## Environment Variables

### Local Development
- `ENVIRONMENT=development` (uses SQLite)

### Vercel Production
- `DATABASE_URL` (PostgreSQL connection string from Vercel)

## Testing

### Test Locally
1. Run `python app.py`
2. Test all features
3. Verify database persistence

### Test on Vercel
1. Deploy to Vercel
2. Check serverless function logs
3. Verify multi-user access

## License

Copyright © 2025 Eshopbox Ecommerce Private Limited. All Rights Reserved.
