import React from 'react';
import Link from 'next/link';
import { Logo } from '../components/Logo';

export const metadata = {
  title: 'Nutzungsbedingungen (Terms of Service) | MIMAROS AutoShorts AI',
  description: 'Nutzungsbedingungen für die Nutzung der MIMAROS Social Media Automation Plattform.',
};

export default function TermsPage() {
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
            MIMAROS TERMS OF SERVICE
          </span>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight mt-1">
            Nutzungsbedingungen (Terms of Service)
          </h1>
          <p className="text-sm text-[#94A3B8] mt-2">
            Stand: September 2026 | Gültig für die Nutzung der MIMAROS AutoShorts AI Plattform.
          </p>
        </div>

        <section className="bg-[#0F172A]/60 border border-white/10 p-6 sm:p-8 rounded-2xl space-y-6 text-sm leading-relaxed text-[#CBD5E1]">
          <div>
            <h2 className="text-lg font-bold text-white mb-2">1. Geltungsbereich</h2>
            <p>
              Diese Nutzungsbedingungen regeln die Nutzung der <strong>MIMAROS AutoShorts AI</strong> Software und der zugehörigen Web-Dienste. Mit der Nutzung der Plattform stimmen Sie diesen Bedingungen zu.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">2. Leistungsbeschreibung</h2>
            <p>
              MIMAROS stellt Werkzeuge zur KI-gestützten Analyse, Formatierung (9:16 Vertikalvideo), Untertitelung und automatisierten Veröffentlichung von Videoinhalten auf Drittplattformen (YouTube, TikTok, Instagram, LinkedIn) bereit.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">3. Pflichten und Verantwortung des Nutzers</h2>
            <p>
              Der Nutzer ist allein verantwortlich für die von ihm hochgeladenen, generierten und veröffentlichten Inhalte. Es dürfen keine Inhalte verbreitet werden, die gegen geltendes Recht, Urheberrechte Dritter oder die Richtlinien der jeweiligen Social-Media-Netzwerke verstoßen.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">4. Verknüpfung von Drittanbieter-Diensten</h2>
            <p>
              Bei Nutzung der Auto-Posting-Funktion gelten zusätzlich die offiziellen Nutzungsbedingungen und Community-Richtlinien der angebundenen Plattformen (YouTube Terms of Service, TikTok Community Guidelines, Meta Platform Terms, LinkedIn User Agreement).
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">5. Verfügbarkeit und Haftung</h2>
            <p>
              MIMAROS bemüht sich um eine kontinuierliche Verfügbarkeit der Dienste. Für Ausfälle von Drittanbieter-Schnittstellen (APIs von Meta, Google, TikTok, LinkedIn) oder vorübergehende Wartungsarbeiten wird keine Haftung übernommen.
            </p>
          </div>

          <div>
            <h2 className="text-lg font-bold text-white mb-2">6. Kontakt</h2>
            <p>
              Bei Fragen zu diesen Nutzungsbedingungen erreichen Sie uns unter <a href="https://mimaros.eu" className="text-[#14AEEA] hover:underline">mimaros.eu</a>.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
