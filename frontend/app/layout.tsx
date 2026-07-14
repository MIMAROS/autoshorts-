import type { Metadata } from 'next'
import { Work_Sans, Lato, Josefin_Sans, Poppins } from 'next/font/google'
import './globals.css'

const workSans = Work_Sans({ subsets: ['latin'], variable: '--font-work-sans' })
const lato = Lato({ weight: ['300', '400', '700'], subsets: ['latin'], variable: '--font-lato' })
const josefin = Josefin_Sans({ subsets: ['latin'], variable: '--font-josefin' })
const poppins = Poppins({ weight: ['400', '600', '700'], subsets: ['latin'], variable: '--font-poppins' })

export const metadata: Metadata = {
  title: 'AutoShorts AI',
  description: 'Convert YouTube videos to viral Shorts',
  manifest: '/manifest.json'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${workSans.variable} ${lato.variable} ${josefin.variable} ${poppins.variable} font-sans`}>{children}</body>
    </html>
  )
}
