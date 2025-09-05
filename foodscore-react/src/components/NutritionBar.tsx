import React from 'react';
import { motion } from 'framer-motion';

interface NutritionBarProps {
  label: string;
  value: number;
  maxValue: number;
  unit: string;
  color?: string;
  className?: string;
}

const NutritionBar: React.FC<NutritionBarProps> = ({
  label,
  value,
  maxValue,
  unit,
  className = ''
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const getBarColor = (percentage: number) => {
    if (percentage >= 80) return '#ef4444'; // Red - High
    if (percentage >= 60) return '#f97316'; // Orange - Medium-High
    if (percentage >= 40) return '#ffffff'; // White for dark theme - Medium
    return '#22c55e'; // Green - Low/Good
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-300">{label}</span>
        <span className="text-sm text-gray-400">
          {value.toFixed(1)}{unit}
        </span>
      </div>
      
      <div className="relative h-3 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: getBarColor(percentage) }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
        
        {/* Glow effect */}
        <motion.div
          className="absolute inset-0 rounded-full opacity-30"
          style={{ 
            background: `linear-gradient(90deg, transparent, ${getBarColor(percentage)}, transparent)`,
            filter: 'blur(4px)'
          }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
      
      <div className="text-xs text-gray-500">
        {percentage >= 80 ? 'High' : 
         percentage >= 60 ? 'Medium-High' : 
         percentage >= 40 ? 'Medium' : 'Low'}
      </div>
    </div>
  );
};

export default NutritionBar;
