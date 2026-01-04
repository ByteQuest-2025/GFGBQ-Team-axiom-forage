"""
ML-Compatible Seed Data Generator

Generates realistic historical hospital data with:
- ICU occupancy correlated with weekends
- Weather severity affecting patient volume
- Realistic seasonal illness weights per month
- Enough data for manual ML testing (90 days)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.hospital import Hospital
from app.models.prediction import Prediction
from app.auth.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_seasonal_weight(month: int) -> float:
    """
    Realistic seasonal illness weight by month.
    High in winter (flu) and monsoon (dengue/malaria).
    """
    seasonal_weights = {
        1: 0.85,   # January - Winter (flu peak)
        2: 0.80,   # February - Winter
        3: 0.45,   # March - Spring transition
        4: 0.30,   # April - Low
        5: 0.35,   # May - Pre-monsoon
        6: 0.50,   # June - Monsoon start
        7: 0.70,   # July - Monsoon peak (dengue)
        8: 0.75,   # August - Monsoon
        9: 0.65,   # September - Monsoon end
        10: 0.45,  # October - Post-monsoon
        11: 0.55,  # November - Winter start
        12: 0.75   # December - Winter (flu)
    }
    return seasonal_weights.get(month, 0.5)


def generate_correlated_data(date: datetime) -> dict:
    """
    Generate ML-compatible daily data with realistic correlations.
    
    Correlations:
    - Weekends → Higher ICU occupancy (+15-25%)
    - High temp → More patients (+10-20%)
    - Heavy rain → More accidents (+20-30%)
    - Seasonal illness → Higher ER load
    """
    is_weekend = 1 if date.weekday() >= 5 else 0
    month = date.month
    
    # Base values
    base_icu_occ = random.uniform(0.55, 0.75)
    base_patients = random.randint(80, 140)
    
    # Weekend correlation
    if is_weekend:
        base_icu_occ += random.uniform(0.10, 0.20)  # +10-20% ICU on weekends
        base_patients += random.randint(15, 30)      # +15-30 patients
    
    # Temperature (realistic for India)
    temp_base = random.randint(20, 42)
    if temp_base > 38:  # Heatwave
        base_patients += random.randint(10, 25)  # Heat-related admissions
    
    # Rainfall (realistic monsoon patterns)
    if month in [6, 7, 8, 9]:  # Monsoon months
        rain_mm = random.choice([0, 5, 15, 35, 60], counts=[30, 25, 20, 15, 10], k=1)[0]
    else:
        rain_mm = random.choice([0, 2, 5], counts=[85, 10, 5], k=1)[0]
    
    if rain_mm > 30:  # Heavy rain → accidents
        base_patients += random.randint(15, 35)
    
    # Seasonal illness weight
    seasonal_weight = get_seasonal_weight(month)
    base_patients = int(base_patients * (1 + seasonal_weight * 0.2))  # +0-20% based on season
    
    # Cap values
    icu_occupancy = min(base_icu_occ, 0.95)
    daily_patients = min(base_patients, 220)
    
    # Generate realistic risk score
    risk_base = icu_occupancy * 0.6
    if rain_mm > 30:
        risk_base += 0.15
    if temp_base > 38:
        risk_base += 0.10
    if is_weekend:
        risk_base += 0.05
    risk_score = min(risk_base, 1.0)
    
    # Derive risk level
    if risk_score > 0.75:
        risk_level = "Critical"
    elif risk_score > 0.50:
        risk_level = "High"
    elif risk_score > 0.30:
        risk_level = "Elevated"
    else:
        risk_level = "Normal"
    
    # Calculate surges and resources
    er_surge = min(risk_score * 0.4, 0.5)
    icu_surge = min(risk_score * 0.25, 0.3)
    
    additional_beds = int(40 * icu_surge)  # 40 = typical ICU capacity
    additional_staff = max(0, int((daily_patients * (1 + er_surge) / 10) - random.randint(8, 14)))
    
    supply_status = "Low" if (er_surge > 0.2 and random.random() > 0.7) else "Stable"
    
    return {
        "date": date.date(),
        "risk_score": round(risk_score, 3),
        "er_surge_pct": round(er_surge, 3),
        "icu_surge_pct": round(icu_surge, 3),
        "risk_level": risk_level,
        "additional_icu_beds": additional_beds,
        "additional_staff": additional_staff,
        "supply_status": supply_status,
        "input_features": {
            "icu_occupancy_pct": round(icu_occupancy, 2),
            "daily_patients": daily_patients,
            "staff_on_duty": random.randint(8, 16),
            "oxygen_low": 1 if random.random() < 0.1 else 0,
            "medicine_low": 1 if random.random() < 0.05 else 0,
            "temp_max": temp_base,
            "rain_mm": rain_mm,
            "weather_severity": 0.8 if rain_mm > 30 else 0.2,
            "is_weekend": is_weekend,
            "is_festival": 1 if random.random() < 0.04 else 0,
            "seasonal_illness_weight": seasonal_weight
        },
        "is_fallback": 0
    }


def seed_database():
    """
    Seed database with:
    1. Test hospital account
    2. 90 days of ML-compatible prediction data
    """
    db = SessionLocal()
    
    try:
        # 1. Create/Update test hospital
        hospital = db.query(Hospital).filter(Hospital.email == "test@hospital.com").first()
        
        if not hospital:
            hospital = Hospital(
                email="test@hospital.com",
                hashed_password=get_password_hash("password123"),
                hospital_name="Test General Hospital",
                location="Mumbai",
                icu_total_capacity=40,
                is_active=True
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)
            logger.info(f"✅ Created test hospital (ID: {hospital.id})")
        else:
            logger.info(f"✅ Test hospital exists (ID: {hospital.id})")
        
        # 2. Clear existing predictions for clean slate
        db.query(Prediction).filter(Prediction.hospital_id == hospital.id).delete()
        db.commit()
        logger.info("🗑️  Cleared old predictions")
        
        # 3. Generate 90 days of realistic data
        logger.info("📊 Generating 90 days of ML-compatible data...")
        
        start_date = datetime.now() - timedelta(days=89)
        
        for day_offset in range(90):
            current_date = start_date + timedelta(days=day_offset)
            data = generate_correlated_data(current_date)
            
            prediction = Prediction(
                hospital_id=hospital.id,
                **data
            )
            db.add(prediction)
            
            if (day_offset + 1) % 30 == 0:
                logger.info(f"  Generated {day_offset + 1} days...")
        
        db.commit()
        logger.info("✅ Generated 90 days of predictions")
        
        # 4. Verification stats
        total_predictions = db.query(Prediction).filter(
            Prediction.hospital_id == hospital.id
        ).count()
        
        critical_count = db.query(Prediction).filter(
            Prediction.hospital_id == hospital.id,
            Prediction.risk_level == "Critical"
        ).count()
        
        weekend_predictions = db.query(Prediction).filter(
            Prediction.hospital_id == hospital.id,
            Prediction.input_features["is_weekend"].astext == "1"
        ).count()
        
        logger.info(f"\n📈 Seed Data Summary:")
        logger.info(f"   Total predictions: {total_predictions}")
        logger.info(f"   Critical risk days: {critical_count}")
        logger.info(f"   Weekend entries: {weekend_predictions}")
        logger.info(f"\n🔐 Test Account:")
        logger.info(f"   Email: test@hospital.com")
        logger.info(f"   Password: password123")
        logger.info(f"\n✅ Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
