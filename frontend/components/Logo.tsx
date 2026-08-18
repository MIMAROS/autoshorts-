'use client';
import React, { useId } from 'react';

export const Logo = ({ className = "w-10 h-10 shrink-0 block" }: { className?: string }) => {
  const id = useId();
  const cleanId = `mimarosGrad-${id.replace(/[^a-zA-Z0-9_-]/g, '')}`;

  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 100 100" 
      className={`shrink-0 block ${className}`}
      fill="none"
    >
      <defs>
        <linearGradient id={cleanId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#14AEEA" />
          <stop offset="100%" stopColor="#D9A83A" />
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="44" fill="none" stroke={`url(#${cleanId})`} strokeWidth="5"/>
      <polygon points="42,34 42,66 68,50" fill={`url(#${cleanId})`}/>
    </svg>
  );
};

export default Logo;

