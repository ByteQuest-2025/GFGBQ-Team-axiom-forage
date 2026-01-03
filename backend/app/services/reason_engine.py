"""
Reason & Recommendation Engine - Traceable Explanations.

CRITICAL: Reasons must be based on INPUT DATA, not ML internals.

Examples:
- "ICU occupancy at 85% (above 80% threshold)"
- "Heatwave detected: 42°C (normal: 25-35°C)"
- "Weekend staffing risk (historically 15% higher accidents)"
- "Oxygen supplies low (current stock below safety threshold)"

Recommendations are protocol-based, tied to risk level.
"""

from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ReasonEngine:
    """
    Generates human-readable, traceable explanations for predictions.
    All reasons must be derivable from input features.
    """
    
    # Thresholds for reason generation
    THRESHOLDS = {
        "icu_occupancy_high": 0.80,
        "icu_occupancy_critical": 0.90,
        "temp_heatwave": 38,  # °C
        "temp_extreme": 42,
        "rain_heavy": 30,  # mm
        "rain_extreme": 50,
        "staff_shortage": 8,  # minimum staff
    }
    
    @staticmethod
    def generate_reasons(
        feature_vector: Dict,
        hospital_data: Dict,
        backend_context: Dict
    ) -> List[str]:
        """
        Generate traceable reasons based on input data.
        
        Args:
            feature_vector: Complete 11-feature vector
            hospital_data: Raw hospital data
            backend_context: External context
            
        Returns:
            List of human-readable reason strings
        """
        reasons = []
        
        # 1. ICU Occupancy Reasons
        icu_occ = feature_vector.get("icu_occupancy_pct", 0)
        if icu_occ > ReasonEngine.THRESHOLDS["icu_occupancy_critical"]:
            reasons.append(
                f"🚨 CRITICAL: ICU occupancy at {icu_occ*100:.0f}% "
                f"(threshold: {ReasonEngine.THRESHOLDS['icu_occupancy_critical']*100:.0f}%)"
            )
        elif icu_occ > ReasonEngine.THRESHOLDS["icu_occupancy_high"]:
            reasons.append(
                f"⚠️  ICU occupancy at {icu_occ*100:.0f}% "
                f"(above {ReasonEngine.THRESHOLDS['icu_occupancy_high']*100:.0f}% threshold)"
            )
        
        # 2. Temperature/Weather Reasons
        temp = backend_context.get("temp_max")
        if temp and temp > ReasonEngine.THRESHOLDS["temp_extreme"]:
            reasons.append(
                f"🌡️  Extreme heat: {temp}°C (increases cardiac/respiratory stress)"
            )
        elif temp and temp > ReasonEngine.THRESHOLDS["temp_heatwave"]:
            reasons.append(
                f"🌡️  Heatwave detected: {temp}°C (normal range: 25-35°C)"
            )
        
        # 3. Rainfall Reasons
        rain = backend_context.get("rain_mm", 0)
        if rain > ReasonEngine.THRESHOLDS["rain_extreme"]:
            reasons.append(
                f"🌧️  Extreme rainfall: {rain}mm (high accident risk)"
            )
        elif rain > ReasonEngine.THRESHOLDS["rain_heavy"]:
            reasons.append(
                f"🌧️  Heavy rain: {rain}mm (increased accident rate expected)"
            )
        
        # 4. Staffing Reasons
        staff = hospital_data.get("staff_on_duty", 0)
        if staff < ReasonEngine.THRESHOLDS["staff_shortage"]:
            reasons.append(
                f"👥 Staff below threshold: {staff} on duty (minimum: {ReasonEngine.THRESHOLDS['staff_shortage']})"
            )
        
        # 5. Weekend Risk
        if backend_context.get("is_weekend"):
            reasons.append(
                "📅 Weekend: Historically 15% higher accident rates"
            )
        
        # 6. Festival Risk
        if backend_context.get("is_festival"):
            reasons.append(
                "🎉 Festival/Holiday: Mass gathering event increases ER load"
            )
        
        # 7. Supply Chain Warnings
        if hospital_data.get("oxygen_status") == "low":
            reasons.append(
                "💨 Oxygen supplies LOW (below safety stock threshold)"
            )
        
        if hospital_data.get("medicine_status") == "low":
            reasons.append(
                "💊 Medicine inventory LOW (restock recommended)"
            )
        
        # 8. Seasonal Illness
        seasonal_weight = backend_context.get("seasonal_illness_weight", 0)
        if seasonal_weight > 0.7:
            reasons.append(
                f"🦠 High seasonal illness period (weight: {seasonal_weight:.1f})"
            )
        
        logger.info(f"✅ Generated {len(reasons)} traceable reasons")
        return reasons
    
    @staticmethod
    def get_recommendations(risk_level: str, decisions: Dict) -> List[str]:
        """
        Generate protocol-based recommendations tied to risk level.
        
        Args:
            risk_level: "Critical", "High", "Elevated", or "Normal"
            decisions: Derived decisions (beds, staff, supply_status)
            
        Returns:
            List of actionable recommendation strings
        """
        recommendations = []
        
        # Base recommendations by risk level
        base_recs = {
            "Critical": [
                "🚨 URGENT: Activate Surge Staffing Protocol (Level 3)",
                "🚑 Immediately divert non-critical ambulances to nearby facilities",
                "❌ Suspend ALL elective surgeries for next 48 hours",
                "🏥 Open emergency overflow wards and prepare temporary beds"
            ],
            "High": [
                "📞 Call in on-call nursing staff immediately",
                "🏃 Expedite discharge process for medically fit patients",
                "🛏️  Prioritize ICU bed turnaround and cleaning",
                "📦 Review oxygen, PPE, and medicine inventory levels"
            ],
            "Elevated": [
                "👀 Monitor ICU bed availability every 2 hours",
                "📋 Brief shift leads on expected patient intake increase",
                "🚨 Ensure trauma and emergency units are on standby",
                "🔧 Conduct equipment checks and verify backup systems"
            ],
            "Normal": [
                "✅ Maintain standard shift rotations",
                "🔧 Routine equipment maintenance and checks",
                "📅 No change to elective surgery schedules",
                "📊 Continue standard community health monitoring"
            ]
        }
        
        recommendations.extend(base_recs.get(risk_level, []))
        
        # Additional specific recommendations based on decisions
        if decisions["additional_icu_beds"] > 0:
            recommendations.append(
                f"🛏️  Prepare {decisions['additional_icu_beds']} additional ICU beds"
            )
        
        if decisions["additional_staff"] > 0:
            recommendations.append(
                f"👥 Summon {decisions['additional_staff']} additional staff members"
            )
        
        if decisions["supply_status"] == "Low":
            recommendations.append(
                "📦 URGENT: Restock oxygen and essential medicines before surge"
            )
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations


class ExplanationEngine:
    """
    Combines reasons and recommendations into complete explanation.
    """
    
    @staticmethod
    def generate_explanation(
        feature_vector: Dict,
        hospital_data: Dict,
        backend_context: Dict,
        ml_predictions: Dict,
        decisions: Dict
    ) -> Dict:
        """
        Generate complete traceable explanation.
        
        Returns:
            {
                "reasons": List[str],  # Why this prediction
                "recommendations": List[str],  # What to do
                "summary": str  # One-line summary
            }
        """
        reasons = ReasonEngine.generate_reasons(
            feature_vector,
            hospital_data,
            backend_context
        )
        
        recommendations = ReasonEngine.get_recommendations(
            decisions["risk_level"],
            decisions
        )
        
        # Generate summary
        risk_pct = ml_predictions["risk_score"] * 100
        summary = (
            f"{decisions['risk_level']} risk ({risk_pct:.0f}%) - "
            f"{len(reasons)} contributing factors identified"
        )
        
        return {
            "reasons": reasons,
            "recommendations": recommendations,
            "summary": summary
        }
