'use client';
import dynamic from 'next/dynamic';
const FullCalendar = dynamic(() => import('@fullcalendar/react'), { ssr: false });
import dayGridPlugin from '@fullcalendar/daygrid';
import { useState, useRef, useEffect } from 'react';
import { Play, Scissors, Subtitles, UploadCloud, Loader2, Sparkles, Calendar, Check, Settings, X, Clock, Video, Home, Menu, Share2, Download, Edit2, TrendingUp, Flame, Type, MonitorPlay, ChevronUp, ChevronDown, Layout, Volume2, Mic } from 'lucide-react';

const LogoIcon = ({ className = "w-10 h-10 md:w-12 md:h-12 shrink-0" }: { className?: string }) => (
  <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" className={`w-10 h-10 md:w-12 md:h-12 shrink-0 max-w-[48px] max-h-[48px] ${className}`}>
    <defs>
      <linearGradient id="mimaros-brand-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#14AEEA" />
        <stop offset="50%" stopColor="#0B7FA8" />
        <stop offset="100%" stopColor="#C89B31" />
      </linearGradient>
      <filter id="mimaros-glow-eff" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="1.5" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>
    {/* 1. Feiner runder Außenkreis */}
    <circle cx="32" cy="32" r="28" stroke="url(#mimaros-brand-grad)" strokeWidth="2.5" filter="url(#mimaros-glow-eff)" />
    
    {/* 2. Zwei vertikale parallele Linien (Smartphone 9:16 Ränder) */}
    <line x1="22" y1="4" x2="22" y2="60" stroke="url(#mimaros-brand-grad)" strokeWidth="2" opacity="0.85" />
    <line x1="42" y1="4" x2="42" y2="60" stroke="url(#mimaros-brand-grad)" strokeWidth="2" opacity="0.85" />
    
    {/* 3. Minimalistischer Play-Button exakt in der Mitte */}
    <path d="M29 25.5L38 32L29 38.5V25.5Z" fill="url(#mimaros-brand-grad)" filter="url(#mimaros-glow-eff)" />
  </svg>
);

const API_BASE = (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL)
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '')
  : '';

export default function Page() {
  // Navigation & Layout
  const [currentView, setCurrentView] = useState('new'); // 'new', 'history', 'calendar'
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // New Project State
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [localFile, setLocalFile] = useState<File | null>(null);
  
  // Sequence State
  type SequenceItem = { id: string; type: 'url' | 'local'; content: string; file?: File; name: string };
  const [sequence, setSequence] = useState<SequenceItem[]>([]);
  const [isSequenceMode, setIsSequenceMode] = useState(false);

  const [clipLength, setClipLength] = useState('auto');
  const [resolution, setResolution] = useState('720p');
  const [videoLang, setVideoLang] = useState('auto');
  const [subtitleLang, setSubtitleLang] = useState('auto');
  
  // Metadata & Trimming State
  const [videoMetadata, setVideoMetadata] = useState<{title: string, duration: number, thumbnail: string} | null>(null);
  const [trimStart, setTrimStart] = useState<number | ''>('');
  const [trimEnd, setTrimEnd] = useState<number | ''>('');
  const [isFetchingMetadata, setIsFetchingMetadata] = useState(false);
  
  // Global Design & Preview State
  const [globalSubtitleConfig, setGlobalSubtitleConfig] = useState({ design: 'minimalist', cta: 'follow', text: '', template: 'clean_lower_third', watermark_text: 'mimaros.eu' });
  const [useMasterCi, setUseMasterCi] = useState(true);
  const [primaryColor, setPrimaryColor] = useState('#14AEEA');
  const [textColor, setTextColor] = useState('#ffffff');
  const [highlightColor, setHighlightColor] = useState('#D4AF37');
  const [fontName, setFontName] = useState('Work Sans');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPosition, setLogoPosition] = useState('top-left');
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [logoPath, setLogoPath] = useState<string>('');
  const [logoUploading, setLogoUploading] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [hookHeader, setHookHeader] = useState('DAS DARFST DU NICHT VERPASSEN 🔥');
  const [showTitle, setShowTitle] = useState(true);
  const [showLogo, setShowLogo] = useState(true);
  const [showSubtitles, setShowSubtitles] = useState(true);
  const [showCTA, setShowCTA] = useState(true);
  const [activeAccordion, setActiveAccordion] = useState<string | null>('basic');
  const [globalPreviewUrl, setGlobalPreviewUrl] = useState('');
  const [isGlobalPreviewing, setIsGlobalPreviewing] = useState(false);

  // KI Voiceover State
  const [voiceoverUrl, setVoiceoverUrl] = useState<string>('');
  const [isGeneratingVoiceover, setIsGeneratingVoiceover] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState('alloy');

  const handleGenerateVoiceover = async () => {
    if (!hookHeader || !hookHeader.trim()) {
      alert("Bitte gib zuerst einen Skript-Text oder Titel ein.");
      return;
    }
    setIsGeneratingVoiceover(true);
    try {
      const res = await fetch(`${API_BASE}/api/generate-voiceover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: hookHeader, voice: selectedVoice, lang: videoLang })
      });
      if (!res.ok) throw new Error("Voiceover-Generierung fehlgeschlagen.");
      const data = await res.json();
      setVoiceoverUrl(data.audio_url.startsWith('/') ? `${API_BASE}${data.audio_url}` : data.audio_url);
    } catch (err) {
      console.error(err);
      alert("Fehler bei der KI-Voiceover-Generierung.");
    } finally {
      setIsGeneratingVoiceover(false);
    }
  };

  // Processing State
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [clips, setClips] = useState<any[]>([]);
  const [currentJobId, setCurrentJobId] = useState('');

  // History & Schedules
  const [history, setHistory] = useState<any[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  
  // Modals
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({ date: '', time: '', platforms: ['YouTube Shorts'], caption: '' });
  const [schedulingClip, setSchedulingClip] = useState<any>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [authStatus, setAuthStatus] = useState({ youtube: false, tiktok: false });

  useEffect(() => {
    fetchSchedules();
    fetchHistory();
    fetchAuthStatus();
    setHookHeader(prev => prev || 'DAS DARFST DU NICHT VERPASSEN 🔥');
    generateAutoTitle('VIRALES SHORTS VIDEO HOOK');
  }, []);

  const fetchAuthStatus = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/auth/status`);
        const data = await res.json();
        setAuthStatus({ youtube: data.youtube, tiktok: data.tiktok });
    } catch (e) {
        console.error("Error fetching auth status:", e);
    }
  };

  const fetchSchedules = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/schedules`);
        const data = await res.json();
        setSchedules(data.schedules || []);
    } catch (e) {
        console.error("Error fetching schedules:", e);
    }
  };

  const fetchHistory = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/history`);
        const data = await res.json();
        setHistory(data.history || []);
    } catch (e) {
        console.error("Error fetching history:", e);
    }
  };

  const generateAutoTitle = async (inputText: string) => {
    if (!inputText) return;
    try {
        const res = await fetch(`${API_BASE}/api/generate-viral-title`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: inputText })
        });
        if (res.ok) {
            const data = await res.json();
            if (data.title) {
                setHookHeader(data.title.toUpperCase());
            }
        }
    } catch (err) {
        console.error("Fehler bei Auto-Titel-Generierung:", err);
    }
  };

   const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (isSequenceMode) {
          const file = e.dataTransfer.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          const file = e.dataTransfer.files[0];
          setLocalFile(file);
          setYoutubeUrl('');
          generateAutoTitle(file.name);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      if (isSequenceMode) {
          const file = e.target.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          const file = e.target.files[0];
          setLocalFile(file);
          setYoutubeUrl(''); 
          generateAutoTitle(file.name);
      }
    }
  };

  const addYoutubeToSequence = () => {
      if (youtubeUrl) {
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'url', content: youtubeUrl, name: youtubeUrl }]);
          setYoutubeUrl('');
      }
  };

  const moveSequenceItem = (index: number, direction: 'up' | 'down') => {
      const newSequence = [...sequence];
      if (direction === 'up' && index > 0) {
          [newSequence[index - 1], newSequence[index]] = [newSequence[index], newSequence[index - 1]];
      } else if (direction === 'down' && index < newSequence.length - 1) {
          [newSequence[index + 1], newSequence[index]] = [newSequence[index], newSequence[index + 1]];
      }
      setSequence(newSequence);
  };

  const removeSequenceItem = (index: number) => {
      setSequence(prev => prev.filter((_, i) => i !== index));
  };

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setLogoFile(file);
      setLogoPreview(URL.createObjectURL(file));
      
      setLogoUploading(true);
      const logoData = new FormData();
      logoData.append('file', file);
      try {
          const logoRes = await fetch(`${API_BASE}/api/upload-logo`, { method: 'POST', body: logoData });
          if (logoRes.ok) {
              const parsedLogo = await logoRes.json();
              setLogoPath(parsedLogo.logo_path);
          }
      } catch (err) {
          console.error("Logo upload error:", err);
      } finally {
          setLogoUploading(false);
      }
    }
  };

  const fetchVideoInfo = async (url: string) => {
      if (!url) return;
      setIsFetchingMetadata(true);
      try {
          const res = await fetch(`${API_BASE}/api/video-info`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ youtube_url: url })
          });
          
          if (!res.ok) {
              const text = await res.text();
              console.error("Response body:", text);
              alert("Fehler vom Server: " + text);
              return;
          }
          
          const data = await res.json();
          if (data.status === 'success') {
              setVideoMetadata(data.info);
              generateAutoTitle(data.info.title);
              if (data.info.duration > 600) {
                  setTrimStart(0);
                  setTrimEnd(600);
              } else {
                  setTrimStart('');
                  setTrimEnd('');
              }
          }
      } catch (e) {
          console.error(e);
      } finally {
          setIsFetchingMetadata(false);
      }
  };

  const handleGeneratePreview = async () => {
      setIsGlobalPreviewing(true);
      try {
          const config = {
              ...globalSubtitleConfig,
              use_master_ci: useMasterCi,
              primaryColor,
              textColor,
              highlightColor,
              fontName,
              logoPosition,
              logoPath: logoPath || null,
              design: globalSubtitleConfig.design || 'minimalist',
              resolution,
              hookHeader,
              showTitle,
              showLogo,
              showSubtitles,
              showCTA
          };

          const res = await fetch(`${API_BASE}/api/preview-clip`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ clip_path: 'demo', config })
          });
          
          if (!res.ok) throw new Error("Preview generation failed");
          
          const data = await res.json();
          setGlobalPreviewUrl(`${API_BASE}${data.preview_url}`);
      } catch (err) {
          console.error(err);
      } finally {
          setIsGlobalPreviewing(false);
      }
  };

  useEffect(() => {
      const delayDebounce = setTimeout(() => {
          handleGeneratePreview();
      }, 1000); // 1000ms debounce
      
      return () => clearTimeout(delayDebounce);
  }, [globalSubtitleConfig, useMasterCi, primaryColor, textColor, highlightColor, fontName, logoPosition, logoPath, resolution, hookHeader, showTitle, showLogo, showSubtitles, showCTA]);

  const handleProcess = async () => {
    if (!isSequenceMode && !youtubeUrl && !localFile) return;
    if (isSequenceMode && sequence.length === 0) return;
    
    setIsProcessing(true);
    setStatusMessage('Starte Verarbeitung...');
    setClips([]);
    
    try {
      const subConfig = {
          ...globalSubtitleConfig,
          primaryColor,
          textColor,
          highlightColor,
          fontName,
          logoPosition,
          logoPath: logoPath || null,
          useMasterCi,
          hookHeader,
          showTitle,
          showLogo,
          showSubtitles,
          showCTA,
          voiceoverUrl: voiceoverUrl || null
      };
      
      let jobId = '';
      if (isSequenceMode) {
          const formData = new FormData();
          const sequenceConfig = sequence.map((item, index) => {
              if (item.type === 'local') {
                  const filename = `file_${index}`;
                  formData.append(filename, item.file as Blob, item.file!.name);
                  return { type: 'file', filename: filename };
              } else {
                  return { type: 'url', content: item.content };
              }
          });
          
          formData.append('sequence_data', JSON.stringify(sequenceConfig));
          formData.append('resolution', resolution);
          formData.append('video_lang', videoLang);
          formData.append('subtitle_lang', subtitleLang);
          formData.append('subtitle_config', JSON.stringify(subConfig));
          
          const res = await fetch(`${API_BASE}/api/process-sequence`, {
              method: 'POST',
              body: formData
          });
          const data = await res.json();
          jobId = data.job_id;
      } else {
          if (localFile) {
              const formData = new FormData();
              formData.append('file', localFile);
              formData.append('resolution', resolution);
              formData.append('clip_length', clipLength);
              formData.append('video_lang', videoLang);
              formData.append('subtitle_lang', subtitleLang);
              formData.append('subtitle_config', JSON.stringify(subConfig));
              if (trimStart !== '') formData.append('trim_start', trimStart.toString());
              if (trimEnd !== '') formData.append('trim_end', trimEnd.toString());
              
              const res = await fetch(`${API_BASE}/api/upload-video`, {
                  method: 'POST',
                  body: formData
              });
              
              if (!res.ok) {
                  const text = await res.text().catch(() => '');
                  throw new Error(`Upload fehlgeschlagen (${res.status}): ${text}`);
              }
              
              const data = await res.json();
              jobId = data.job_id;
          } else {
              const payload: any = { 
                  youtube_url: youtubeUrl,
                  resolution: resolution,
                  clip_length: clipLength,
                  video_lang: videoLang,
                  subtitle_lang: subtitleLang,
                  subtitle_config: subConfig
              };
              if (trimStart !== '') payload.trim_start = Number(trimStart);
              if (trimEnd !== '') payload.trim_end = Number(trimEnd);
              
              const res = await fetch(`${API_BASE}/api/process-video`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
              });
              const data = await res.json();
              jobId = data.job_id;
          }
      }
      
      setCurrentJobId(jobId);
      if (!jobId) throw new Error('Kein Job ID erhalten');

      const interval = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE}/api/status/${jobId}`);
          const statusData = await statusRes.json();
          
          if (statusData.status === 'error') {
            clearInterval(interval);
            setIsProcessing(false);
            setStatusMessage('Fehler: ' + statusData.error);
            return;
          }
          
          if (statusData.hooks && statusData.hooks.length > 0 && !hookHeader) {
            setHookHeader(statusData.hooks[0].title);
          }
          
          setStatusMessage(`Status: ${statusData.status} (${statusData.progress}%)`);
          
          if (statusData.status === 'done') {
            clearInterval(interval);
            setIsProcessing(false);
            setStatusMessage('');
            
            const newClips = statusData.hooks.map((hook: any, index: number) => ({
              id: index + 1,
              title: hook.title || `Hook ${index + 1}`,
              start: hook.start_time_approx,
              end: hook.end_time_approx,
              rationale: hook.rationale,
              social_media_caption: hook.social_media_caption,
              viralScore: hook.viral_score || Math.floor(Math.random() * 20 + 80),
              videoUrl: statusData.clips && statusData.clips[index] ? statusData.clips[index] : null,
              clipPath: statusData.clips && statusData.clips[index] ? statusData.clips[index] : null
            }));
            setClips(newClips);
            fetchHistory(); 
          }
        } catch (e) {
          console.error("Fehler beim Status-Check:", e);
        }
      }, 3000);
      
    } catch (error: any) {
      console.error(error);
      setIsProcessing(false);
      setStatusMessage(`Fehler: ${error.message}`);
    }
  };

  const handleScheduleSubmit = async () => {
    try {
        await fetch(`${API_BASE}/api/schedule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: currentJobId || 'manual-job',
                video_url: schedulingClip?.videoUrl || '',
                platforms: scheduleForm.platforms,
                schedule_date: `${scheduleForm.date} ${scheduleForm.time}`,
                caption: scheduleForm.caption
            })
        });
        setShowScheduleModal(false);
        fetchSchedules();
        setCurrentView('calendar'); // Switch to calendar to see it
        setStatusMessage("Video erfolgreich eingeplant!");
    } catch (e) {
        console.error(e);
    }
  };

  const renderSidebar = () => (
    <>
    {/* Desktop Sidebar */}
    <div className={`hidden md:flex fixed inset-y-0 left-0 z-40 w-64 bg-panel/80 backdrop-blur-xl border-r border-borderGlass flex-col`}>
        <div className="p-6 flex items-center gap-3 border-b border-borderGlass">
            <LogoIcon className="w-11 h-11 shrink-0 drop-shadow-[0_0_12px_rgba(20,174,234,0.4)]" />
            <div>
                <h1 className="font-heading font-bold text-lg tracking-tight text-white leading-none">
                    mimaros
                </h1>
                <span className="text-[10px] font-bold tracking-widest text-mimaros-blue uppercase block mt-0.5">
                    AutoShorts AI
                </span>
            </div>
        </div>
        <nav className="flex-1 p-4 flex flex-col gap-2">
            <button onClick={() => setCurrentView('new')} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'new' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                <Sparkles className="w-5 h-5" /> Neues Projekt
            </button>
            <button onClick={() => setCurrentView('history')} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'history' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                <Video className="w-5 h-5" /> Meine Videos
            </button>
            <button onClick={() => setCurrentView('calendar')} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'calendar' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                <Calendar className="w-5 h-5" /> Kalender
            </button>
            <button onClick={() => setCurrentView('integrations')} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'integrations' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                <Share2 className="w-5 h-5" /> Verknüpfungen
            </button>
        </nav>
    </div>
    
    {/* Mobile Bottom Navigation */}
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-panel/90 backdrop-blur-xl border-t border-borderGlass flex justify-around p-3 pb-safe shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
        <button onClick={() => setCurrentView('new')} className={`flex flex-col items-center gap-1 ${currentView === 'new' ? 'text-mimaros-blue scale-110' : 'text-textDim hover:text-white'} transition-all`}>
            <Sparkles className="w-6 h-6" />
            <span className="text-[10px] font-bold">Neu</span>
        </button>
        <button onClick={() => setCurrentView('history')} className={`flex flex-col items-center gap-1 ${currentView === 'history' ? 'text-mimaros-blue scale-110' : 'text-textDim hover:text-white'} transition-all`}>
            <Video className="w-6 h-6" />
            <span className="text-[10px] font-bold">Videos</span>
        </button>
        <button onClick={() => setCurrentView('calendar')} className={`flex flex-col items-center gap-1 ${currentView === 'calendar' ? 'text-mimaros-blue scale-110' : 'text-textDim hover:text-white'} transition-all`}>
            <Calendar className="w-6 h-6" />
            <span className="text-[10px] font-bold">Plan</span>
        </button>
        <button onClick={() => setCurrentView('integrations')} className={`flex flex-col items-center gap-1 ${currentView === 'integrations' ? 'text-mimaros-blue scale-110' : 'text-textDim hover:text-white'} transition-all`}>
            <Share2 className="w-6 h-6" />
            <span className="text-[10px] font-bold">Apps</span>
        </button>
    </div>
    {/* Mobile Drawer */}
    {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm flex">
            <div className="w-64 bg-panel border-r border-borderGlass h-full flex flex-col">
                <div className="p-4 border-b border-borderGlass flex justify-between items-center">
                    <h2 className="font-heading font-bold text-xl text-white">Menü</h2>
                    <button onClick={() => setIsMobileMenuOpen(false)} className="text-textDim hover:text-white">
                        <X className="w-6 h-6" />
                    </button>
                </div>
                <nav className="flex-1 p-4 flex flex-col gap-2">
                    <button onClick={() => { setCurrentView('new'); setIsMobileMenuOpen(false); }} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'new' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                        <Sparkles className="w-5 h-5" /> Neues Projekt
                    </button>
                    <button onClick={() => { setCurrentView('history'); setIsMobileMenuOpen(false); }} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'history' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                        <Video className="w-5 h-5" /> Meine Videos
                    </button>
                    <button onClick={() => { setCurrentView('calendar'); setIsMobileMenuOpen(false); }} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'calendar' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                        <Calendar className="w-5 h-5" /> Kalender
                    </button>
                    <button onClick={() => { setCurrentView('integrations'); setIsMobileMenuOpen(false); }} className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all ${currentView === 'integrations' ? 'bg-mimaros-blue/10 text-mimaros-blue' : 'text-textDim hover:text-white hover:bg-background/50'}`}>
                        <Share2 className="w-5 h-5" /> Verknüpfungen
                    </button>
                </nav>
            </div>
            <div className="flex-1" onClick={() => setIsMobileMenuOpen(false)} />
        </div>
    )}
    </>
  );

  const renderNewProject = () => (
      <div className="flex-1 max-w-5xl mx-auto w-full flex flex-col gap-8">
          <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-8 flex flex-col space-y-8">
            <div className="text-center space-y-2">
              <span className="font-display text-[10px] uppercase tracking-[0.2em] text-mimaros-gold font-bold flex items-center justify-center gap-2">
                <div className="w-5 h-px bg-mimaros-gold/50" /> KI ANALYSE <div className="w-5 h-px bg-mimaros-gold/50" />
              </span>
              <h2 className="font-heading text-3xl font-bold text-white tracking-tight">Verwandle dein Video in Shorts</h2>
            </div>
            
            <div className="flex items-center justify-center gap-4 bg-background/50 p-2 rounded-xl border border-borderGlass mx-auto max-w-sm">
                <button 
                    onClick={() => setIsSequenceMode(false)}
                    className={`flex-1 py-2 px-4 rounded-lg font-bold text-sm transition-all ${!isSequenceMode ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'text-textDim hover:text-white'}`}
                >
                    Einzelner Clip
                </button>
                <button 
                    onClick={() => setIsSequenceMode(true)}
                    className={`flex-1 py-2 px-4 rounded-lg font-bold text-sm transition-all ${isSequenceMode ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'text-textDim hover:text-white'}`}
                >
                    Sequenz (Stitching)
                </button>
            </div>

            <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full">
                
                {/* UPOLAD SECTION */}
                {!isSequenceMode ? (
                    <>
                        <div 
                            onDragOver={(e) => e.preventDefault()} 
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${localFile ? 'border-mimaros-blue bg-mimaros-blue/5' : 'border-borderGlass hover:border-mimaros-blue/50 bg-background/30'}`}
                        >
                            <input type="file" accept="video/mp4,video/quicktime" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
                            <UploadCloud className={`w-10 h-10 mb-3 ${localFile ? 'text-mimaros-blue' : 'text-textDim'}`} />
                            {localFile ? (
                                <p className="text-white font-bold">{localFile.name}</p>
                            ) : (
                                <>
                                    <p className="text-white font-bold mb-1">Lokale Datei hochladen</p>
                                    <p className="text-sm text-textDim">Drag & Drop oder hier klicken (MP4, MOV)</p>
                                </>
                            )}
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="h-px bg-borderGlass flex-1" />
                            <span className="text-xs font-bold text-textDim uppercase">ODER YOUTUBE</span>
                            <div className="h-px bg-borderGlass flex-1" />
                        </div>

                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <Play className="h-5 w-5 text-textDim" />
                                </div>
                                <input 
                                type="text" 
                                value={youtubeUrl}
                                onChange={(e) => {
                                    setYoutubeUrl(e.target.value); 
                                    setLocalFile(null);
                                    setVideoMetadata(null);
                                }}
                                placeholder="YouTube-Link einfügen (z.B. https://youtube.com/watch?v=...)" 
                                className="block w-full pl-12 pr-4 py-4 border border-borderGlass rounded-xl focus:outline-none focus:ring-1 focus:ring-mimaros-blue bg-background/50 text-white placeholder-textDim transition-all"
                                />
                            </div>
                            {youtubeUrl && (
                                <button 
                                    onClick={() => fetchVideoInfo(youtubeUrl)}
                                    disabled={isFetchingMetadata}
                                    className="px-6 py-4 bg-mimaros-blue text-white rounded-xl font-bold shadow-blue-glow hover:bg-mimaros-blue/90 transition-all disabled:opacity-50 flex items-center gap-2"
                                >
                                    {isFetchingMetadata ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
                                    Laden
                                </button>
                            )}
                        </div>

                        {/* Metadata & Interactive Range Trimmer UI */}
                        {(videoMetadata || localFile) && (
                            <div className="bg-panel/60 border border-borderGlass rounded-2xl p-5 space-y-4 shadow-glass backdrop-blur-md">
                                <div className="flex items-center gap-4 border-b border-borderGlass/50 pb-3">
                                    <Scissors className="w-5 h-5 text-mimaros-blue shrink-0" />
                                    <div className="flex-1">
                                        <h4 className="text-white font-bold text-sm">Manueller Video-Trimmer & Smart Jump-Cuts</h4>
                                        <p className="text-textDim text-xs">Wähle den exakten Zeitbereich, der analysiert & per Silence-Removal verdichtet werden soll.</p>
                                    </div>
                                    <span className="bg-mimaros-blue/10 text-mimaros-blue text-xs font-bold px-3 py-1 rounded-full border border-mimaros-blue/20">
                                        {trimStart !== '' && trimEnd !== '' ? `${Math.max(0, Number(trimEnd) - Number(trimStart))}s Bereich` : 'Ganzes Video'}
                                    </span>
                                </div>

                                {videoMetadata && (
                                    <div className="flex items-center gap-4 bg-background/40 p-3 rounded-xl border border-borderGlass/30">
                                        {videoMetadata.thumbnail && (
                                            <img src={videoMetadata.thumbnail} alt="Thumbnail" className="w-20 h-auto rounded-lg object-cover" />
                                        )}
                                        <div className="flex-1 min-w-0">
                                            <p className="text-white font-bold text-sm truncate">{videoMetadata.title}</p>
                                            <p className="text-textDim text-xs mt-0.5">Gesamtdauer: {Math.floor(videoMetadata.duration / 60)}:{String(Math.floor(videoMetadata.duration % 60)).padStart(2, '0')} min</p>
                                        </div>
                                    </div>
                                )}

                                {/* Dual Range Slider Controls */}
                                <div className="space-y-3 bg-background/50 p-4 rounded-xl border border-borderGlass/40">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <div className="flex justify-between text-xs mb-1">
                                                <span className="font-bold text-textDim uppercase">Startzeit</span>
                                                <span className="font-mono text-mimaros-blue font-bold">
                                                    {trimStart !== '' ? `${Math.floor(Number(trimStart) / 60)}:${String(Math.floor(Number(trimStart) % 60)).padStart(2, '0')}` : '0:00'}
                                                </span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min={0}
                                                max={videoMetadata ? videoMetadata.duration : 600}
                                                value={trimStart !== '' ? trimStart : 0} 
                                                onChange={(e) => {
                                                    const val = parseInt(e.target.value) || 0;
                                                    setTrimStart(val);
                                                    if (trimEnd !== '' && val >= Number(trimEnd)) {
                                                        setTrimEnd(val + 30);
                                                    }
                                                }}
                                                className="w-full accent-mimaros-blue cursor-pointer h-2 bg-panel rounded-lg"
                                            />
                                        </div>

                                        <div>
                                            <div className="flex justify-between text-xs mb-1">
                                                <span className="font-bold text-textDim uppercase">Endzeit</span>
                                                <span className="font-mono text-mimaros-gold font-bold">
                                                    {trimEnd !== '' ? `${Math.floor(Number(trimEnd) / 60)}:${String(Math.floor(Number(trimEnd) % 60)).padStart(2, '0')}` : (videoMetadata ? `${Math.floor(videoMetadata.duration / 60)}:${String(Math.floor(videoMetadata.duration % 60)).padStart(2, '0')}` : 'Max')}
                                                </span>
                                            </div>
                                            <input 
                                                type="range" 
                                                min={0}
                                                max={videoMetadata ? videoMetadata.duration : 600}
                                                value={trimEnd !== '' ? trimEnd : (videoMetadata ? videoMetadata.duration : 600)} 
                                                onChange={(e) => {
                                                    const val = parseInt(e.target.value) || 0;
                                                    setTrimEnd(val);
                                                }}
                                                className="w-full accent-mimaros-gold cursor-pointer h-2 bg-panel rounded-lg"
                                            />
                                        </div>
                                    </div>

                                    {/* Direct Numeric Inputs */}
                                    <div className="flex gap-4 pt-2">
                                        <div className="flex-1">
                                            <label className="block text-[10px] font-bold text-textDim uppercase mb-1">Start (Sekunden)</label>
                                            <input 
                                                type="number" 
                                                value={trimStart} 
                                                placeholder="z.B. 15"
                                                onChange={(e) => setTrimStart(e.target.value ? parseInt(e.target.value) : '')}
                                                className="w-full bg-panel border border-borderGlass rounded-lg p-2 text-white text-xs font-mono"
                                            />
                                        </div>
                                        <div className="flex-1">
                                            <label className="block text-[10px] font-bold text-textDim uppercase mb-1">Ende (Sekunden)</label>
                                            <input 
                                                type="number" 
                                                value={trimEnd} 
                                                placeholder="z.B. 75"
                                                onChange={(e) => setTrimEnd(e.target.value ? parseInt(e.target.value) : '')}
                                                className="w-full bg-panel border border-borderGlass rounded-lg p-2 text-white text-xs font-mono"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="bg-background/40 p-6 rounded-2xl border border-borderGlass space-y-4">
                        <h3 className="font-bold text-white flex items-center gap-2"><Menu className="w-5 h-5 text-mimaros-blue"/> Sequenz Timeline</h3>
                        <p className="text-sm text-textDim">Füge Clips in der Reihenfolge hinzu, in der sie aneinandergehängt werden sollen (z.B. Hook als erstes, dann Hauptteil).</p>
                        
                        <div className="flex gap-4 items-center">
                            <button onClick={() => fileInputRef.current?.click()} className="px-4 py-2 bg-panel border border-borderGlass rounded-lg text-sm text-white hover:border-mimaros-blue transition-all flex items-center gap-2">
                                <UploadCloud className="w-4 h-4" /> Lokal
                            </button>
                            <input type="file" accept="video/mp4,video/quicktime" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
                            
                            <div className="flex-1 flex gap-2">
                                <input 
                                    type="text" 
                                    value={youtubeUrl}
                                    onChange={(e) => setYoutubeUrl(e.target.value)}
                                    placeholder="YouTube-Link..." 
                                    className="flex-1 px-4 py-2 border border-borderGlass rounded-lg focus:outline-none focus:ring-1 focus:ring-mimaros-blue bg-background/50 text-white placeholder-textDim text-sm"
                                />
                                <button onClick={addYoutubeToSequence} className="px-4 py-2 bg-panel border border-borderGlass rounded-lg text-sm text-white hover:border-mimaros-blue transition-all flex items-center gap-2">
                                    <Play className="w-4 h-4" /> Hinzufügen
                                </button>
                            </div>
                        </div>
                        
                        <div className="space-y-2 mt-4 max-h-60 overflow-y-auto pr-2">
                            {sequence.length === 0 ? (
                                <div className="text-center p-8 border border-dashed border-borderGlass rounded-xl text-textDim text-sm">
                                    Keine Clips in der Sequenz. Füge welche hinzu!
                                </div>
                            ) : (
                                sequence.map((item, index) => (
                                    <div key={item.id} className="flex items-center gap-3 bg-panel p-3 rounded-xl border border-borderGlass group">
                                        <div className="flex flex-col">
                                            <button onClick={() => moveSequenceItem(index, 'up')} disabled={index===0} className="text-textDim hover:text-white disabled:opacity-30"><ChevronUp className="w-5 h-5"/></button>
                                            <button onClick={() => moveSequenceItem(index, 'down')} disabled={index===sequence.length-1} className="text-textDim hover:text-white disabled:opacity-30"><ChevronDown className="w-5 h-5"/></button>
                                        </div>
                                        <div className="w-10 h-10 bg-background/50 rounded flex items-center justify-center">
                                            <span className="text-mimaros-blue font-bold">{index + 1}</span>
                                        </div>
                                        <div className="flex-1 truncate">
                                            <p className="text-white text-sm font-bold truncate">{item.name}</p>
                                            <p className="text-xs text-textDim uppercase">{item.type}</p>
                                        </div>
                                        <button onClick={() => removeSequenceItem(index)} className="p-2 text-red-500/50 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all">
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* SETTINGS & PREVIEW GRID */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-background/40 p-6 rounded-2xl border border-borderGlass">
                    
                    {/* Left: General Settings */}
                    <div className="col-span-2 space-y-6">
                        <div>
                            <h3 className="font-bold text-white mb-4 flex items-center gap-2"><Settings className="w-4 h-4 text-mimaros-blue"/> Grundeinstellungen</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Video Sprache</label>
                                    <select value={videoLang} onChange={(e) => setVideoLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                        <option value="auto">Auto-Detect</option>
                                        <option value="de">Deutsch</option>
                                        <option value="en">Englisch</option>
                                        <option value="es">Spanisch</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Untertitel Zielsprache</label>
                                    <select value={subtitleLang} onChange={(e) => setSubtitleLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                        <option value="auto">Wie Video</option>
                                        <option value="de">Deutsch</option>
                                        <option value="en">Englisch</option>
                                        <option value="es">Spanisch</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Clip Länge</label>
                                    <select value={clipLength} onChange={(e) => setClipLength(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                        <option value="auto">Auto (30-60s)</option>
                                        <option value="short">Viral Hook (&lt;30s)</option>
                                        <option value="standard">Standard (30-60s)</option>
                                        <option value="extended">Extended (60-90s)</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Auflösung</label>
                                    <select value={resolution} onChange={(e) => setResolution(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                        <option value="720p">720p (Schnell)</option>
                                        <option value="1080p">1080p (HQ)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {/* Accordion 1: Basis-Einstellungen */}
                            <div className="border border-borderGlass rounded-2xl overflow-hidden bg-panel/20 backdrop-blur-md">
                                <button 
                                    type="button"
                                    onClick={() => setActiveAccordion(activeAccordion === 'basic' ? null : 'basic')}
                                    className="w-full px-6 py-4 flex items-center justify-between text-left font-bold text-white bg-panel/30 hover:bg-panel/50 transition-all focus:outline-none"
                                >
                                    <span className="flex items-center gap-2">
                                        <Settings className="w-4 h-4 text-mimaros-blue" />
                                        Basis-Einstellungen
                                    </span>
                                    <ChevronDown className={`w-4 h-4 text-textDim transition-transform duration-300 ${activeAccordion === 'basic' ? 'rotate-180' : ''}`} />
                                </button>
                                {activeAccordion === 'basic' && (
                                    <div className="p-6 bg-background/10 space-y-4 border-t border-borderGlass/50">
                                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Video Sprache</label>
                                                <select value={videoLang} onChange={(e) => setVideoLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                                    <option value="auto">Auto Erkennung</option>
                                                    <option value="de">Deutsch</option>
                                                    <option value="en">Englisch</option>
                                                    <option value="es">Spanisch</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Untertitel Übersetzung</label>
                                                <select value={subtitleLang} onChange={(e) => setSubtitleLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                                    <option value="auto">Wie Video</option>
                                                    <option value="de">Deutsch</option>
                                                    <option value="en">Englisch</option>
                                                    <option value="es">Spanisch</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Clip Länge</label>
                                                <select value={clipLength} onChange={(e) => setClipLength(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                                    <option value="auto">Auto (30-60s)</option>
                                                    <option value="short">Viral Hook (&lt;30s)</option>
                                                    <option value="standard">Standard (30-60s)</option>
                                                    <option value="extended">Extended (60-90s)</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Auflösung</label>
                                                <select value={resolution} onChange={(e) => setResolution(e.target.value)} className="w-full bg-panel border border-borderGlass p-2 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue">
                                                    <option value="720p">720p (Schnell)</option>
                                                    <option value="1080p">1080p (HQ)</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div className="pt-4 border-t border-borderGlass/20 space-y-3">
                                            <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Video-Titel / Skript-Text</label>
                                            <input 
                                                type="text" 
                                                value={hookHeader}
                                                onChange={(e) => setHookHeader(e.target.value)}
                                                className="w-full bg-background/50 border border-borderGlass rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-mimaros-blue/50 transition-colors"
                                                placeholder="z.B. DIESEN FEHLER VERMEIDEN"
                                            />

                                            {/* KI-Voiceover Panel */}
                                            <div className="bg-panel/40 border border-borderGlass/40 rounded-xl p-3 space-y-3">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Volume2 className="w-4 h-4 text-mimaros-blue" />
                                                        <span className="text-xs font-bold text-white">KI-Voiceover Sprecherstimme</span>
                                                    </div>
                                                    <select 
                                                        value={selectedVoice} 
                                                        onChange={(e) => setSelectedVoice(e.target.value)}
                                                        className="bg-background/80 border border-borderGlass text-xs text-white p-1.5 rounded-lg outline-none"
                                                    >
                                                        <option value="alloy">Alloy (Dynamisch)</option>
                                                        <option value="echo">Echo (Klar & Neutral)</option>
                                                        <option value="nova">Nova (Weiblich/Sanft)</option>
                                                        <option value="onyx">Onyx (Tief & Markant)</option>
                                                    </select>
                                                </div>

                                                <button
                                                    type="button"
                                                    onClick={handleGenerateVoiceover}
                                                    disabled={isGeneratingVoiceover || !hookHeader}
                                                    className="w-full py-2.5 px-4 bg-mimaros-blue/20 hover:bg-mimaros-blue/30 border border-mimaros-blue/40 text-mimaros-blue font-bold text-xs rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                                                >
                                                    {isGeneratingVoiceover ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
                                                    {isGeneratingVoiceover ? "Generiere KI-Voiceover..." : "🎙️ Als KI-Voiceover generieren"}
                                                </button>

                                                {voiceoverUrl && (
                                                    <div className="pt-2">
                                                        <p className="text-[10px] text-mimaros-gold font-bold mb-1 font-mono">✅ Vorschau der KI-Audiospur:</p>
                                                        <audio src={voiceoverUrl} controls className="w-full h-9 rounded-lg bg-background" />
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex items-center justify-between pt-4 border-t border-borderGlass/20">
                                            <span className="text-xs font-bold text-textDim font-sans">Master CI-Template anwenden</span>
                                            <button 
                                                type="button"
                                                onClick={() => setUseMasterCi(!useMasterCi)}
                                                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${useMasterCi ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background/80 border border-borderGlass'}`}
                                            >
                                                <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${useMasterCi ? 'translate-x-5' : 'translate-x-0'}`} />
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Accordion 2: Sichtbarkeit & CI-Design */}
                            {useMasterCi && (
                                <div className="border border-borderGlass rounded-2xl overflow-hidden bg-panel/20 backdrop-blur-md">
                                    <button 
                                        type="button"
                                        onClick={() => setActiveAccordion(activeAccordion === 'ci' ? null : 'ci')}
                                        className="w-full px-6 py-4 flex items-center justify-between text-left font-bold text-white bg-panel/30 hover:bg-panel/50 transition-all focus:outline-none"
                                    >
                                        <span className="flex items-center gap-2">
                                            <Layout className="w-4 h-4 text-mimaros-blue" />
                                            Sichtbarkeit & CI-Design
                                        </span>
                                        <ChevronDown className={`w-4 h-4 text-textDim transition-transform duration-300 ${activeAccordion === 'ci' ? 'rotate-180' : ''}`} />
                                    </button>
                                    {activeAccordion === 'ci' && (
                                        <div className="p-6 bg-background/10 space-y-6 border-t border-borderGlass/50">
                                            {/* Modular Visibility Toggles */}
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-3">Sichtbare Elemente</label>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                                    <div className="flex items-center justify-between p-3 bg-background/30 border border-borderGlass rounded-xl">
                                                        <span className="text-xs font-bold text-white">Titel</span>
                                                        <button 
                                                            type="button"
                                                            onClick={() => setShowTitle(!showTitle)}
                                                            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showTitle ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background/50 border border-borderGlass'}`}
                                                        >
                                                            <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showTitle ? 'translate-x-4' : 'translate-x-0'}`} />
                                                        </button>
                                                    </div>
                                                    <div className="flex items-center justify-between p-3 bg-background/30 border border-borderGlass rounded-xl">
                                                        <span className="text-xs font-bold text-white">Logo</span>
                                                        <button 
                                                            type="button"
                                                            onClick={() => setShowLogo(!showLogo)}
                                                            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showLogo ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background/50 border border-borderGlass'}`}
                                                        >
                                                            <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showLogo ? 'translate-x-4' : 'translate-x-0'}`} />
                                                        </button>
                                                    </div>
                                                    <div className="flex items-center justify-between p-3 bg-background/30 border border-borderGlass rounded-xl">
                                                        <span className="text-xs font-bold text-white">Untertitel</span>
                                                        <button 
                                                            type="button"
                                                            onClick={() => setShowSubtitles(!showSubtitles)}
                                                            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showSubtitles ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background/50 border border-borderGlass'}`}
                                                        >
                                                            <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showSubtitles ? 'translate-x-4' : 'translate-x-0'}`} />
                                                        </button>
                                                    </div>
                                                    <div className="flex items-center justify-between p-3 bg-background/30 border border-borderGlass rounded-xl">
                                                        <span className="text-xs font-bold text-white">Follow CTA</span>
                                                        <button 
                                                            type="button"
                                                            onClick={() => setShowCTA(!showCTA)}
                                                            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showCTA ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background/50 border border-borderGlass'}`}
                                                        >
                                                            <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showCTA ? 'translate-x-4' : 'translate-x-0'}`} />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Colors */}
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">CI Hauptfarbe (Rahmen & Akzente)</label>
                                                    <div className="flex items-center gap-3 bg-background/50 border border-borderGlass rounded-xl p-2">
                                                        <input 
                                                            type="color" 
                                                            value={primaryColor}
                                                            onChange={(e) => setPrimaryColor(e.target.value)}
                                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-0"
                                                        />
                                                        <input 
                                                            type="text" 
                                                            value={primaryColor}
                                                            onChange={(e) => setPrimaryColor(e.target.value)}
                                                            className="bg-transparent text-white text-sm w-full focus:outline-none uppercase"
                                                        />
                                                    </div>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">CI Textfarbe (Untertitel)</label>
                                                    <div className="flex items-center gap-3 bg-background/50 border border-borderGlass rounded-xl p-2">
                                                        <input 
                                                            type="color" 
                                                            value={textColor}
                                                            onChange={(e) => setTextColor(e.target.value)}
                                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-0"
                                                        />
                                                        <input 
                                                            type="text" 
                                                            value={textColor}
                                                            onChange={(e) => setTextColor(e.target.value)}
                                                            className="bg-transparent text-white text-sm w-full focus:outline-none uppercase"
                                                        />
                                                    </div>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Highlight-Farbe (Aktuelles Wort)</label>
                                                    <div className="flex items-center gap-3 bg-background/50 border border-borderGlass rounded-xl p-2">
                                                        <input 
                                                            type="color" 
                                                            value={highlightColor}
                                                            onChange={(e) => setHighlightColor(e.target.value)}
                                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-0"
                                                        />
                                                        <input 
                                                            type="text" 
                                                            value={highlightColor}
                                                            onChange={(e) => setHighlightColor(e.target.value)}
                                                            className="bg-transparent text-white text-sm w-full focus:outline-none uppercase"
                                                        />
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Logo Upload & position */}
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Logo Upload</label>
                                                    <label className="flex items-center justify-center w-full h-12 px-4 transition bg-background/50 border-2 border-borderGlass border-dashed rounded-xl appearance-none cursor-pointer hover:border-mimaros-blue/50 focus:outline-none">
                                                        <span className="flex items-center space-x-2">
                                                            <UploadCloud className="w-5 h-5 text-textDim" />
                                                            <span className="font-medium text-sm text-textDim truncate max-w-[180px]">
                                                                {logoUploading ? 'Lade hoch...' : (logoFile ? logoFile.name : 'Logo (.png)')}
                                                            </span>
                                                        </span>
                                                        <input type="file" name="file_upload" className="hidden" accept=".png,.jpg,.jpeg" onChange={handleLogoUpload} />
                                                    </label>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Logo Position</label>
                                                    <select 
                                                        value={logoPosition}
                                                        onChange={(e) => setLogoPosition(e.target.value)}
                                                        className="w-full bg-background/50 border border-borderGlass rounded-xl px-4 h-12 text-sm text-white focus:outline-none focus:border-mimaros-blue/50"
                                                    >
                                                        <option value="top-left">Oben Links</option>
                                                        <option value="top-right">Oben Rechts</option>
                                                    </select>
                                                </div>
                                            </div>

                                            {/* Watermark */}
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Watermark Text</label>
                                                <input 
                                                    type="text" 
                                                    value={globalSubtitleConfig.watermark_text}
                                                    onChange={(e) => setGlobalSubtitleConfig({...globalSubtitleConfig, watermark_text: e.target.value})}
                                                    className="w-full bg-background/50 border border-borderGlass rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-mimaros-blue/50 transition-colors"
                                                    placeholder="z.B. @deinkanal"
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Accordion 3: Untertitel Design-Stile */}
                            {useMasterCi && (
                                <div className="border border-borderGlass rounded-2xl overflow-hidden bg-panel/20 backdrop-blur-md">
                                    <button 
                                        type="button"
                                        onClick={() => setActiveAccordion(activeAccordion === 'design' ? null : 'design')}
                                        className="w-full px-6 py-4 flex items-center justify-between text-left font-bold text-white bg-panel/30 hover:bg-panel/50 transition-all focus:outline-none"
                                    >
                                        <span className="flex items-center gap-2">
                                            <Subtitles className="w-4 h-4 text-mimaros-blue" />
                                            Untertitel Design-Stile
                                        </span>
                                        <ChevronDown className={`w-4 h-4 text-textDim transition-transform duration-300 ${activeAccordion === 'design' ? 'rotate-180' : ''}`} />
                                    </button>
                                    {activeAccordion === 'design' && (
                                        <div className="p-6 bg-background/10 space-y-6 border-t border-borderGlass/50">
                                            {/* Horizontal Templates Slider (CapCut/TikTok style) */}
                                            <div>
                                                <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-3">Untertitel Vorlagen</label>
                                                <style dangerouslySetInnerHTML={{__html: `
                                                  @keyframes anim-karaoke-1 { 0%, 100% { color: #ffffff; transform: scale(1); } 33% { color: ${highlightColor}; transform: scale(1.15); filter: drop-shadow(0 0 6px ${highlightColor}); } }
                                                  @keyframes anim-karaoke-2 { 0%, 33%, 100% { color: #ffffff; transform: scale(1); } 66% { color: ${highlightColor}; transform: scale(1.15); filter: drop-shadow(0 0 6px ${highlightColor}); } }
                                                  @keyframes anim-karaoke-3 { 0%, 66%, 100% { color: #ffffff; transform: scale(1); } 95% { color: ${highlightColor}; transform: scale(1.15); filter: drop-shadow(0 0 6px ${highlightColor}); } }
                                                  
                                                  @keyframes anim-pop-bounce { 0%, 100% { opacity: 0.2; transform: scale(0.4); } 20%, 80% { opacity: 1; transform: scale(1.2); } 40%, 60% { transform: scale(1.0); } }
                                                  
                                                  @keyframes anim-box-slide {
                                                    0%, 100% { transform: translateX(-24px); background-color: ${primaryColor}; opacity: 0.9; }
                                                    50% { transform: translateX(24px); background-color: ${highlightColor}; opacity: 0.9; }
                                                  }
                                                  
                                                  @keyframes anim-hormozi-pulse { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-3px) scale(1.08); } }
                                                  
                                                  @keyframes anim-clean-fade { 0%, 100% { opacity: 0.2; transform: translateY(2px); } 50% { opacity: 1; transform: translateY(0); } }
                                                  
                                                  .anim-k-1 { animation: anim-karaoke-1 1.8s infinite inline-block; }
                                                  .anim-k-2 { animation: anim-karaoke-2 1.8s infinite inline-block; }
                                                  .anim-k-3 { animation: anim-karaoke-3 1.8s infinite inline-block; }
                                                  .anim-pop-b { animation: anim-pop-bounce 1.6s infinite ease-out; }
                                                  .anim-h-pulse { animation: anim-hormozi-pulse 1s infinite ease-in-out; }
                                                  .anim-c-fade { animation: anim-clean-fade 2s infinite ease-in-out; }
                                                `}} />
                                                <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-mimaros-blue/20">
                                                    {[
                                                        { id: 'karaoke', name: 'Karaoke Highlight', desc: 'Wort-für-Wort Animation' },
                                                        { id: 'dynamic_box', name: 'Dynamic Box', desc: 'Mitlaufendes Highlight' },
                                                        { id: 'popup_bouncy', name: 'Pop-Up (Bouncy)', desc: 'Ploppender Fokus-Text' },
                                                        { id: 'hormozi', name: 'Hormozi Style', desc: 'Fett, Gelb/Grün 3D' },
                                                        { id: 'mimaros_clean', name: 'mimaros Clean', desc: 'Minimalistischer B2B Stil' }
                                                    ].map(tpl => (
                                                        <button 
                                                            key={tpl.id}
                                                            type="button"
                                                            onClick={() => setGlobalSubtitleConfig({...globalSubtitleConfig, design: tpl.id})}
                                                            className={`relative min-w-[145px] w-[145px] aspect-[9/16] rounded-2xl overflow-hidden border-2 transition-all shrink-0 bg-slate-950 flex flex-col justify-between p-3 select-none ${globalSubtitleConfig.design === tpl.id ? 'border-mimaros-blue shadow-[0_0_20px_rgba(20,174,234,0.4)] scale-[0.98]' : 'border-borderGlass opacity-70 hover:opacity-100 hover:border-white/30'}`}
                                                        >
                                                            {/* Animated Canvas Backdrop */}
                                                            <div className="absolute inset-0 bg-gradient-to-b from-indigo-950/60 via-slate-900/90 to-black z-0 pointer-events-none" />
                                                            <div className="absolute top-2 right-2 flex flex-col gap-1 z-10 opacity-40">
                                                                <div className="w-1.5 h-1.5 rounded-full bg-white" />
                                                                <div className="w-1.5 h-1.5 rounded-full bg-white" />
                                                                <div className="w-1.5 h-1.5 rounded-full bg-white" />
                                                            </div>

                                                            {/* Subtitle Animation Showcase */}
                                                            <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-1 text-center">
                                                                {tpl.id === 'karaoke' && (
                                                                    <div className="text-[11px] font-black text-white tracking-wider leading-snug bg-black/70 px-2 py-1.5 rounded-lg border border-white/10 shadow-xl">
                                                                        <span className="anim-k-1 mr-1">VIRALER</span>
                                                                        <span className="anim-k-2 mr-1">HOOK</span>
                                                                        <span className="anim-k-3">TEXT!</span>
                                                                    </div>
                                                                )}

                                                                {tpl.id === 'dynamic_box' && (
                                                                    <div className="relative text-[11px] font-black text-white tracking-wider px-3 py-1.5 rounded-lg bg-black/70 border border-white/10 shadow-xl overflow-hidden">
                                                                        <span className="relative z-10">DYNAMISCHE BOX</span>
                                                                        <div className="absolute inset-0 rounded-lg z-0" style={{ animation: 'anim-box-slide 2s infinite ease-in-out' }} />
                                                                    </div>
                                                                )}

                                                                {tpl.id === 'popup_bouncy' && (
                                                                    <div className="anim-pop-b text-[15px] font-black text-white uppercase tracking-widest drop-shadow-[0_4px_8px_rgba(0,0,0,0.9)] bg-gradient-to-r from-mimaros-blue to-purple-500 px-3 py-1 rounded-xl shadow-2xl">
                                                                        BOOM!
                                                                    </div>
                                                                )}

                                                                {tpl.id === 'hormozi' && (
                                                                    <div className="anim-h-pulse text-center font-black uppercase leading-none drop-shadow-[0_3px_6px_rgba(0,0,0,0.9)] bg-black/60 p-2 rounded-xl border border-yellow-400/30">
                                                                        <div className="text-[13px] text-[#FFFF00] tracking-tight">ALEX STYLE</div>
                                                                        <div className="text-[11px] text-[#00FF00] tracking-widest mt-0.5">MAX IMPACT</div>
                                                                    </div>
                                                                )}

                                                                {tpl.id === 'mimaros_clean' && (
                                                                    <div className="text-[8px] font-medium text-white text-center leading-tight anim-fade px-2 font-sans opacity-95 drop-shadow-[0_1px_2px_rgba(0,0,0,0.6)]">
                                                                        Seriöse B2B<br/>Botschaft
                                                                    </div>
                                                                )}
                                                            </div>
                                                            
                                                            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/95 via-black/40 to-transparent flex flex-col justify-end p-2.5 text-left z-20">
                                                                <span className="text-xs font-bold text-white leading-tight">{tpl.name}</span>
                                                                <span className="text-[8px] text-textDim truncate">{tpl.desc}</span>
                                                            </div>
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Fonts & CTA options */}
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Typografie (Schriftart)</label>
                                                    <select 
                                                        value={fontName}
                                                        onChange={(e) => setFontName(e.target.value)}
                                                        className="w-full bg-background/50 border border-borderGlass rounded-xl px-3 h-12 text-sm text-white focus:outline-none focus:border-mimaros-blue/50"
                                                    >
                                                        <option value="Work Sans">Work Sans (Modern)</option>
                                                        <option value="Lato">Lato (Sleek)</option>
                                                        <option value="Montserrat">Montserrat Black (Thick CI)</option>
                                                        <option value="Oswald">Oswald (Compact Bold)</option>
                                                        <option value="Anton">Anton (Extra Bold & Heavy)</option>
                                                        <option value="Impact">Impact (Classic)</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Call-to-Action (CTA)</label>
                                                    <select 
                                                        value={globalSubtitleConfig.cta}
                                                        onChange={(e) => setGlobalSubtitleConfig({...globalSubtitleConfig, cta: e.target.value})}
                                                        className="w-full bg-background/50 border border-borderGlass rounded-xl px-3 h-12 text-sm text-white focus:outline-none focus:border-mimaros-blue/50"
                                                    >
                                                        <option value="none">Kein CTA</option>
                                                        <option value="follow">Folgen für mehr</option>
                                                        <option value="subscribe">Jetzt abonnieren</option>
                                                        <option value="more">Mehr Videos</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {!useMasterCi && (
                                <div className="p-4 bg-background/50 border border-borderGlass rounded-xl">
                                    <p className="text-sm text-textDim">Das Master CI-Template ist deaktiviert. Es wird ein absolutes Basis-Design für Untertitel angewendet (ohne Call-to-Action und ohne Branding).</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Live Preview */}
                    <div className="col-span-1 flex flex-col items-center justify-center">
                        <label className="block text-xs font-bold text-textDim uppercase mb-3 w-full text-center flex items-center justify-center gap-1.5">
                            Live Style-Vorschau
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-bold bg-mimaros-blue/10 text-mimaros-blue border border-mimaros-blue/20 uppercase tracking-wider">Auto</span>
                        </label>
                        <div className="w-full max-w-[220px] bg-background rounded-2xl overflow-hidden shadow-2xl flex items-center justify-center aspect-[9/16] relative bg-cover bg-center transition-all duration-300" style={{
                            backgroundImage: "url('https://images.unsplash.com/photo-1616469829941-c7200edec809?auto=format&fit=crop&w=400&q=80')",
                            border: useMasterCi ? `4px solid ${primaryColor}` : '1px solid var(--borderGlass)'
                        }}>
                            {isGlobalPreviewing && (
                                <div className="absolute inset-0 bg-black/80 backdrop-blur-sm z-30 flex flex-col items-center justify-center space-y-2">
                                    <Loader2 className="animate-spin w-8 h-8 text-mimaros-blue" />
                                    <span className="text-[10px] text-textDim font-sans">Rendere Vorschau...</span>
                                </div>
                            )}
                            {globalPreviewUrl ? (
                                <video src={globalPreviewUrl} autoPlay loop muted playsInline className="absolute inset-0 w-full h-full object-cover z-20" />
                            ) : useMasterCi ? (
                                <>
                                     {showTitle ? (
                                         <div className="absolute top-0 left-0 right-0 z-15 bg-[#0b192c]/80 flex flex-col items-center justify-center pt-2 pb-2.5 border-b-2" style={{ borderColor: primaryColor }}>
                                             {/* Watermark text at the very top (Ebene 1) */}
                                             <div className="text-[7px] text-white/90 font-medium tracking-wider leading-none mb-1 font-sans">
                                                 {globalSubtitleConfig.watermark_text || "mimaros.eu"}
                                             </div>
                                             {/* Title / Hook (Ebene 2) */}
                                             <div className="text-[10px] text-white font-heading font-bold uppercase tracking-wider text-center px-6 max-w-[90%] break-words whitespace-normal leading-tight">
                                                 {hookHeader || "DEIN VIRALER VIDEO TITEL"}
                                             </div>
                                         </div>
                                     ) : (
                                         globalSubtitleConfig.watermark_text && (
                                             <div className="absolute top-4 left-0 right-0 flex justify-center z-10">
                                                 <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center gap-2">
                                                     <span className="text-white text-[8px] font-medium tracking-wide font-sans">
                                                         {globalSubtitleConfig.watermark_text}
                                                     </span>
                                                 </div>
                                             </div>
                                         )
                                     )}
                                     {/* Logo position overlays top-left or top-right */}
                                     {logoPreview && showLogo && (
                                         <div className="absolute w-7 h-7 rounded bg-white/10 backdrop-blur-sm z-20" style={{
                                             top: showTitle ? '8px' : '16px',
                                             left: logoPosition === 'top-left' ? '8px' : 'auto',
                                             right: logoPosition === 'top-right' ? '8px' : 'auto',
                                             backgroundImage: `url(${logoPreview})`,
                                             backgroundSize: 'contain',
                                             backgroundPosition: 'center',
                                             backgroundRepeat: 'no-repeat'
                                         }}></div>
                                     )}
                                     
                                     {showSubtitles && (
                                         <>
                                             {/* Full-width bottom backdrop banner */}
                                             <div className="absolute bottom-0 left-0 right-0 top-[270px] bg-[#0b192c]/90 z-5 border-t border-white/5"></div>
                                             
                                             <div className="absolute bottom-12 left-0 right-0 text-center font-bold text-[10px] z-10" style={{ color: textColor, fontFamily: fontName }}>
                                                 DYNAMISCHE <span style={{ color: highlightColor, fontSize: '12px' }}>UNTERTITEL</span>
                                                 <br/><span className="text-[8px] font-normal opacity-80" style={{ fontFamily: fontName }}>Beispieltext</span>
                                             </div>
                                         </>
                                     )}
                                     
                                    <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                                        {globalSubtitleConfig.cta !== 'none' && showCTA && (
                                            <button className="text-white text-[14px] font-bold px-8 py-3.5 rounded-full shadow-[0_0_15px_rgba(0,0,0,0.5)] uppercase pointer-events-auto" style={{ backgroundColor: primaryColor, fontFamily: fontName }}>
                                                {globalSubtitleConfig.cta === 'follow' ? 'FOLGEN FÜR MEHR' : globalSubtitleConfig.cta === 'subscribe' ? 'JETZT ABONNIEREN' : globalSubtitleConfig.cta === 'more' ? 'MEHR VIDEOS' : 'CTA TEXT'}
                                            </button>
                                        )}
                                    </div>
                                </>
                            ) : (
                                <div className="absolute bottom-12 left-0 right-0 text-center text-white font-bold text-xs bg-black/50 mx-4 p-1 z-10" style={{ fontFamily: fontName }}>
                                    STANDARD UNTERTITEL
                                </div>
                            )}
                        </div>
                        <div className="mt-3 text-[10px] text-textDim flex items-center gap-1.5">
                            <span className={`w-1.5 h-1.5 rounded-full ${isGlobalPreviewing ? 'bg-mimaros-gold animate-pulse' : 'bg-green-500'}`} />
                            {isGlobalPreviewing ? 'Aktualisiere Vorschau...' : 'Vorschau bereit'}
                        </div>
                    </div>
                </div>

                <button 
                    onClick={handleProcess}
                    disabled={isProcessing || (!youtubeUrl && !localFile)}
                    className="w-full bg-mimaros-blue hover:bg-[#42c6ff] disabled:opacity-50 text-white px-8 py-4 rounded-xl font-heading font-bold text-lg transition-all shadow-blue-glow flex items-center justify-center gap-2"
                >
                    {isProcessing ? <Loader2 className="animate-spin w-6 h-6" /> : <><Sparkles className="w-6 h-6"/> Shorts jetzt generieren</>}
                </button>

                {statusMessage && (
                <div className="w-full text-sm text-mimaros-gold font-medium text-center bg-mimaros-gold/10 border border-mimaros-gold/20 py-3 rounded-lg flex items-center justify-center gap-2">
                    <Loader2 className="animate-spin w-4 h-4" /> {statusMessage}
                </div>
                )}
            </div>
          </div>

          {clips.length > 0 && (
              <div className="space-y-6 pb-20">
                  <h3 className="font-heading font-bold text-2xl text-white">Generierte Clips ({clips.length})</h3>
                  {clips.map((clip, idx) => (
                      <div key={clip.id} className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-6 flex flex-col md:flex-row gap-8 items-start">
                          
                          <div className="w-full md:w-[240px] shrink-0 relative bg-background rounded-xl overflow-hidden shadow-2xl border border-borderGlass flex items-center justify-center aspect-[9/16]">
                              {clip.videoUrl ? (
                                  <video src={clip.videoUrl.startsWith('/') ? API_BASE + clip.videoUrl : clip.videoUrl} controls className="absolute inset-0 w-full h-full object-cover z-20" />
                              ) : (
                                  <div className="text-textDim text-sm">Video lädt...</div>
                              )}
                          </div>

                          <div className="flex-1 flex flex-col gap-4">
                              <div className="flex justify-between items-start">
                                  <h4 className="font-heading font-bold text-xl text-white">#{idx+1} {clip.title}</h4>
                                  <div className="flex flex-col items-center bg-mimaros-blue/10 border border-mimaros-blue/30 rounded-xl px-4 py-2">
                                      <span className="flex items-center gap-1 text-mimaros-gold font-bold text-xs uppercase tracking-wider"><Flame className="w-3 h-3"/> Viral Score</span>
                                      <span className="text-2xl font-black font-heading text-white">{clip.viralScore}<span className="text-sm text-textDim">/100</span></span>
                                  </div>
                              </div>
                              
                              <p className="text-sm text-textDim bg-background/50 p-4 rounded-xl border border-borderGlass leading-relaxed">
                                  {clip.rationale}
                              </p>

                              <div className="mt-auto pt-4 flex gap-3">
                                  <button onClick={() => { 
                                      setSchedulingClip(clip); 
                                      setScheduleForm(prev => ({...prev, caption: clip.social_media_caption || '', platforms: prev.platforms.length ? prev.platforms : ['YouTube Shorts']}));
                                      setShowScheduleModal(true); 
                                  }} className="flex-1 bg-mimaros-blue text-white py-3 rounded-xl font-bold flex justify-center items-center gap-2 hover:bg-[#42c6ff] transition-all shadow-blue-glow text-sm">
                                      <Calendar className="w-4 h-4"/> Einplanen & Posten
                                  </button>
                                  <button className="px-4 bg-background border border-borderGlass hover:border-white text-textDim hover:text-white py-3 rounded-xl font-bold flex justify-center items-center transition-all">
                                      <Download className="w-4 h-4"/>
                                  </button>
                              </div>
                          </div>
                      </div>
                  ))}
              </div>
          )}
      </div>
  );

  const renderCalendar = () => {
      // Map schedules to FullCalendar events
      const events = schedules.map(item => {
          // parse schedule_date which is DD.MM.YYYY
          const parts = item.schedule_date?.split('.') || [];
          let dateStr = item.schedule_date; // fallback
          if(parts.length === 3) {
              dateStr = `${parts[2]}-${parts[1]}-${parts[0]}`;
          }
          return {
              id: item.job_id,
              title: `${item.platforms?.join(', ')} - Post`,
              date: dateStr,
              extendedProps: { caption: item.caption }
          };
      });

      return (
          <div className="flex-1 max-w-5xl mx-auto w-full flex flex-col gap-6">
              <h2 className="font-heading text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                  <Calendar className="w-8 h-8 text-mimaros-blue" /> Content Kalender
              </h2>
              <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass p-4 md:p-6 shadow-glass text-sm" style={{ minHeight: '600px' }}>
                  <FullCalendar
                      plugins={[dayGridPlugin]}
                      initialView="dayGridMonth"
                      events={events}
                      headerToolbar={{
                          left: 'prev,next today',
                          center: 'title',
                          right: 'dayGridMonth,dayGridWeek'
                      }}
                      height="100%"
                      eventContent={(arg) => (
                          <div className="p-1 text-xs truncate overflow-hidden bg-mimaros-blue/20 text-mimaros-blue rounded border border-mimaros-blue/30 w-full" title={arg.event.extendedProps.caption}>
                              <div className="font-bold">{arg.event.title}</div>
                              <div className="truncate opacity-80">{arg.event.extendedProps.caption}</div>
                          </div>
                      )}
                  />
              </div>
          </div>
      );
  };

  const renderHistory = () => (
      <div className="flex-1 max-w-5xl mx-auto w-full flex flex-col gap-6">
          <h2 className="font-heading text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <Video className="w-8 h-8 text-mimaros-blue" /> Meine Videos
          </h2>
          {history.length === 0 ? (
              <div className="bg-panel/40 rounded-2xl border border-borderGlass p-12 flex flex-col items-center justify-center text-textDim">
                  <UploadCloud className="w-12 h-12 mb-4 opacity-50" />
                  <p>Du hast noch keine Videos verarbeitet.</p>
              </div>
          ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {history.map((item, idx) => (
                      <div key={idx} onClick={() => setSelectedProject(item)} className="cursor-pointer bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass overflow-hidden hover:border-mimaros-blue/50 transition-all group">
                          <div className="aspect-[9/16] max-h-[300px] w-full bg-background relative flex items-center justify-center overflow-hidden">
                               {item.thumbnail ? (
                                   <video src={item.thumbnail} className="w-full h-full object-cover opacity-50 group-hover:opacity-100 transition-opacity" muted loop onMouseEnter={(e)=>e.currentTarget.play()} onMouseLeave={(e)=>e.currentTarget.pause()}/>
                               ) : (
                                   <Play className="w-8 h-8 text-textDim" />
                               )}
                          </div>
                          <div className="p-4">
                              <h4 className="font-bold text-white text-lg truncate mb-2">{item.title}</h4>
                              <div className="flex justify-between items-center text-xs text-textDim font-mono">
                                  <span>{item.clips?.length || 0} Clips</span>
                                  <span>ID: {item.job_id.substring(0,8)}</span>
                              </div>
                          </div>
                      </div>
                  ))}
              </div>
          )}
      </div>
  );

  const handleOAuthConnect = async (platform: string) => {
      try {
          const res = await fetch(`${API_BASE}/api/auth/${platform}`, { method: 'POST' });
          if (res.ok) {
              const data = await res.json();
              if (data.auth_url) {
                  window.location.href = data.auth_url;
              } else {
                  alert(data.message || `Erfolgreich mit ${platform} verbunden!`);
              }
          } else {
              const error = await res.json();
              alert(`Fehler: ${error.detail}`);
          }
      } catch (e) {
          console.error(e);
      }
  };

  const renderIntegrations = () => (
      <div className="flex-1 max-w-5xl mx-auto w-full flex flex-col gap-6">
          <h2 className="font-heading text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <Share2 className="w-8 h-8 text-mimaros-blue" /> Verknüpfungen
          </h2>
          <p className="text-textDim mb-4">Verbinde deine Social Media Accounts für Auto-Posting.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-panel/40 p-6 rounded-2xl border border-borderGlass flex items-center justify-between">
                  <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-red-500/20 text-red-500 rounded-xl flex items-center justify-center">
                          <Video className="w-6 h-6" />
                      </div>
                      <div>
                          <h3 className="font-bold text-white">YouTube</h3>
                          <p className={`text-xs ${authStatus.youtube ? 'text-green-400' : 'text-textDim'}`}>
                              Status: {authStatus.youtube ? 'Verbunden' : 'Nicht verbunden'}
                          </p>
                      </div>
                  </div>
                  {authStatus.youtube ? (
                      <button className="bg-green-500/20 text-green-400 px-4 py-2 rounded-lg font-bold text-sm" disabled>Verbunden</button>
                  ) : (
                      <button onClick={() => handleOAuthConnect('youtube')} className="bg-mimaros-blue text-white px-4 py-2 rounded-lg font-bold text-sm hover:bg-[#42c6ff] transition-all">Verbinden</button>
                  )}
              </div>
              
              <div className="bg-panel/40 p-6 rounded-2xl border border-borderGlass flex items-center justify-between">
                  <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-black/40 text-white rounded-xl flex items-center justify-center border border-borderGlass">
                          <Video className="w-6 h-6" />
                      </div>
                      <div>
                          <h3 className="font-bold text-white">TikTok</h3>
                          <p className="text-xs text-textDim">Status: Nicht verbunden</p>
                      </div>
                  </div>
                  <button onClick={() => handleOAuthConnect('tiktok')} className="bg-mimaros-blue text-white px-4 py-2 rounded-lg font-bold text-sm">Verbinden</button>
              </div>
          </div>
      </div>
  );

  return (
    <div className="min-h-screen bg-background text-textMain font-sans flex overflow-hidden selection:bg-mimaros-blue/30 selection:text-white">
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-mimaros-blue/10 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-mimaros-gold/5 blur-[120px] pointer-events-none" />

      {renderSidebar()}

      {/* md:pl-64 shifts main content right on desktop to accommodate the fixed sidebar */}
      <main className="flex-1 flex flex-col relative z-10 overflow-y-auto h-screen md:pl-64">
          <div className="md:hidden flex items-center justify-between p-4 border-b border-borderGlass bg-panel/80 backdrop-blur-xl sticky top-0 z-30">
             <div className="flex items-center gap-2.5">
                 <LogoIcon className="w-9 h-9 shrink-0 drop-shadow-[0_0_10px_rgba(20,174,234,0.4)]" />
                 <div>
                     <h1 className="font-heading font-bold text-base tracking-tight text-white leading-none">mimaros</h1>
                     <span className="text-[9px] font-bold text-mimaros-blue uppercase block mt-0.5">AutoShorts AI</span>
                 </div>
             </div>
             <button onClick={() => setIsMobileMenuOpen(true)} className="text-white p-2">
                 <Menu className="w-6 h-6" />
             </button>
          </div>
          
          {/* Add pb-24 padding bottom for mobile so the bottom navigation doesn't hide content */}
          <div className="p-4 md:p-8 pb-24 md:pb-8">
              {currentView === 'new' && renderNewProject()}
              {currentView === 'history' && renderHistory()}
              {currentView === 'calendar' && renderCalendar()}
              {currentView === 'integrations' && renderIntegrations()}
          </div>
      </main>

      {selectedProject && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <div className="bg-panel border border-borderGlass rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto flex flex-col shadow-2xl relative">
                  <div className="sticky top-0 bg-panel/90 backdrop-blur-md p-4 border-b border-borderGlass flex justify-between items-center z-10">
                      <h2 className="text-xl font-bold font-heading text-white">{selectedProject.title}</h2>
                      <button onClick={() => setSelectedProject(null)} className="text-textDim hover:text-white"><X className="w-6 h-6"/></button>
                  </div>
                  <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                      {selectedProject.clips?.map((clipUrl: string, idx: number) => (
                          <div key={idx} className="flex flex-col gap-4 bg-background/50 rounded-xl p-4 border border-borderGlass">
                              <h3 className="font-bold text-center text-mimaros-gold">Variante {idx + 1}</h3>
                              <video src={clipUrl.startsWith('/') ? API_BASE + clipUrl : clipUrl} controls className="w-full aspect-[9/16] bg-black rounded-lg object-contain" />
                              <button onClick={() => {
                                  setSchedulingClip({ id: 'hist_'+idx, title: `Variante ${idx+1}`, videoUrl: clipUrl, rationale: '' });
                                  setScheduleForm(prev => ({...prev, platforms: ['YouTube Shorts']}));
                                  setShowScheduleModal(true);
                              }} className="w-full bg-mimaros-blue hover:bg-[#42c6ff] text-white font-bold py-2 rounded-lg transition-all text-sm flex items-center justify-center gap-2">
                                  <Calendar className="w-4 h-4" /> Einplanen
                              </button>
                          </div>
                      ))}
                      {!selectedProject.clips || selectedProject.clips.length === 0 && (
                          <p className="text-textDim col-span-3 text-center">Keine Clips für dieses Projekt gefunden.</p>
                      )}
                  </div>
              </div>
          </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
              <div className="bg-panel border border-borderGlass rounded-2xl p-6 w-full max-w-md shadow-2xl relative my-8">
                  <button onClick={() => setShowScheduleModal(false)} className="absolute top-4 right-4 text-textDim hover:text-white"><X className="w-5 h-5" /></button>
                  <h2 className="text-xl font-heading font-bold text-white mb-6 flex items-center gap-2"><Clock className="text-mimaros-blue w-5 h-5"/> Upload planen</h2>
                  <div className="space-y-6">
                      
                      <div>
                          <label className="block text-xs font-bold text-textDim uppercase mb-3">Plattformen (Mehrfachauswahl)</label>
                          <div className="flex flex-wrap gap-3">
                              {['YouTube Shorts', 'TikTok', 'Instagram Reels'].map(plat => (
                                  <label key={plat} className="flex items-center gap-2 bg-background border border-borderGlass px-4 py-2 rounded-xl cursor-pointer hover:border-mimaros-blue/50 transition-all">
                                      <input 
                                        type="checkbox" 
                                        className="accent-mimaros-blue"
                                        checked={scheduleForm.platforms.includes(plat)}
                                        onChange={(e) => {
                                            if (e.target.checked) {
                                                setScheduleForm({...scheduleForm, platforms: [...scheduleForm.platforms, plat]});
                                            } else {
                                                setScheduleForm({...scheduleForm, platforms: scheduleForm.platforms.filter(p => p !== plat)});
                                            }
                                        }}
                                      />
                                      <span className="text-sm font-bold text-white">{plat}</span>
                                  </label>
                              ))}
                          </div>
                      </div>
                      
                      <div>
                          <div className="flex justify-between items-end mb-2">
                            <label className="block text-xs font-bold text-textDim uppercase">Datum & Uhrzeit</label>
                            <button 
                                onClick={() => {
                                    const today = new Date().toISOString().split('T')[0];
                                    setScheduleForm({...scheduleForm, date: today, time: '18:00'});
                                }}
                                className="text-[10px] font-bold text-mimaros-gold bg-mimaros-gold/10 px-2 py-1 rounded hover:bg-mimaros-gold/20 flex items-center gap-1 transition-all"
                            >
                                <Sparkles className="w-3 h-3"/> Beste Uhrzeit (Auto)
                            </button>
                          </div>
                          <div className="flex gap-4">
                              <input type="date" value={scheduleForm.date} onChange={(e) => setScheduleForm({...scheduleForm, date: e.target.value})} className="flex-1 bg-background border border-borderGlass p-3 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue" />
                              <input type="time" value={scheduleForm.time} onChange={(e) => setScheduleForm({...scheduleForm, time: e.target.value})} className="flex-1 bg-background border border-borderGlass p-3 rounded-lg text-sm text-white outline-none focus:border-mimaros-blue" />
                          </div>
                      </div>

                      <div>
                          <label className="block text-xs font-bold text-textDim uppercase mb-2 flex items-center gap-2">
                              <Type className="w-4 h-4"/> Post Beschreibung (KI Generiert)
                          </label>
                          <textarea 
                              placeholder="Füge hier deine Emojis und den Text für TikTok / YouTube ein..."
                              value={scheduleForm.caption} 
                              onChange={(e) => setScheduleForm({...scheduleForm, caption: e.target.value})} 
                              className="w-full h-40 bg-background border border-borderGlass p-4 rounded-xl text-sm text-white outline-none focus:border-mimaros-blue leading-relaxed" 
                          />
                      </div>

                      <button 
                        onClick={handleScheduleSubmit} 
                        disabled={scheduleForm.platforms.length === 0 || !scheduleForm.date || !scheduleForm.time}
                        className="w-full mt-2 disabled:opacity-50 bg-mimaros-blue hover:bg-[#42c6ff] text-white py-3 rounded-xl font-bold font-heading shadow-blue-glow transition-all">
                          Fertig & Speichern
                      </button>
                  </div>
              </div>
          </div>
      )}
    </div>
  );
}


