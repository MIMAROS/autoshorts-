import type { Metadata } from 'next'
import { Work_Sans, Lato, Josefin_Sans, Poppins } from 'next/font/google'
import './globals.css'

const workSans = Work_Sans({ subsets: ['latin'], variable: '--font-work-sans' })
const lato = Lato({ weight: ['300', '400', '700'], subsets: ['latin'], variable: '--font-lato' })
const josefin = Josefin_Sans({ subsets: ['latin'], variable: '--font-josefin' })
const poppins = Poppins({ weight: ['400', '600', '700'], subsets: ['latin'], variable: '--font-poppins' })

export const metadata: Metadata = {
  title: 'mimaros AutoShorts AI',
  description: 'Convert YouTube videos to viral Shorts',
  manifest: '/manifest.json?v=3.0.0',
  icons: {
    icon: '/favicon.svg?v=3.0.0',
    shortcut: '/favicon.ico?v=3.0.0',
    apple: '/icon-192.png?v=3.0.0',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de">
      <head>
        <link rel="icon" href="/favicon.svg?v=3.0.0" type="image/svg+xml" />
        <link rel="icon" href="/icon-192.png?v=3.0.0" sizes="192x192" type="image/png" />
        <link rel="apple-touch-icon" href="/icon-192.png?v=3.0.0" />
        <link rel="shortcut icon" href="/favicon.ico?v=3.0.0" />
      </head>
      <body className={`${workSans.variable} ${lato.variable} ${josefin.variable} ${poppins.variable} font-sans bg-[#0B111A] text-[#EEF3F8]`}>
        {children}
        <script dangerouslySetInnerHTML={{__html: `
          if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
              navigator.serviceWorker.register('/sw.js').then(function(reg) {
                console.log('ServiceWorker registration successful');
              }).catch(function(err) {
                console.log('ServiceWorker registration failed:', err);
              });
            });
          }
        `}} />
      </body>
    </html>
  )
}
