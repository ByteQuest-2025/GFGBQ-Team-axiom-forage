# Production Backend Setup Guide

## 🚀 Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create `.env` file in `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: Generate with `openssl rand -hex 32`

### 3. Initialize Database

```bash
# Create tables and seed test account
python scripts/init_db.py

# Test credentials:
# Email: test@hospital.com
# Password: password123
```

### 4. Train ML Model

```bash
python train_and_init.py
```

### 5. Start Server

```bash
uvicorn app.main:app --reload --port 8001
```

### 6. Test API

Visit: http://127.0.0.1:8001/docs (Swagger UI)

**Authentication Flow:**
1. POST `/api/v1/auth/register` or `/api/v1/auth/login`
2. Copy the `access_token` from response
3. Click "Authorize" button in Swagger UI
4. Enter: `Bearer <your_token>`
5. Now you can access protected endpoints like `/api/v1/dashboard`

---

## 🌐 Deploying to Render

### Prerequisites
- Render account
- GitHub repository

### Steps:

1. **Push Code to GitHub**
```bash
git add .
git commit -m "Production backend ready"
git push origin main
```

2. **Create Render Account**
- Go to https://render.com
- Connect your GitHub account

3. **Deploy from Dashboard**
- Click "New +" → "Blueprint"
- Connect repository
- Render will read `render.yaml` automatically

4. **Set Environment Variables**
Render will prompt for:
- `SECRET_KEY` (auto-generated)
- `ALLOWED_ORIGINS` (your frontend URL)

5. **Wait for Deployment**
- Database provisions (~2 min)
- Backend builds and starts (~5 min)

6. **Run Migrations**
After deployment, run once:
```bash
# In Render shell
python scripts/init_db.py
python train_and_init.py
```

7. **Test Production API**
```
https://axiom-forage-backend.onrender.com/
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Update `ALLOWED_ORIGINS` to your frontend domain
- [ ] Use strong passwords for test accounts
- [ ] Enable HTTPS (automatic on Render)
- [ ] Review database security settings

---

## 📊 ML Model Contract

**Input (11 Features):**
1. `icu_occupancy_pct` (float, 0-1)
2. `daily_patients` (int)
3. `staff_on_duty` (int)
4. `oxygen_low` (binary: 0/1)
5. `medicine_low` (binary: 0/1)
6. `temp_max` (float, °C)
7. `rain_mm` (float, mm)
8. `weather_severity` (float, 0-1)
9. `is_weekend` (binary: 0/1)
10. `is_festival` (binary: 0/1)
11. `seasonal_illness_weight` (float, 0-1)

**Output (3 Numeric Values):**
- `risk_score` (0-1)
- `expected_er_increase_pct` (0-1)
- `expected_icu_increase_pct` (0-1)

**Backend Derives:**
- `risk_level`: Critical/High/Elevated/Normal
- `additional_icu_beds`: Integer count
- `additional_staff`: Integer count
- `supply_status`: Low/Stable
- `recommendations`: List of actionable items

---

## 🧪 Testing

```bash
# Run tests
pytest backend/tests/

# Check health
curl http://localhost:8001/

# Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@hospital.com","password":"password123"}'

# Get dashboard (with token)
curl http://localhost:8001/api/v1/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🐛 Troubleshooting

**Database Connection Failed:**
- Check `DATABASE_URL` format
- Ensure PostgreSQL is running
- Verify network access

**ML Model Not Found:**
- Run `python train_and_init.py`
- Check `backend/saved_models/stress_model.pkl` exists

**JWT Token Invalid:**
- Ensure `SECRET_KEY` matches between sessions
- Token expires after 30 minutes (default)

**Import Errors:**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version >= 3.8

---

##  📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── auth.py              # Authentication endpoints
│   ├── auth/
│   │   ├── security.py          # JWT & password utils
│   │   └── dependencies.py      # Auth dependencies
│   ├── models/
│   │   ├── hospital.py          # Hospital model
│   │   ├── prediction.py        # Prediction model
│   │   ├── cached_data.py       # Cache model
│   │   └── emergency_model.py   # ML model wrapper
│   ├── schemas/
│   │   └── auth.py              # Pydantic schemas
│   ├── services/
│   │   ├── forecasting.py       # Prediction logic
│   │   └── cache.py             # Caching service
│   ├── utils/
│   │   └── preprocessing.py     # Data processing
│   ├── database.py              # DB connection
│   └── main.py                  # FastAPI app
├── scripts/
│   └── init_db.py               # DB initialization
├── data/
│   ├── raw/                     # Raw training data
│   └── processed/               # Processed datasets
├── saved_models/
│   └── stress_model.pkl         # Trained ML model
├── requirements.txt             # Python dependencies
├── train_and_init.py            # Model training
└── .env.example                 # Environment template
```

---

## 🔄 Maintenance

**Update Model:**
```bash
# Retrain with new data
python train_and_init.py
```

**Clear Cache:**
```sql
DELETE FROM cached_data WHERE expires_at < NOW();
```

**Backup Database:**
```bash
pg_dump $DATABASE_URL > backup.sql
```

---

## 📞 Support

For issues or questions:
1. Check `/docs` endpoint for API documentation
2. Review logs in Render dashboard
3. Inspect database with `psql $DATABASE_URL`
