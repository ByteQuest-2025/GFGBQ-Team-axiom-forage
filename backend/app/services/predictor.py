"""
Pure ML Inference Service - No Business Logic.

CRITICAL SEPARATION:
- ML model returns ONLY numeric predictions
- No risk levels, no resource counts, no recommendations
- Backend (decision_logic.py) derives everything else

Flow:
  features → ML model → {risk_score, er_increase_pct, icu_increase_pct}
"""

import pandas as pd
import logging
from typing import Dict

from app.models.emergency_model import EmergencyModel

logger = logging.getLogger(__name__)


class PredictorService:
    """
    Pure ML inference service.
    Input: 11-feature DataFrame
    Output: 3 numeric predictions only
    """
    
    def __init__(self, global_model: EmergencyModel = None):
        """
        Initialize with globally loaded ML model.
        
        Args:
            global_model: ML model loaded at startup (or None if unavailable)
        """
        self.model = global_model
        
        if self.model is None:
            logger.warning("⚠️  PredictorService initialized without ML model")
    
    def predict(self, feature_df: pd.DataFrame) -> Dict[str, float]:
        """
        Pure ML inference - returns ONLY numbers.
        
        Args:
            feature_df: DataFrame with exactly 11 features in correct order
            
        Returns:
            Dictionary with 3 numeric predictions:
            {
                "risk_score": float (0.0-1.0),
                "expected_er_increase_pct": float (0.0-1.0),
                "expected_icu_increase_pct": float (0.0-1.0),
                "is_fallback": bool
            }
        """
        if self.model is None:
            # Model unavailable - use conservative rule-based fallback
            logger.warning("⚠️  ML model unavailable, using rule-based fallback")
            return self._rule_based_fallback(feature_df)
        
        try:
            # Pure ML prediction
            predictions = self.model.predict(feature_df)
            logger.info(f"✅ ML Prediction: risk={predictions['risk_score']:.3f}")
            return predictions
            
        except Exception as e:
            # ML failed - use fallback
            logger.error(f"❌ ML prediction error: {e}. Using fallback.")
            return self._rule_based_fallback(feature_df)
    
    def _rule_based_fallback(self, feature_df: pd.DataFrame) -> Dict[str, float]:
        """
        Conservative rule-based predictions when ML unavailable.
        Based on key indicators: ICU occupancy, supply status, weekend.
        
        Args:
            feature_df: Feature DataFrame
            
        Returns:
            Fallback predictions matching ML output format
        """
        # Extract key indicators
        icu_occ = feature_df["icu_occupancy_pct"].iloc[0]
        oxygen_low = feature_df["oxygen_low"].iloc[0]
        medicine_low = feature_df["medicine_low"].iloc[0]
        is_weekend = feature_df["is_weekend"].iloc[0]
        
        # Conservative rule-based risk scoring
        base_risk = icu_occ * 0.6  # Primary: ICU occupancy
        
        if oxygen_low or medicine_low:
            base_risk += 0.2  # Supply shortage penalty
        
        if is_weekend:
            base_risk += 0.1  # Weekend staffing concern
        
        risk_score = min(base_risk, 1.0)  # Cap at 1.0
        
        # Conservative surge predictions
        er_surge = 0.15 if risk_score > 0.5 else 0.10
        icu_surge = 0.10 if risk_score > 0.5 else 0.05
        
        logger.warning(
            f"⚠️  Rule-based fallback: risk={risk_score:.2f}, "
            f"er={er_surge:.2f}, icu={icu_surge:.2f}"
        )
        
        return {
            "risk_score": round(risk_score, 3),
            "expected_er_increase_pct": round(er_surge, 3),
            "expected_icu_increase_pct": round(icu_surge, 3),
            "is_fallback": True
        }
