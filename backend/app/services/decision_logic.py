"""
Backend Decision Logic - Derives Everything from ML Predictions.

CRITICAL: ML model returns ONLY numbers.
This module derives:
- risk_level (Critical/High/Elevated/Normal)
- additional_icu_beds (integer count)
- additional_staff (integer count)
- supply_status (Low/Stable)

Formulas:
- additional_icu_beds = ceil(total_icu_beds × expected_icu_increase_pct)
- additional_staff = ceil((daily_patients × (1 + expected_er_increase_pct)) / patients_per_staff) - current_staff
- supply_status = "Low" if (surge > 20% AND oxygen/medicine low) else "Stable"
"""

import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Constants
PATIENTS_PER_STAFF = 10  # Clinical standard: 1 staff per 10 patients


class DecisionLogic:
    """
    Backend business logic that derives decisions from ML predictions.
    """
    
    @staticmethod
    def classify_risk_level(risk_score: float) -> str:
        """
        Derive risk level from numeric risk score.
        
        Args:
            risk_score: ML-predicted risk score (0.0-1.0)
            
        Returns:
            Risk level: "Critical", "High", "Elevated", or "Normal"
        """
        if risk_score > 0.75:
            return "Critical"
        elif risk_score > 0.50:
            return "High"
        elif risk_score > 0.30:
            return "Elevated"
        else:
            return "Normal"
    
    @staticmethod
    def calculate_additional_beds(
        total_icu_beds: int,
        expected_icu_increase_pct: float
    ) -> int:
        """
        Calculate additional ICU beds needed.
        
        Formula: ceil(total_icu_beds × expected_icu_increase_pct)
        
        Args:
            total_icu_beds: Total ICU capacity
            expected_icu_increase_pct: ML-predicted ICU surge (0.0-1.0)
            
        Returns:
            Integer count of additional beds to prepare
        """
        additional = np.ceil(total_icu_beds * expected_icu_increase_pct)
        return int(max(0, additional))
    
    @staticmethod
    def calculate_additional_staff(
        daily_patients: int,
        current_staff: int,
        expected_er_increase_pct: float,
        patients_per_staff: int = PATIENTS_PER_STAFF
    ) -> int:
        """
        Calculate additional staff needed.
        
        Formula:
          total_expected_patients = daily_patients × (1 + expected_er_increase_pct)
          ideal_staff = ceil(total_expected_patients / patients_per_staff)
          additional_staff = ideal_staff - current_staff
        
        Args:
            daily_patients: Current daily patient count
            current_staff: Current staff on duty
            expected_er_increase_pct: ML-predicted ER surge (0.0-1.0)
            patients_per_staff: Staff-to-patient ratio (default: 10)
            
        Returns:
            Integer count of additional staff to summon
        """
        total_expected = daily_patients * (1 + expected_er_increase_pct)
        ideal_staff = np.ceil(total_expected / patients_per_staff)
        additional = ideal_staff - current_staff
        
        return int(max(0, additional))
    
    @staticmethod
    def determine_supply_status(
        expected_er_increase_pct: float,
        oxygen_status: str,
        medicine_status: str
    ) -> str:
        """
        Determine supply chain alert status.
        
        Logic:
          - If surge > 20% AND (oxygen OR medicine low) → "Low"
          - Otherwise → "Stable"
        
        Args:
            expected_er_increase_pct: ML-predicted ER surge
            oxygen_status: "low" or "normal"
            medicine_status: "low" or "normal"
            
        Returns:
            "Low" or "Stable"
        """
        high_surge = expected_er_increase_pct > 0.2
        supply_shortage = (oxygen_status == "low" or medicine_status == "low")
        
        if high_surge and supply_shortage:
            return "Low"
        else:
            return "Stable"
    
    @staticmethod
    def derive_all_decisions(
        ml_predictions: Dict[str, float],
        hospital_data: Dict
    ) -> Dict:
        """
        Master function: Derive all backend decisions from ML predictions.
        
        Args:
            ml_predictions: {risk_score, expected_er_increase_pct, expected_icu_increase_pct}
            hospital_data: {icu_total, daily_patients, staff_on_duty, oxygen_status, medicine_status}
            
        Returns:
            Dictionary with all derived decisions
        """
        risk_level = DecisionLogic.classify_risk_level(
            ml_predictions["risk_score"]
        )
        
        additional_beds = DecisionLogic.calculate_additional_beds(
            hospital_data["icu_total"],
            ml_predictions["expected_icu_increase_pct"]
        )
        
        additional_staff = DecisionLogic.calculate_additional_staff(
            hospital_data["daily_patients"],
            hospital_data["staff_on_duty"],
            ml_predictions["expected_er_increase_pct"]
        )
        
        supply_status = DecisionLogic.determine_supply_status(
            ml_predictions["expected_er_increase_pct"],
            hospital_data["oxygen_status"],
            hospital_data["medicine_status"]
        )
        
        logger.info(
            f"✅ Decisions: risk_level={risk_level}, beds={additional_beds}, "
            f"staff={additional_staff}, supply={supply_status}"
        )
        
        return {
            "risk_level": risk_level,
            "additional_icu_beds": additional_beds,
            "additional_staff": additional_staff,
            "supply_status": supply_status
        }
