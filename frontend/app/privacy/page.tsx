import React from 'react';
import Link from 'next/link';
import { Logo } from '../components/Logo';

export const metadata = {
  title: 'Datenschutzerklärung | MIMAROS AutoShorts AI',
  description: 'Datenschutzerklärung und Richtlinien zur Datenverarbeitung der MIMAROS Social Media Automation Plattform.',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#0B111A] text-[#EEF3F8] font-sans selection:bg-[#14AEEA]/30">
      <header className="w-full border-b border-white/10 bg-[#0F172A]/80 backdrop-blur-xl sticky top-0 z-30 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <Logo className="w-8 h-8 drop-shadow-[0_0_12px_rgba(20,174,234,0.5)]" />
          <span className="font-bold text-lg tracking-tight text-white">MIMAROS</span>
        </Link>
        <Link href="/" className="text-xs text-[#14AEEA] hover:underline font-bold">
          ← Zurück zum Dashboard
        </Link>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 space-y-8">
        <div>
          <span className="text-xs font-mono uppercase tracking-widest text-[#C89B31] font-bold">
            MIMAROS LEGAL & PRIVACY
          </span>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight mt-1">
            Datenschutzerklärung (Privacy Policy)
          </h1>
          <p className="text-sm text-[#94A3B8] mt-2">
            Stand: September 2026 | Gültig für alle Dienste der MIMAROS Social Media Automation Plattform.
          </p>
        </div>

        <section className="bg-[#0F172A]/60 border border-white/10 p-6 sm:p-8 rounded-2xl space-y-6 text-sm leading-relaxed text-[#CBD5E1]">
          <div>
            <h2 className="text-lg font-bold text-white mb-2">1. Verantwortliche Stelle</h2>
            <p>
              Verantwortlich für die Datenverarbeitung auf dieser Plattform ist die Marke <strong>MIMAROS</strong> (Webseite: <a href="https://mimaros.eu" className="text-[#14AEEA] hover:underline">mimaros.eu</a>).
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">2. Zweck der Datenverarbeitung</h2>
            <p>
              MIMAROS ist eine Software zur automatisierten Erstellung, Bearbeitung und Veröffentlichung von Kurzvideos (YouTube Shorts, Instagram Reels, TikTok Videos, LinkedIn Posts). Zur Erbringung dieser Dienste werden vom Nutzer autorisierte Daten verarbeitet.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">3. Anbindung von Social-Media-Konten (OAuth 2.0)</h2>
            <p>
              Wenn Sie Ihr YouTube-, Instagram-, TikTok- oder LinkedIn-Konto verknüpfen, nutzen wir das offizielle OAuth 2.0-Autorisierungsverfahren der jeweiligen Plattform. Wir erhalten zu keinem Zeitpunkt Zugriff auf Ihr persönliches Passwort.
            </p>
            <ul className="list-disc pl-5 mt-2 space-y-1 text-xs text-[#94A3B8]">
              <li><strong>YouTube:</strong> Zugriffsberechtigung zur Veröffentlichung von YouTube Shorts über die YouTube Data API v3 (Google API Services User Data Policy konform).</li>
              <li><strong>TikTok:</strong> Autorisierung über die TikTok Content Posting API zum Hochladen von Videos.</li>
              <li><strong>Instagram:</strong> Autorisierung über die Meta Graph API zum Veröffentlichen von Reels.</li>
              <li><strong>LinkedIn:</strong> Autorisierung über die LinkedIn Community Management & Post API.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">4. Speicherung und Sicherheit der Zugriffs-Token</h2>
            <p>
              Die für das automatische Veröffentlichen notwendigen Zugriffstoken (Access & Refresh Tokens) werden verschlüsselt auf gesicherten Servern gespeichert. Sie können die Verknüpfung jederzeit im Dashboard mit einem Klick auf &quot;Trennen&quot; vollständig aufheben.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">5. Weitergabe von Daten an Dritte</h2>
            <p>
              Ihre Daten werden vertraulich behandelt und niemals an unbefugte Dritte verkauft oder weitergegeben. Daten werden ausschließlich zur Ausführung der von Ihnen beauftragten Video-Erstellung und -Veröffentlichung an die ausgewählten Social-Media-Netzwerke übermittelt.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">6. Ihre Rechte (DSGVO)</h2>
            <p>
              Sie haben jederzeit das Recht auf Auskunft, Berichtigung, Sperrung oder Löschung Ihrer gespeicherten Daten. Zur Ausübung Ihrer Rechte kontaktieren Sie uns bitte über <a href="https://mimaros.eu" className="text-[#14AEEA] hover:underline">mimaros.eu</a>.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
