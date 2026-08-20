'use client';
import React, { useId } from 'react';

export const Logo = ({ className = "w-10 h-10 shrink-0 block" }: { className?: string }) => {
  const id = useId();
  const cleanId = `mimarosGrad-${id.replace(/[^a-zA-Z0-9_-]/g, '')}`;

  return (
    <div className={`relative shrink-0 flex items-center justify-center ${className}`}>
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        viewBox="0 0 100 100" 
        className="w-full h-full drop-shadow-[0_2px_12px_rgba(20,174,234,0.5)]"
        fill="none"
      >
        <defs>
          <linearGradient id={cleanId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#14AEEA" />
            <stop offset="100%" stopColor="#D9A83A" />
          </linearGradient>
        </defs>
        {/* Outer Glowing Circle */}
        <circle cx="50" cy="50" r="42" stroke={`url(#${cleanId})`} strokeWidth="6"/>
        {/* Center Play Triangle */}
        <polygon points="42,32 42,68 72,50" fill={`url(#${cleanId})`}/>
      </svg>
    </div>
  );
};

export default Logo;

