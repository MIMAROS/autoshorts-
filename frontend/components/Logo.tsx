import React from 'react';

export const Logo = ({ className = "w-full h-full" }: { className?: string }) => (
  <svg viewBox="0 0 100 100" className={className}>
    <defs>
      <linearGradient id="mimarosGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#56CCF2" />
        <stop offset="100%" stopColor="#F2994A" />
      </linearGradient>
    </defs>
    <circle cx="50" cy="50" r="44" fill="none" stroke="url(#mimarosGrad)" strokeWidth="3.5"/>
    <path d="M 34 10.65 L 34 89.35 M 66 10.65 L 66 89.35" fill="none" stroke="url(#mimarosGrad)" strokeWidth="3.5" strokeLinecap="round"/>
    <polygon points="44,42 44,58 56,50" fill="url(#mimarosGrad)"/>
  </svg>
);

export default Logo;
