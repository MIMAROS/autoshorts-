'use client';
import React from 'react';

export const Logo = ({ className = "w-10 h-10 shrink-0 block" }: { className?: string }) => {
  return (
    <div className={`relative shrink-0 flex items-center justify-center ${className}`}>
      <img 
        src="/logo.png" 
        alt="MIMAROS Logo" 
        className="w-full h-full object-contain drop-shadow-[0_2px_10px_rgba(20,174,234,0.4)]"
        onError={(e) => {
          // Fallback if image fails
          e.currentTarget.style.display = 'none';
        }}
      />
    </div>
  );
};

export default Logo;

