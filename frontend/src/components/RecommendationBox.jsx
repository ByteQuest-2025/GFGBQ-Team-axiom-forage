// Recommendation Box Component
import React from 'react';
import { ClipboardCheck, ArrowRightCircle } from 'lucide-react';

const RecommendationBox = ({ recommendations, alertLevel }) => {
  // Border colors based on the severity of the recommendations
  const borderColors = {
    Critical: 'border-red-500 bg-red-50',
    High: 'border-orange-400 bg-orange-50',
    Elevated: 'border-yellow-400 bg-yellow-50',
    Normal: 'border-green-400 bg-green-50',
  };

  return (
    <div className={`p-6 rounded-xl border-l-8 shadow-sm ${borderColors[alertLevel] || borderColors.Normal}`}>
      <div className="flex items-center gap-3 mb-4">
        <ClipboardCheck className="w-6 h-6 text-gray-700" />
        <h3 className="text-xl font-bold text-gray-800">Operational Recommendations</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((text, index) => (
          <div key={index} className="flex items-start gap-3 bg-white/60 p-3 rounded-lg border border-white/40 shadow-sm">
            <ArrowRightCircle className="w-5 h-5 mt-0.5 text-blue-600 flex-shrink-0" />
            <p className="text-gray-700 font-medium leading-tight">{text}</p>
          </div>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 mt-4 italic">
        * Recommendations generated based on predicted {alertLevel} load status.
      </p>
    </div>
  );
};

export default RecommendationBox;