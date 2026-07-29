import { MetadataRoute } from 'next'
 
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Mimaros AutoShorts AI',
    short_name: 'mimaros Shorts',
    description: 'Verwandle deine langen Videos vollautomatisch in virale Shorts',
    start_url: '/',
    display: 'standalone',
    background_color: '#0B192C',
    theme_color: '#14AEEA',
    icons: [
      {
        src: '/icon-192.png?v=2.0.0',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512.png?v=2.0.0',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
