'use client';
import dynamic from 'next/dynamic';
const FullCalendar = dynamic(() => import('@fullcalendar/react'), { ssr: false });
import dayGridPlugin from '@fullcalendar/daygrid';

import { useState, useRef, useEffect } from 'react';
import { Play, Scissors, Subtitles, UploadCloud, Loader2, Sparkles, Calendar, Check, Settings, X, Clock, Video, Home, Menu, Share2, Download, Edit2, TrendingUp, Flame, Type, MonitorPlay, ChevronUp, ChevronDown, Layout } from 'lucide-react';

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
  const [globalSubtitleConfig, setGlobalSubtitleConfig] = useState({ design: 'hormozi', cta: 'follow', text: '', template: 'clean_lower_third', watermark_text: 'mimaros.eu' });
    const [useMasterCi, setUseMasterCi] = useState(true);
  const [primaryColor, setPrimaryColor] = useState('#14AEEA');
  const [textColor, setTextColor] = useState('#ffffff');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPosition, setLogoPosition] = useState('top-left');
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [globalPreviewUrl, setGlobalPreviewUrl] = useState('');
  const [isGlobalPreviewing, setIsGlobalPreviewing] = useState(false);

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
  }, []);

  const fetchAuthStatus = async () => {
    try {
        const res = await fetch('https://autoshorts-backend-3s1b.onrender.com/api/auth/status');
        const data = await res.json();
        setAuthStatus({ youtube: data.youtube, tiktok: data.tiktok });
    } catch (e) {
        console.error("Error fetching auth status:", e);
    }
  };

  const fetchSchedules = async () => {
    try {
        const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/schedules`);
        const data = await res.json();
        setSchedules(data.schedules || []);
    } catch (e) {
        console.error("Error fetching schedules:", e);
    }
  };

  const fetchHistory = async () => {
    try {
        const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/history`);
        const data = await res.json();
        setHistory(data.history || []);
    } catch (e) {
        console.error("Error fetching history:", e);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (isSequenceMode) {
          const file = e.dataTransfer.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          setLocalFile(e.dataTransfer.files[0]);
          setYoutubeUrl('');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      if (isSequenceMode) {
          const file = e.target.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          setLocalFile(e.target.files[0]);
          setYoutubeUrl(''); 
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

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setLogoFile(file);
      setLogoPreview(URL.createObjectURL(file));
    }
  };

  const fetchVideoInfo = async (url: string) => {
      if (!url) return;
      setIsFetchingMetadata(true);
      try {
          const res = await fetch('https://autoshorts-backend-3s1b.onrender.com/api/video-info', {
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

  const handleProcess = async () => {
    if (!isSequenceMode && !youtubeUrl && !localFile) return;
    if (isSequenceMode && sequence.length === 0) return;
    
    setIsProcessing(true);
    setStatusMessage('Starte Verarbeitung...');
    setClips([]);
    
    try {
      let finalLogoPath = null;
      if (logoFile) {
          const logoData = new FormData();
          logoData.append('file', logoFile);
          const logoRes = await fetch('https://autoshorts-backend-3s1b.onrender.com/api/upload-logo', { method: 'POST', body: logoData });
          if (logoRes.ok) {
              const parsedLogo = await logoRes.json();
              finalLogoPath = parsedLogo.logo_path;
          }
      }
      
      const subConfig = {
          ...globalSubtitleConfig,
          primaryColor,
          textColor,
          logoPosition,
          logoPath: finalLogoPath,
          useMasterCi
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
          
          const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/process-sequence`, {
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
              
              const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/upload-video`, {
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
              
              const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/process-video`, {
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
          const statusRes = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/status/${jobId}`);
          const statusData = await statusRes.json();
          
          if (statusData.status === 'error') {
            clearInterval(interval);
            setIsProcessing(false);
            setStatusMessage('Fehler: ' + statusData.error);
            return;
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
        await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/schedule`, {
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
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-mimaros-blue to-mimaros-blueMid flex items-center justify-center shadow-blue-glow">
                <Scissors className="text-white w-5 h-5" />
            </div>
            <h1 className="font-heading font-bold text-xl tracking-tight text-white flex gap-1">
                AutoShorts <span className="text-mimaros-blue">AI</span>
            </h1>
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

                        {/* Metadata & Trimming UI */}
                        {videoMetadata && (
                            <div className="bg-panel/50 border border-borderGlass rounded-xl p-4 flex flex-col gap-4">
                                <div className="flex items-center gap-4">
                                    {videoMetadata.thumbnail && (
                                        <img src={videoMetadata.thumbnail} alt="Thumbnail" className="w-24 h-auto rounded-lg" />
                                    )}
                                    <div className="flex-1">
                                        <p className="text-white font-bold text-sm line-clamp-2">{videoMetadata.title}</p>
                                        <p className="text-textDim text-xs mt-1">Dauer: {Math.floor(videoMetadata.duration / 60)}:{String(videoMetadata.duration % 60).padStart(2, '0')} min</p>
                                    </div>
                                </div>
                                {videoMetadata.duration > 600 && (
                                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                                        <p className="text-red-400 text-xs mb-3 font-bold">⚠️ Video ist länger als 10 Minuten. Bitte wähle den Bereich aus, der verarbeitet werden soll (max. 10 Min):</p>
                                        <div className="flex gap-4 items-center">
                                            <div className="flex-1">
                                                <label className="block text-[10px] text-textDim uppercase mb-1">Start (in Sekunden)</label>
                                                <input 
                                                    type="number" 
                                                    value={trimStart} 
                                                    onChange={(e) => setTrimStart(parseInt(e.target.value) || 0)}
                                                    className="w-full bg-background border border-borderGlass rounded-lg p-2 text-white text-sm"
                                                    min={0}
                                                    max={videoMetadata.duration}
                                                />
                                            </div>
                                            <div className="flex-1">
                                                <label className="block text-[10px] text-textDim uppercase mb-1">Ende (in Sekunden)</label>
                                                <input 
                                                    type="number" 
                                                    value={trimEnd} 
                                                    onChange={(e) => {
                                                        const val = parseInt(e.target.value) || 0;
                                                        if (val - Number(trimStart) > 600) {
                                                            setTrimEnd(Number(trimStart) + 600);
                                                        } else {
                                                            setTrimEnd(val);
                                                        }
                                                    }}
                                                    className="w-full bg-background border border-borderGlass rounded-lg p-2 text-white text-sm"
                                                    min={0}
                                                    max={videoMetadata.duration}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}
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

                        <div className="border-t border-borderGlass pt-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-bold text-white flex items-center gap-2"><Subtitles className="w-4 h-4 text-mimaros-blue"/> Master CI-Template</h3>
                                <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-textDim">
                                    <input 
                                        type="checkbox" 
                                        checked={useMasterCi} 
                                        onChange={(e) => setUseMasterCi(e.target.checked)}
                                        className="rounded border-borderGlass bg-panel text-mimaros-blue focus:ring-mimaros-blue"
                                    />
                                    Aktiviert
                                </label>
                            </div>
                            
                            {useMasterCi ? (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-2 gap-4">
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
                                    </div>

                                    <div>
                                        <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-2">Logo Upload & Position</label>
                                        <div className="flex flex-col sm:flex-row gap-4">
                                            <div className="flex-1">
                                                <label className="flex items-center justify-center w-full h-12 px-4 transition bg-background/50 border-2 border-borderGlass border-dashed rounded-xl appearance-none cursor-pointer hover:border-mimaros-blue/50 focus:outline-none">
                                                    <span className="flex items-center space-x-2">
                                                        <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-textDim" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                                                            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                                        </svg>
                                                        <span className="font-medium text-sm text-textDim truncate max-w-[150px]">
                                                            {logoFile ? logoFile.name : 'Logo (.png)'}
                                                        </span>
                                                    </span>
                                                    <input type="file" name="file_upload" className="hidden" accept=".png,.jpg,.jpeg" onChange={handleLogoUpload} />
                                                </label>
                                            </div>
                                            <select 
                                                value={logoPosition}
                                                onChange={(e) => setLogoPosition(e.target.value)}
                                                className="bg-background/50 border border-borderGlass rounded-xl px-4 h-12 text-sm text-white focus:outline-none focus:border-mimaros-blue/50"
                                            >
                                                <option value="top-left">Oben Links</option>
                                                <option value="top-right">Oben Rechts</option>
                                                <option value="bottom-left">Unten Links</option>
                                                <option value="bottom-right">Unten Rechts</option>
                                            </select>
                                        </div>
                                    </div>

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
                            ) : (
                                <div className="p-4 bg-background/50 border border-borderGlass rounded-xl">
                                    <p className="text-sm text-textDim">Das Master CI-Template ist deaktiviert. Es wird ein absolutes Basis-Design für Untertitel angewendet (ohne Call-to-Action und ohne Branding).</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Live Preview */}
                    <div className="col-span-1 flex flex-col items-center justify-center">
                        <label className="block text-xs font-bold text-textDim uppercase mb-3 w-full text-center">Live Style-Vorschau</label>
                        <div className="w-full max-w-[220px] bg-background rounded-2xl overflow-hidden shadow-2xl flex items-center justify-center aspect-[9/16] relative bg-cover bg-center transition-all duration-300" style={{
                            backgroundImage: "url('https://images.unsplash.com/photo-1616469829941-c7200edec809?auto=format&fit=crop&w=400&q=80')",
                            border: useMasterCi ? `4px solid ${primaryColor}` : '1px solid var(--borderGlass)'
                        }}>
                            
                            {useMasterCi ? (
                                <>
                                    {logoPreview && (
                                        <div className="absolute w-10 h-10 rounded bg-white/10 backdrop-blur-sm" style={{
                                            top: logoPosition.includes('top') ? '16px' : 'auto',
                                            bottom: logoPosition.includes('bottom') ? '16px' : 'auto',
                                            left: logoPosition.includes('left') ? '16px' : 'auto',
                                            right: logoPosition.includes('right') ? '16px' : 'auto',
                                            backgroundImage: `url(${logoPreview})`,
                                            backgroundSize: 'contain',
                                            backgroundPosition: 'center',
                                            backgroundRepeat: 'no-repeat'
                                        }}></div>
                                    )}
                                    <div className="absolute top-16 left-0 right-0 flex justify-center">
                                        <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 flex items-center gap-2">
                                            <span className="text-white text-[10px] font-medium tracking-wide">
                                                {globalSubtitleConfig.watermark_text || "mimaros.eu"}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="absolute bottom-16 left-0 right-0 text-center font-sans font-bold text-sm bg-black/60 mx-2 p-2 rounded-lg border-l-4" style={{ borderColor: primaryColor, color: textColor }}>
                                        DYNAMISCHE UNTERTITEL
                                        <br/><span className="text-[10px] font-normal opacity-80">Beispieltext</span>
                                    </div>
                                    <div className="absolute bottom-4 left-0 right-0 flex justify-center">
                                        <button className="text-white text-[10px] font-bold px-4 py-1.5 rounded-full shadow-[0_0_15px_rgba(0,0,0,0.5)]" style={{ backgroundColor: primaryColor }}>
                                            FOLGEN FÜR MEHR
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div className="absolute bottom-12 left-0 right-0 text-center text-white font-sans font-bold text-xs bg-black/50 mx-4 p-1">
                                    STANDARD UNTERTITEL
                                </div>
                            )}
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
                                  <video src={clip.videoUrl.startsWith('/') ? 'https://autoshorts-backend-3s1b.onrender.com' + clip.videoUrl : clip.videoUrl} controls className="absolute inset-0 w-full h-full object-cover z-20" />
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
          const res = await fetch(`https://autoshorts-backend-3s1b.onrender.com/api/auth/${platform}`, { method: 'POST' });
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
             <div className="flex items-center gap-2">
                 <div className="w-8 h-8 rounded-full bg-gradient-to-br from-mimaros-blue to-mimaros-blueMid flex items-center justify-center">
                    <Scissors className="text-white w-4 h-4" />
                 </div>
                 <h1 className="font-heading font-bold text-lg text-white">AutoShorts AI</h1>
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
                              <video src={clipUrl.startsWith('/') ? 'https://autoshorts-backend-3s1b.onrender.com' + clipUrl : clipUrl} controls className="w-full aspect-[9/16] bg-black rounded-lg object-contain" />
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


