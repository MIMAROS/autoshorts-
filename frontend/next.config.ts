import type { NextConfig } from "next";

const nextConfig: NextConfig = {

  allowedDevOrigins: ['192.168.5.20', 'localhost', '127.0.0.1', '2db36ece4d294df4-93-249-177-38.serveousercontent.com', 'autoshorts-mimaros.loca.lt'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/videos/:path*',
        destination: 'http://127.0.0.1:8000/videos/:path*',
      },
    ];
  },
};

export default nextConfig;
