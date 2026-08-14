import { MetadataRoute } from 'next'
 
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'MIMAROS AutoShorts AI',
    short_name: 'MIMAROS Shorts',
    description: 'Verwandle deine langen Videos vollautomatisch in virale Shorts im MIMAROS CI',
    start_url: '/',
    display: 'standalone',
    background_color: '#0B111A',
    theme_color: '#14AEEA',
    icons: [
      {
        src: '/icon-192.png?v=7.0.0',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512.png?v=7.0.0',
        sizes: '512x512',
        type: 'image/png',
      },
      {
        src: '/apple-touch-icon.png?v=7.0.0',
        sizes: '180x180',
        type: 'image/png',
      },
    ],
  }
}
