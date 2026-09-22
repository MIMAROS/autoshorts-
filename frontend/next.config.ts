import type { NextConfig } from "next";

const defaultBackend = process.env.NODE_ENV === 'production' 
  ? 'https://autoshorts-backend.onrender.com' 
  : 'http://127.0.0.1:8000';

const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || defaultBackend;


const nextConfig: NextConfig = {
  allowedDevOrigins: [
    'localhost:3000',
    'localhost:3001',
    '127.0.0.1:3000',
    '127.0.0.1:3001',
    '192.168.5.20',
    '*.serveousercontent.com',
    '*.onrender.com',
    'autoshorts-frontend-6yo8.onrender.com',
    '*.loca.lt',
    '*.ngrok-free.app',
  ],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl.replace(/\/$/, '')}/api/:path*`, // Proxy to Backend
      },
      {
        source: '/videos/:path*',
        destination: `${backendUrl.replace(/\/$/, '')}/videos/:path*`, // Proxy Video Static Files
      },
    ];
  },
};

export default nextConfig;
