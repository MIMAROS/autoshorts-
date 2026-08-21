'use client';
import dynamic from 'next/dynamic';
const FullCalendar = dynamic(() => import('@fullcalendar/react'), { ssr: false });
import dayGridPlugin from '@fullcalendar/daygrid';
import { useState, useRef, useEffect } from 'react';
import { Play, Scissors, Subtitles, UploadCloud, Loader2, Sparkles, Calendar, Check, Settings, X, Clock, Video, Home, Menu, Share2, Download, Edit2, TrendingUp, Flame, Type, MonitorPlay, ChevronUp, ChevronDown, Layout, Volume2, Mic, Palette, Layers, Sliders, Eye, RefreshCw, Search, Globe, Link2, ExternalLink } from 'lucide-react';
import Logo from '../components/Logo';

const LogoIcon = ({ className = "w-10 h-10 md:w-12 md:h-12 shrink-0" }: { className?: string }) => (
  <Logo className={className} />
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
  
  // Web Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Array<{
    id: string;
    title: string;
    url: string;
    duration: number;
    thumbnail: string;
    channel: string;
    view_count: number;
  }>>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [inputTab, setInputTab] = useState<'search' | 'url'>('search');
  
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
  const [globalSubtitleConfig, setGlobalSubtitleConfig] = useState({ design: 'karaoke', cta: 'follow', text: '', template: 'clean_lower_third', watermark_text: 'mimaros.eu' });
  const [useMasterCi, setUseMasterCi] = useState(true);
  const [primaryColor, setPrimaryColor] = useState('#14AEEA');
  const [textColor, setTextColor] = useState('#ffffff');
  const [highlightColor, setHighlightColor] = useState('#D4AF37');
  const [boxColor, setBoxColor] = useState('#064A63');
  const [fontName, setFontName] = useState('Work Sans');
  const [titlePosition, setTitlePosition] = useState<'top' | 'center' | 'bottom'>('top');
  const [titleStyle, setTitleStyle] = useState<'box' | 'outline' | 'clean'>('box');
  const [titleFontSize, setTitleFontSize] = useState<'normal' | 'large' | 'xlarge'>('normal');
  const [subtitleFontSize, setSubtitleFontSize] = useState<'normal' | 'large' | 'xlarge'>('normal');
  const [previewMode, setPreviewMode] = useState<'css' | 'video'>('css');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPosition, setLogoPosition] = useState('top-left');
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [logoPath, setLogoPath] = useState<string>('');
  const [logoUploading, setLogoUploading] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [hookHeader, setHookHeader] = useState('');
  const [showTitle, setShowTitle] = useState(true);
  const [showLogo, setShowLogo] = useState(true);
  const [showSubtitles, setShowSubtitles] = useState(true);
  const [showCTA, setShowCTA] = useState(true);
  const [activeAccordion, setActiveAccordion] = useState<string | null>('basic');
  const [globalPreviewUrl, setGlobalPreviewUrl] = useState('');
  const [isGlobalPreviewing, setIsGlobalPreviewing] = useState(false);

  // Multi-Step Wizard Architecture (Step 1, 2, 3)
  const [wizardStep, setWizardStep] = useState<1 | 2 | 3>(1);
  const [selectedMode, setSelectedMode] = useState<'standard' | 'youtube' | 'reaction' | null>(null);
  const [modus1Option, setModus1Option] = useState<'one_to_one' | 'auto_highlights'>('one_to_one');
  const [autoGenerateAIContent, setAutoGenerateAIContent] = useState<boolean>(true);
  const [reactionFile, setReactionFile] = useState<File | null>(null);
  const [socialCaption, setSocialCaption] = useState<string>('');
  const [previewObjectUrl, setPreviewObjectUrl] = useState<string>('');

  const handleResetToStep1 = () => {
    setWizardStep(1);
    setSelectedMode(null);
    setLocalFile(null);
    setYoutubeUrl('');
    setVideoMetadata(null);
    setTrimStart('');
    setTrimEnd('');
    if (previewObjectUrl) {
      URL.revokeObjectURL(previewObjectUrl);
      setPreviewObjectUrl('');
    }
  };

  // Processing State
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

   const [isAnalyzingSection, setIsAnalyzingSection] = useState(false);
  const [enableDubbing, setEnableDubbing] = useState(false);

  const processSelectedFile = (file: File) => {
    setLocalFile(file);
    setYoutubeUrl('');
    if (previewObjectUrl) URL.revokeObjectURL(previewObjectUrl);
    const objUrl = URL.createObjectURL(file);
    setPreviewObjectUrl(objUrl);
    setHookHeader('');
    setSocialCaption('');
    setWizardStep(2);
  };

  const handleConfirmSection = async () => {
    if (!localFile && !youtubeUrl) {
      setWizardStep(3);
      return;
    }

    if (!autoGenerateAIContent) {
      // Nutzer möchte KI-Generierung nicht -> Textfelder bleiben manuell/leer
      setHookHeader('');
      setSocialCaption('');
      setWizardStep(3);
      return;
    }

    setIsAnalyzingSection(true);
    try {
      const formData = new FormData();
      if (localFile) {
        formData.append('file', localFile);
      } else if (youtubeUrl) {
        formData.append('youtube_url', youtubeUrl);
      }
      if (trimStart !== '') formData.append('trim_start', trimStart.toString());
      if (trimEnd !== '') formData.append('trim_end', trimEnd.toString());
      formData.append('video_lang', videoLang);

      const res = await fetch(`${API_BASE}/api/analyze-trimmed-section`, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.title) setHookHeader(data.title.toUpperCase());
        if (data.caption) setSocialCaption(data.caption);
      } else {
        setHookHeader("");
        setSocialCaption("");
      }
    } catch (err) {
      console.error("Fehler bei Bereichs-Analyse:", err);
      setHookHeader("");
      setSocialCaption("");
    } finally {
      setIsAnalyzingSection(false);
      setWizardStep(3);
    }
  };

   const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (isSequenceMode) {
          const file = e.dataTransfer.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          processSelectedFile(e.dataTransfer.files[0]);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      if (isSequenceMode) {
          const file = e.target.files[0];
          setSequence(prev => [...prev, { id: Math.random().toString(), type: 'local', content: '', file: file, name: file.name }]);
      } else {
          processSelectedFile(e.target.files[0]);
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

  const handleSearchVideos = async (queryText?: string) => {
      const q = (queryText !== undefined ? queryText : searchQuery).trim();
      if (!q) return;
      setIsSearching(true);
      try {
          const res = await fetch(`${API_BASE}/api/search-videos`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ query: q, limit: 8 })
          });
          if (res.ok) {
              const data = await res.json();
              if (data.status === 'success' && Array.isArray(data.results)) {
                  setSearchResults(data.results);
              } else {
                  setSearchResults([]);
              }
          }
      } catch (e) {
          console.error("Fehler bei Websuche:", e);
      } finally {
          setIsSearching(false);
      }
  };

  const handleSelectSearchResult = (item: { id: string; title: string; url: string; duration: number; thumbnail: string }) => {
      setYoutubeUrl(item.url);
      setVideoMetadata({
          title: item.title,
          duration: item.duration,
          thumbnail: item.thumbnail
      });
      generateAutoTitle(item.title);
      if (item.duration > 600) {
          setTrimStart(0);
          setTrimEnd(600);
      } else {
          setTrimStart(0);
          setTrimEnd(Math.max(1, Math.round(item.duration)));
      }
  };

  const fetchVideoInfo = async (url: string) => {
      if (!url) return;
      const cleanUrl = url.trim();
      // If user typed a search term instead of URL, automatically search
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://') && !cleanUrl.includes('youtube.com') && !cleanUrl.includes('youtu.be')) {
          setInputTab('search');
          setSearchQuery(cleanUrl);
          handleSearchVideos(cleanUrl);
          return;
      }

      setIsFetchingMetadata(true);
      try {
          const res = await fetch(`${API_BASE}/api/video-info`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ youtube_url: cleanUrl })
          });
          
          if (!res.ok) {
              const text = await res.text();
              console.error("Response body:", text);
              alert("Fehler vom Server: " + text);
              return;
          }
          
          const data = await res.json();
          if (data.status === 'success' && data.info) {
              setVideoMetadata(data.info);
              if (data.info.url && data.info.url !== cleanUrl) {
                  setYoutubeUrl(data.info.url);
              }
              generateAutoTitle(data.info.title);
              if (data.info.duration > 600) {
                  setTrimStart(0);
                  setTrimEnd(600);
              } else {
                  setTrimStart(0);
                  setTrimEnd(Math.max(1, Math.round(data.info.duration)));
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
              design: globalSubtitleConfig.design || 'karaoke',
              use_master_ci: useMasterCi,
              useMasterCi,
              primaryColor,
              textColor,
              highlightColor,
              boxColor,
              titleBgColor: boxColor,
              fontName,
              titlePosition,
              titleStyle,
              titleFontSize,
              subtitleFontSize,
              logoPosition,
              logoPath: logoPath || null,
              resolution,
              hookHeader,
              showTitle,
              showLogo,
              showSubtitles,
              showCTA,
              cta: globalSubtitleConfig.cta || 'follow',
              watermark_text: globalSubtitleConfig.watermark_text || 'mimaros.eu'
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
  }, [globalSubtitleConfig, useMasterCi, primaryColor, textColor, highlightColor, boxColor, fontName, titlePosition, titleStyle, titleFontSize, subtitleFontSize, logoPosition, logoPath, resolution, hookHeader, showTitle, showLogo, showSubtitles, showCTA]);

  const handleProcess = async () => {
    if (!isSequenceMode && !youtubeUrl && !localFile) return;
    if (isSequenceMode && sequence.length === 0) return;
    
    setIsProcessing(true);
    setStatusMessage('Starte Verarbeitung...');
    setClips([]);
    
    try {
      const subConfig = {
          ...globalSubtitleConfig,
          design: globalSubtitleConfig.design || 'karaoke',
          primaryColor,
          textColor,
          highlightColor,
          boxColor,
          titleBgColor: boxColor,
          fontName,
          titlePosition,
          titleStyle,
          titleFontSize,
          subtitleFontSize,
          logoPosition,
          logoPath: logoPath || null,
          useMasterCi,
          use_master_ci: useMasterCi,
          hookHeader,
          showTitle,
          showLogo,
          showSubtitles,
          showCTA,
          cta: globalSubtitleConfig.cta || 'follow',
          watermark_text: globalSubtitleConfig.watermark_text || 'mimaros.eu',
          enable_dubbing: enableDubbing,
          dubbing_voice: selectedVoice,
          modus1Option: selectedMode === 'standard' || !selectedMode ? modus1Option : (modus1Option || 'one_to_one'),
          modus1_option: selectedMode === 'standard' || !selectedMode ? modus1Option : (modus1Option || 'one_to_one'),
          selectedMode: selectedMode || 'standard'
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
          
          if (statusData.generated_title) {
            setHookHeader(statusData.generated_title);
          }
          if (statusData.generated_caption) {
            setSocialCaption(statusData.generated_caption);
          }
          if (statusData.hooks && statusData.hooks.length > 0 && statusData.hooks[0].social_media_caption) {
            setSocialCaption(statusData.hooks[0].social_media_caption);
          }
          
          let phaseDesc = statusData.status;
          if (statusData.status === 'downloading') phaseDesc = "Lade Video herunter...";
          else if (statusData.status === 'transcribing') phaseDesc = "Transkribiere Audio mit Whisper...";
          else if (statusData.status === 'analyzing') phaseDesc = "Generiere Titel & Beschreibung aus Transkript...";
          else if (statusData.status === 'editing') phaseDesc = "Rendere 1:1 Video mit Untertiteln & CI-Design...";
          
          setStatusMessage(`${phaseDesc} (${statusData.progress || 0}%)`);
          
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
            if (newClips.length > 0 && newClips[0].social_media_caption) {
              setSocialCaption(newClips[0].social_media_caption);
            }
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
            <Logo className="w-10 h-10 shrink-0 drop-shadow-[0_0_12px_rgba(86,204,242,0.5)]" />
            <div>
                <h1 className="font-heading font-bold text-lg tracking-tight text-white leading-none">
                    MIMAROS
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
                    <div className="flex items-center gap-2.5">
                        <Logo className="w-8 h-8 shrink-0 drop-shadow-[0_0_10px_rgba(86,204,242,0.5)]" />
                        <div>
                            <h2 className="font-heading font-bold text-base text-white leading-none">MIMAROS</h2>
                            <span className="text-[8px] font-bold text-mimaros-blue uppercase tracking-wider block mt-0.5">AutoShorts AI</span>
                        </div>
                    </div>
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
          {/* Multi-Step Wizard Progress Bar */}
          <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-3 sm:p-4 flex flex-wrap items-center justify-between gap-2 sm:gap-3">
              <button 
                  onClick={handleResetToStep1} 
                  className={`flex items-center justify-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex-1 min-w-[130px] sm:min-w-[160px] ${wizardStep === 1 ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'bg-background/40 text-textDim hover:text-white'}`}
              >
                  <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px] shrink-0">1</span>
                  <span className="truncate">1. Modus wählen</span>
              </button>
              <div className="hidden lg:block h-px bg-borderGlass flex-1 mx-2" />
              <button 
                  disabled={wizardStep < 2} 
                  onClick={() => setWizardStep(2)} 
                  className={`flex items-center justify-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex-1 min-w-[130px] sm:min-w-[160px] ${wizardStep === 2 ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'bg-background/40 text-textDim hover:text-white disabled:opacity-40'}`}
              >
                  <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px] shrink-0">2</span>
                  <span className="truncate">2. Vorschau & Trimming</span>
              </button>
              <div className="hidden lg:block h-px bg-borderGlass flex-1 mx-2" />
              <button 
                  disabled={wizardStep < 3} 
                  onClick={() => setWizardStep(3)} 
                  className={`flex items-center justify-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex-1 min-w-[130px] sm:min-w-[160px] ${wizardStep === 3 ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'bg-background/40 text-textDim hover:text-white disabled:opacity-40'}`}
              >
                  <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px] shrink-0">3</span>
                  <span className="truncate">3. Design & Generierung</span>
              </button>
          </div>

          {/* STEP 1: Das 3-Modi Start-Dashboard */}
          {wizardStep === 1 && (
              <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-8 flex flex-col space-y-8">
                  <div className="text-center space-y-2">
                      <span className="font-display text-[10px] uppercase tracking-[0.2em] text-mimaros-gold font-bold flex items-center justify-center gap-2">
                          <div className="w-5 h-px bg-mimaros-gold/50" /> PROJEKT STARTEN <div className="w-5 h-px bg-mimaros-gold/50" />
                      </span>
                      <h2 className="font-heading text-3xl font-bold text-white tracking-tight">Wähle deinen Verarbeitungs-Modus</h2>
                      <p className="text-sm text-textDim max-w-xl mx-auto">Wähle eine der drei Workflows, um dein Video automatisch in virale Shorts zu verwandeln.</p>
                  </div>

                  {/* 3 Große Auswahl-Kacheln */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Modus 1 - Option A & B */}
                      <div className="bg-background/50 border border-borderGlass hover:border-mimaros-blue p-6 rounded-2xl flex flex-col justify-between space-y-4 transition-all duration-300 shadow-glass">
                          <div className="flex items-center justify-between w-full">
                              <div className="w-12 h-12 rounded-xl bg-mimaros-blue/10 border border-mimaros-blue/30 flex items-center justify-center text-mimaros-blue">
                                  <UploadCloud className="w-6 h-6" />
                              </div>
                              <span className="bg-mimaros-blue/20 text-mimaros-blue font-bold text-[10px] uppercase px-2.5 py-1 rounded-full border border-mimaros-blue/30">Modus 1</span>
                          </div>
                          <div>
                              <h3 className="font-heading font-bold text-lg text-white">Video Upload & Untertitel</h3>
                              <p className="text-xs text-textDim mt-1 leading-relaxed">
                                  Wähle deine bevorzugte Verarbeitungs-Option für dein hochgeladenes Video:
                              </p>
                          </div>

                          <div className="space-y-2 pt-2">
                              {/* Option A */}
                              <button
                                  type="button"
                                  onClick={() => {
                                      setSelectedMode('standard');
                                      setModus1Option('one_to_one');
                                      setShowSubtitles(true);
                                      setIsSequenceMode(false);
                                      setWizardStep(2);
                                  }}
                                  className="w-full p-3 rounded-xl border border-mimaros-blue/40 bg-mimaros-blue/10 hover:bg-mimaros-blue/20 text-left transition-all group"
                              >
                                  <p className="text-xs font-bold text-white group-hover:text-mimaros-blue">Option A: 1:1 Untertitelung</p>
                                  <p className="text-[10px] text-textDim mt-0.5">Video behält 100% seiner Originallänge. Fügt CI-Design & Untertitel hinzu.</p>
                              </button>

                              {/* Option B */}
                              <button
                                  type="button"
                                  onClick={() => {
                                      setSelectedMode('standard');
                                      setModus1Option('auto_highlights');
                                      setIsSequenceMode(false);
                                      setWizardStep(2);
                                  }}
                                  className="w-full p-3 rounded-xl border border-borderGlass hover:border-mimaros-gold bg-background/40 hover:bg-mimaros-gold/10 text-left transition-all group"
                              >
                                  <p className="text-xs font-bold text-white group-hover:text-mimaros-gold">Option B: Auto-Shorts Highlights</p>
                                  <p className="text-[10px] text-textDim mt-0.5">KI analysiert den Inhalt & schneidet automatisch die spannendsten Passagen zusammen.</p>
                              </button>
                          </div>
                      </div>

                      {/* Modus 2 */}
                      <button 
                          onClick={() => {
                              setSelectedMode('youtube');
                              setIsSequenceMode(false);
                              setWizardStep(2);
                          }}
                          className="bg-background/50 hover:bg-panel/80 border border-borderGlass hover:border-mimaros-gold p-6 rounded-2xl flex flex-col text-left space-y-4 transition-all duration-300 group shadow-glass hover:shadow-gold-glow transform hover:-translate-y-1"
                      >
                          <div className="flex items-center justify-between w-full">
                              <div className="w-12 h-12 rounded-xl bg-mimaros-gold/10 border border-mimaros-gold/30 flex items-center justify-center text-mimaros-gold group-hover:scale-110 transition-transform">
                                  <Sparkles className="w-6 h-6" />
                              </div>
                              <span className="bg-mimaros-gold/20 text-mimaros-gold font-bold text-[10px] uppercase px-2.5 py-1 rounded-full border border-mimaros-gold/30">Modus 2</span>
                          </div>
                          <div>
                              <h3 className="font-heading font-bold text-lg text-white group-hover:text-mimaros-gold transition-colors">YouTube AutoShorts</h3>
                              <p className="text-xs text-textDim mt-2 leading-relaxed">
                                  Gib einen YouTube-Link ein. Die KI extrahiert die spannendsten Passagen, schneidet Pausen raus und untertitelt sie.
                              </p>
                          </div>
                          <div className="pt-2 text-xs font-bold text-mimaros-gold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                              YouTube Link eingeben →
                          </div>
                      </button>

                      {/* Modus 3 */}
                      <button 
                          onClick={() => {
                              setSelectedMode('reaction');
                              setIsSequenceMode(true);
                              setWizardStep(2);
                          }}
                          className="bg-background/50 hover:bg-panel/80 border border-borderGlass hover:border-purple-500 p-6 rounded-2xl flex flex-col text-left space-y-4 transition-all duration-300 group shadow-glass transform hover:-translate-y-1"
                      >
                          <div className="flex items-center justify-between w-full">
                              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                                  <Video className="w-6 h-6" />
                              </div>
                              <span className="bg-purple-500/20 text-purple-400 font-bold text-[10px] uppercase px-2.5 py-1 rounded-full border border-purple-500/30">Modus 3</span>
                          </div>
                          <div>
                              <h3 className="font-heading font-bold text-lg text-white group-hover:text-purple-400 transition-colors">YouTube + Reaction / Intro</h3>
                              <p className="text-xs text-textDim mt-2 leading-relaxed">
                                  Gib einen YouTube-Link ein & füge ein eigenes Intro-Video (oder KI-Voiceover) hinzu, das vor den Clip gestitcht wird.
                              </p>
                          </div>
                          <div className="pt-2 text-xs font-bold text-purple-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                              Reaction-Stitching starten →
                          </div>
                      </button>
                  </div>
              </div>
          )}

          {/* STEP 2: Die zwingende Preview- & Trim-Phase */}
          {wizardStep === 2 && (
              <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-8 flex flex-col space-y-8">
                  <div className="flex items-center justify-between border-b border-borderGlass/50 pb-4">
                      <div>
                          <span className="text-[10px] text-mimaros-gold font-bold uppercase tracking-wider">Schritt 2 von 3</span>
                          <h2 className="font-heading text-2xl font-bold text-white">Video sichten & Bereich auswählen</h2>
                      </div>
                      <button onClick={handleResetToStep1} className="text-xs text-textDim hover:text-white bg-background/50 px-3 py-1.5 rounded-lg border border-borderGlass">
                          ← Modus wechseln
                      </button>
                  </div>

                  {/* Input je nach Modus */}
                  {selectedMode === 'standard' && (
                      <div 
                          onDragOver={(e) => e.preventDefault()}
                          onDrop={handleDrop}
                          onClick={() => fileInputRef.current?.click()}
                          className="border-2 border-dashed border-borderGlass hover:border-mimaros-blue/50 rounded-2xl p-8 text-center cursor-pointer transition-all bg-background/30 flex flex-col items-center justify-center gap-3"
                      >
                          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="video/*" className="hidden" />
                          <UploadCloud className="w-10 h-10 text-mimaros-blue" />
                          <div>
                              <p className="text-white font-bold text-sm">{localFile ? localFile.name : "Klicke oder ziehe dein Video hierher"}</p>
                              <p className="text-textDim text-xs mt-1">MP4, MOV oder WebM (bis zu 500MB)</p>
                          </div>
                      </div>
                  )}

                        {(selectedMode === 'youtube' || selectedMode === 'reaction') && (
                        <div className="space-y-4">
                            {/* Dual-Tab Navigation: Web-Suche vs. Direkter Link */}
                            <div className="flex items-center gap-2 p-1 bg-background/60 rounded-xl border border-borderGlass w-fit">
                                <button
                                    type="button"
                                    onClick={() => setInputTab('search')}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${inputTab === 'search' ? 'bg-mimaros-blue text-white shadow-lg' : 'text-textDim hover:text-white'}`}
                                >
                                    <Search className="w-3.5 h-3.5" />
                                    YouTube & Web-Suche
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setInputTab('url')}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${inputTab === 'url' ? 'bg-mimaros-blue text-white shadow-lg' : 'text-textDim hover:text-white'}`}
                                >
                                    <Link2 className="w-3.5 h-3.5" />
                                    Direkter Link
                                </button>
                            </div>

                            {/* TAB 1: Web- & YouTube-Suche */}
                            {inputTab === 'search' && (
                                <div className="space-y-4 bg-background/30 p-5 rounded-2xl border border-borderGlass">
                                    <div className="flex gap-2">
                                        <div className="relative flex-1">
                                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-textDim" />
                                            <input 
                                                type="text" 
                                                value={searchQuery}
                                                onChange={(e) => setSearchQuery(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') {
                                                        e.preventDefault();
                                                        handleSearchVideos();
                                                    }
                                                }}
                                                placeholder="Thema oder Suchbegriff (z.B. KI Trends 2026, Finanzen, Podcasts, Motivation)..." 
                                                className="w-full pl-12 pr-4 py-3.5 border border-borderGlass rounded-xl bg-background/60 text-white placeholder-textDim outline-none focus:border-mimaros-blue text-sm"
                                            />
                                        </div>
                                        <button 
                                            type="button"
                                            onClick={() => handleSearchVideos()}
                                            disabled={isSearching || !searchQuery.trim()}
                                            className="px-6 py-3.5 bg-mimaros-blue hover:bg-mimaros-blue/90 disabled:opacity-50 text-white rounded-xl font-bold flex items-center gap-2 transition-all shadow-md shrink-0"
                                        >
                                            {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                            Suchen
                                        </button>
                                    </div>

                                    {/* Quick Suggestion Tags */}
                                    <div className="flex items-center gap-2 flex-wrap">
                                        <span className="text-[11px] text-textDim font-bold uppercase tracking-wider mr-1">Vorschläge:</span>
                                        {[
                                            { label: '🔥 Trending', query: 'Trending viral shorts' },
                                            { label: '🧠 KI & Tech Trends', query: 'KI Trends 2026' },
                                            { label: '🎙️ Podcasts', query: 'Podcast Highlights Deutsch' },
                                            { label: '📈 Finanzen & Business', query: 'Finanzen Mindset Erfolg' },
                                            { label: '💡 Motivation', query: 'Motivation Disziplin Erfolg' },
                                        ].map((tag, idx) => (
                                            <button
                                                key={idx}
                                                type="button"
                                                onClick={() => {
                                                    setSearchQuery(tag.query);
                                                    handleSearchVideos(tag.query);
                                                }}
                                                className="px-3 py-1 rounded-full text-xs bg-background/50 hover:bg-mimaros-blue/20 hover:text-mimaros-blue border border-borderGlass hover:border-mimaros-blue/40 text-textDim transition-all"
                                            >
                                                {tag.label}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Loading State */}
                                    {isSearching && (
                                        <div className="py-12 flex flex-col items-center justify-center gap-3 text-textDim">
                                            <Loader2 className="w-8 h-8 animate-spin text-mimaros-blue" />
                                            <p className="text-xs font-medium">Durchsuche YouTube & das Web nach passenden Videos...</p>
                                        </div>
                                    )}

                                    {/* Search Results Grid */}
                                    {!isSearching && searchResults.length > 0 && (
                                        <div className="space-y-2 pt-2">
                                            <div className="flex items-center justify-between text-xs text-textDim font-medium">
                                                <span>Gefundene Videos ({searchResults.length}):</span>
                                                <span className="text-[10px] text-mimaros-gold font-bold uppercase tracking-wider">Klicke ein Video zum Auswählen</span>
                                            </div>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                                                {searchResults.map((item) => (
                                                    <div 
                                                        key={item.id}
                                                        onClick={() => handleSelectSearchResult(item)}
                                                        className={`group relative bg-background/60 hover:bg-panel border ${youtubeUrl === item.url ? 'border-mimaros-blue ring-2 ring-mimaros-blue/30' : 'border-borderGlass hover:border-mimaros-blue/50'} rounded-xl overflow-hidden cursor-pointer transition-all duration-200 flex flex-col shadow-sm hover:shadow-lg`}
                                                    >
                                                        {/* Thumbnail & Duration */}
                                                        <div className="relative aspect-video w-full bg-black/40 overflow-hidden">
                                                            {item.thumbnail ? (
                                                                <img src={item.thumbnail} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                                                            ) : (
                                                                <div className="w-full h-full flex items-center justify-center text-textDim">
                                                                    <Video className="w-8 h-8" />
                                                                </div>
                                                            )}
                                                            <div className="absolute bottom-1.5 right-1.5 bg-black/80 backdrop-blur-sm px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-white">
                                                                {Math.floor(item.duration / 60)}:{String(Math.floor(item.duration % 60)).padStart(2, '0')}
                                                            </div>
                                                        </div>

                                                        {/* Video Details */}
                                                        <div className="p-3 flex flex-col flex-1 justify-between gap-2">
                                                            <div>
                                                                <h4 className="text-xs font-bold text-white line-clamp-2 leading-snug group-hover:text-mimaros-blue transition-colors">
                                                                    {item.title}
                                                                </h4>
                                                                <p className="text-[10px] text-textDim mt-1 truncate">
                                                                    {item.channel}
                                                                </p>
                                                            </div>
                                                            <button 
                                                                type="button"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    handleSelectSearchResult(item);
                                                                }}
                                                                className="w-full py-1.5 rounded-lg bg-mimaros-blue/10 hover:bg-mimaros-blue text-mimaros-blue hover:text-white border border-mimaros-blue/30 text-[11px] font-bold transition-all flex items-center justify-center gap-1 mt-1"
                                                            >
                                                                <Play className="w-3 h-3 fill-current" />
                                                                Auswählen
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* TAB 2: Direkter Link */}
                            {inputTab === 'url' && (
                                <div className="space-y-3 bg-background/30 p-5 rounded-2xl border border-borderGlass">
                                    <div className="flex gap-2">
                                        <div className="relative flex-1">
                                            <Play className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-textDim" />
                                            <input 
                                                type="text" 
                                                value={youtubeUrl}
                                                onChange={(e) => { setYoutubeUrl(e.target.value); setVideoMetadata(null); }}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') {
                                                        e.preventDefault();
                                                        fetchVideoInfo(youtubeUrl);
                                                    }
                                                }}
                                                placeholder="YouTube-Link einfügen (z.B. https://youtube.com/watch?v=...)" 
                                                className="w-full pl-12 pr-4 py-3.5 border border-borderGlass rounded-xl bg-background/60 text-white placeholder-textDim outline-none focus:border-mimaros-blue text-sm"
                                            />
                                        </div>
                                        <button 
                                            type="button"
                                            onClick={() => fetchVideoInfo(youtubeUrl)}
                                            disabled={isFetchingMetadata || !youtubeUrl.trim()}
                                            className="px-6 py-3.5 bg-mimaros-blue hover:bg-mimaros-blue/90 disabled:opacity-50 text-white rounded-xl font-bold flex items-center gap-2 transition-all shadow-md shrink-0"
                                        >
                                            {isFetchingMetadata ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                                            Laden
                                        </button>
                                    </div>
                                    <p className="text-[11px] text-textDim">
                                        Tipp: Wenn du einen Suchbegriff statt eines Links eingibst, wird automatisch die YouTube & Web-Suche gestartet.
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                  {/* Echter Video-Player zum Sichten */}
                  {(localFile || videoMetadata) && (
                      <div className="space-y-6">
                          <div className="bg-background rounded-2xl p-4 border border-borderGlass space-y-3">
                              <h4 className="text-xs font-bold text-textDim uppercase tracking-wider flex items-center gap-2">
                                  <Video className="w-4 h-4 text-mimaros-blue" /> Echter Video-Player (Vorschau)
                              </h4>
                              {previewObjectUrl ? (
                                  <video src={previewObjectUrl} controls className="w-full aspect-[9/16] bg-black rounded-xl max-h-[380px] object-contain shadow-2xl mx-auto" />
                              ) : videoMetadata && (
                                  <div className="flex items-center gap-4 bg-panel/50 p-4 rounded-xl">
                                      {videoMetadata.thumbnail && <img src={videoMetadata.thumbnail} alt="Thumbnail" className="w-24 h-auto rounded-lg" />}
                                      <div>
                                          <p className="text-white font-bold text-sm">{videoMetadata.title}</p>
                                          <p className="text-textDim text-xs mt-1">Dauer: {Math.floor(videoMetadata.duration / 60)}:{String(Math.floor(videoMetadata.duration % 60)).padStart(2, '0')} min</p>
                                      </div>
                                  </div>
                              )}
                          </div>

                          {/* Trimmer & Range Selector */}
                          <div className="bg-background/50 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <div className="flex justify-between items-center border-b border-borderGlass/40 pb-3">
                                  <span className="text-xs font-bold text-white flex items-center gap-2">
                                      <Scissors className="w-4 h-4 text-mimaros-blue" /> Bereich festlegen (Start & Ende)
                                  </span>
                                  <span className="text-xs font-mono font-bold text-mimaros-blue bg-mimaros-blue/10 px-3 py-1 rounded-full border border-mimaros-blue/20">
                                      {trimStart !== '' && trimEnd !== '' ? `${Math.max(0, Number(trimEnd) - Number(trimStart))}s ausgewählt` : 'Ganzes Video'}
                                  </span>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                  <div>
                                      <label className="block text-[10px] text-textDim uppercase font-bold mb-1">Start (Sekunden)</label>
                                      <input 
                                          type="number" 
                                          value={trimStart} 
                                          placeholder="z.B. 0"
                                          onChange={(e) => setTrimStart(e.target.value ? parseInt(e.target.value) : '')}
                                          className="w-full bg-panel border border-borderGlass rounded-lg p-2.5 text-white text-xs font-mono"
                                      />
                                  </div>
                                  <div>
                                      <label className="block text-[10px] text-textDim uppercase font-bold mb-1">Ende (Sekunden)</label>
                                      <input 
                                          type="number" 
                                          value={trimEnd} 
                                          placeholder="z.B. 60"
                                          onChange={(e) => setTrimEnd(e.target.value ? parseInt(e.target.value) : '')}
                                          className="w-full bg-panel border border-borderGlass rounded-lg p-2.5 text-white text-xs font-mono"
                                      />
                                  </div>
                              </div>
                          </div>

                          {/* AI-Content Toggle (Kein API Call bei Klick!) */}
                          <div className="bg-background/40 p-4 rounded-xl border border-borderGlass/60 flex items-center justify-between">
                              <div>
                                  <p className="text-xs font-bold text-white flex items-center gap-2">
                                      <Sparkles className="w-4 h-4 text-mimaros-gold" />
                                      Titel & Social-Media-Text per KI generieren
                                  </p>
                                  <p className="text-[10px] text-textDim mt-0.5">
                                      Wird zwingend erst NACH der Transkription aus dem echten Inhalt abgeleitet.
                                  </p>
                              </div>
                              <button 
                                  type="button"
                                  onClick={() => setAutoGenerateAIContent(!autoGenerateAIContent)}
                                  className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${autoGenerateAIContent ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background border border-borderGlass'}`}
                              >
                                  <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${autoGenerateAIContent ? 'translate-x-5' : 'translate-x-0'}`} />
                              </button>
                          </div>

                          {/* Einziges Button in Step 2 */}
                          <button 
                              onClick={handleConfirmSection}
                              disabled={isAnalyzingSection}
                              className="w-full py-4 bg-mimaros-blue text-white rounded-xl font-bold shadow-blue-glow hover:bg-mimaros-blue/90 text-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                          >
                              {isAnalyzingSection ? (
                                  <>
                                      <Loader2 className="w-5 h-5 animate-spin" />
                                      Transkribiere Bereich & generiere Titel...
                                  </>
                              ) : (
                                  <>Bereich bestätigen & Weiter zu den Einstellungen →</>
                              )}
                          </button>
                      </div>
                  )}
              </div>
          )}

          {/* STEP 3: Einstellungen & Finale Generierung */}
          {wizardStep === 3 && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Left Column: Design Controls */}
                  <div className="lg:col-span-2 space-y-6">
                      <div className="bg-panel/40 backdrop-blur-lg rounded-2xl border border-borderGlass shadow-glass p-6 space-y-6">
                          <div className="flex items-center justify-between border-b border-borderGlass/50 pb-4">
                              <div>
                                  <span className="text-[10px] text-mimaros-gold font-bold uppercase tracking-wider">Schritt 3 von 3</span>
                                  <h2 className="font-heading text-2xl font-bold text-white">Design & KI-Anpassung</h2>
                              </div>
                              <button onClick={() => setWizardStep(2)} className="text-xs text-textDim hover:text-white bg-background/50 px-3 py-1.5 rounded-lg border border-borderGlass">
                                  ← Trimming ändern
                              </button>
                          </div>

                          {/* 1. Untertitel-Design & Vorlagen */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <div className="flex items-center justify-between border-b border-borderGlass/40 pb-3">
                                  <div className="flex items-center gap-2">
                                      <Subtitles className="w-4 h-4 text-mimaros-blue" />
                                      <h3 className="text-xs font-bold text-white uppercase tracking-wider">Untertitel-Design & Vorlagen</h3>
                                  </div>
                                  <div className="flex items-center gap-2">
                                      <span className="text-[10px] text-textDim font-bold uppercase">Untertitel anzeigen:</span>
                                      <button 
                                          type="button"
                                          onClick={() => setShowSubtitles(!showSubtitles)}
                                          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showSubtitles ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background border border-borderGlass'}`}
                                      >
                                          <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showSubtitles ? 'translate-x-4' : 'translate-x-0'}`} />
                                      </button>
                                  </div>
                              </div>

                              {showSubtitles && (
                                  <>
                                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                          {[
                                              { id: 'karaoke', name: 'Karaoke Highlight', desc: 'Standard TikTok/Shorts Highlight', badge: 'Populär' },
                                              { id: 'dynamic_box', name: 'Dynamic Box', desc: 'Farbige CI Backdrop Box', badge: 'CI Fokus' },
                                              { id: 'popup_bouncy', name: 'Pop-Up Bouncy', desc: '1-Wort Bouncy Text Mitte', badge: 'Dynamisch' },
                                              { id: 'hormozi', name: 'Hormozi Style', desc: 'Ultra Bold Anton Font', badge: 'Viral' },
                                              { id: 'mimaros_clean', name: 'MIMAROS Clean', desc: 'B2B Minimalist Fades', badge: 'Corporate' }
                                          ].map((tpl) => (
                                              <button 
                                                  key={tpl.id}
                                                  type="button"
                                                  onClick={() => setGlobalSubtitleConfig({...globalSubtitleConfig, design: tpl.id})}
                                                  className={`p-3.5 rounded-xl border text-left transition-all relative ${globalSubtitleConfig.design === tpl.id ? 'bg-mimaros-blue/10 border-mimaros-blue text-white shadow-blue-glow ring-1 ring-mimaros-blue' : 'bg-background/40 border-borderGlass text-textDim hover:text-white hover:border-borderGlass/80'}`}
                                              >
                                                  <div className="flex justify-between items-start mb-1">
                                                      <p className="font-bold text-xs">{tpl.name}</p>
                                                      <span className="text-[8px] bg-white/10 px-1.5 py-0.5 rounded text-mimaros-gold font-bold">{tpl.badge}</span>
                                                  </div>
                                                  <p className="text-[9px] opacity-70 leading-snug">{tpl.desc}</p>
                                              </button>
                                          ))}
                                      </div>

                                      {/* Untertitel Schriftgröße */}
                                      <div className="flex items-center justify-between pt-2 border-t border-borderGlass/30">
                                          <span className="text-[10px] text-textDim font-bold uppercase tracking-wider">Untertitel Schriftgröße</span>
                                          <div className="flex bg-panel border border-borderGlass rounded-lg p-1 gap-1">
                                              {[
                                                  { id: 'normal', label: 'Normal' },
                                                  { id: 'large', label: 'Groß' },
                                                  { id: 'xlarge', label: 'Extra Groß' }
                                              ].map((size) => (
                                                  <button
                                                      key={size.id}
                                                      type="button"
                                                      onClick={() => setSubtitleFontSize(size.id as any)}
                                                      className={`px-2.5 py-1 text-[10px] font-bold rounded ${subtitleFontSize === size.id ? 'bg-mimaros-blue text-white shadow-sm' : 'text-textDim hover:text-white'}`}
                                                  >
                                                      {size.label}
                                                  </button>
                                              ))}
                                          </div>
                                      </div>
                                  </>
                              )}
                          </div>

                          {/* 2. Video-Titel & Hook Header Design */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <div className="flex items-center justify-between border-b border-borderGlass/40 pb-3">
                                  <div className="flex items-center gap-2">
                                      <Type className="w-4 h-4 text-mimaros-gold" />
                                      <h3 className="text-xs font-bold text-white uppercase tracking-wider">Video-Titel & Hook Header</h3>
                                  </div>
                                  <div className="flex items-center gap-2">
                                      <span className="text-[10px] text-textDim font-bold uppercase">Titel anzeigen:</span>
                                      <button 
                                          type="button"
                                          onClick={() => setShowTitle(!showTitle)}
                                          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${showTitle ? 'bg-mimaros-gold shadow-blue-glow' : 'bg-background border border-borderGlass'}`}
                                      >
                                          <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${showTitle ? 'translate-x-4' : 'translate-x-0'}`} />
                                      </button>
                                  </div>
                              </div>

                              {showTitle && (
                                  <>
                                      {/* Titel Text & KI Button */}
                                      <div className="space-y-2">
                                          <div className="flex justify-between items-center">
                                              <label className="text-[10px] font-bold text-textDim uppercase tracking-wider">Titel / Hook Text</label>
                                              <button
                                                  type="button"
                                                  onClick={() => generateAutoTitle(hookHeader || videoMetadata?.title || 'Virales Kurzvideo')}
                                                  className="text-[10px] text-mimaros-gold hover:text-white flex items-center gap-1 font-bold bg-mimaros-gold/10 px-2 py-0.5 rounded border border-mimaros-gold/20 hover:bg-mimaros-gold/20 transition-all"
                                              >
                                                  <Sparkles className="w-3 h-3 text-mimaros-gold" /> Per KI optimieren
                                              </button>
                                          </div>
                                          <input 
                                              type="text" 
                                              value={hookHeader} 
                                              onChange={(e) => setHookHeader(e.target.value)} 
                                              placeholder="Titel eingeben (z.B. DER GEHEIME TRICK)..." 
                                              className="w-full bg-panel border border-borderGlass p-3 rounded-xl text-xs font-bold text-white outline-none focus:border-mimaros-blue uppercase"
                                          />
                                      </div>

                                      {/* Titel Stil, Position & Größe */}
                                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                                          <div>
                                              <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1.5">Titel Stil</label>
                                              <select 
                                                  value={titleStyle} 
                                                  onChange={(e) => setTitleStyle(e.target.value as any)}
                                                  className="w-full bg-panel border border-borderGlass p-2 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue"
                                              >
                                                  <option value="box">CI Box Backdrop</option>
                                                  <option value="outline">Umrandet (Stroke)</option>
                                                  <option value="clean">Minimalistisch</option>
                                              </select>
                                          </div>

                                          <div>
                                              <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1.5">Titel Position</label>
                                              <select 
                                                  value={titlePosition} 
                                                  onChange={(e) => setTitlePosition(e.target.value as any)}
                                                  className="w-full bg-panel border border-borderGlass p-2 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue"
                                              >
                                                  <option value="top">Oben (Top Header)</option>
                                                  <option value="center">Mitte (Center Hook)</option>
                                                  <option value="bottom">Unten (Über Untertiteln)</option>
                                              </select>
                                          </div>

                                          <div>
                                              <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1.5">Titel Schriftgröße</label>
                                              <select 
                                                  value={titleFontSize} 
                                                  onChange={(e) => setTitleFontSize(e.target.value as any)}
                                                  className="w-full bg-panel border border-borderGlass p-2 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue"
                                              >
                                                  <option value="normal">Normal (44px)</option>
                                                  <option value="large">Groß (52px)</option>
                                                  <option value="xlarge">Extra Groß (60px)</option>
                                              </select>
                                          </div>
                                      </div>
                                  </>
                              )}
                          </div>

                          {/* 3. Typografie & Schriftarten */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-3">
                              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                                  <Type className="w-4 h-4 text-mimaros-blue" /> Typografie & CI-Schriftarten
                              </h3>
                              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                                  {[
                                      { id: 'Work Sans', label: 'Work Sans', sub: 'MIMAROS Standard' },
                                      { id: 'Montserrat', label: 'Montserrat', sub: 'Modern & Bold' },
                                      { id: 'Anton', label: 'Anton', sub: 'Hormozi Impact' },
                                      { id: 'Oswald', label: 'Oswald', sub: 'Condensed Tall' },
                                      { id: 'Lato', label: 'Lato', sub: 'Clean Corporate' }
                                  ].map((font) => (
                                      <button
                                          key={font.id}
                                          type="button"
                                          onClick={() => setFontName(font.id)}
                                          className={`p-3 rounded-xl border text-center transition-all ${fontName === font.id ? 'bg-mimaros-blue/15 border-mimaros-blue text-white shadow-blue-glow ring-1 ring-mimaros-blue' : 'bg-background/40 border-borderGlass text-textDim hover:text-white'}`}
                                      >
                                          <p className="font-bold text-xs" style={{ fontFamily: font.id }}>{font.label}</p>
                                          <p className="text-[8px] opacity-60 mt-0.5">{font.sub}</p>
                                      </button>
                                  ))}
                              </div>
                          </div>

                          {/* 4. Farben & Branding (CI Master) */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <div className="flex items-center justify-between border-b border-borderGlass/40 pb-3">
                                  <div className="flex items-center gap-2">
                                      <Palette className="w-4 h-4 text-mimaros-blue" />
                                      <h3 className="text-xs font-bold text-white uppercase tracking-wider">Farben & Branding (CI Master)</h3>
                                  </div>
                                  <div className="flex items-center gap-2">
                                      <span className="text-[10px] text-textDim font-bold uppercase">CI-Rahmen:</span>
                                      <button 
                                          type="button"
                                          onClick={() => setUseMasterCi(!useMasterCi)}
                                          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${useMasterCi ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background border border-borderGlass'}`}
                                      >
                                          <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${useMasterCi ? 'translate-x-4' : 'translate-x-0'}`} />
                                      </button>
                                  </div>
                              </div>

                              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                                  {/* Primärfarbe */}
                                  <div className="space-y-2 bg-panel/50 p-3 rounded-xl border border-borderGlass/50">
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Primär- / Rahmen</label>
                                      <div className="flex items-center gap-2">
                                          <input 
                                              type="color" 
                                              value={primaryColor} 
                                              onChange={(e) => setPrimaryColor(e.target.value)} 
                                              className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border border-white/20 shrink-0" 
                                          />
                                          <input 
                                              type="text" 
                                              value={primaryColor} 
                                              onChange={(e) => setPrimaryColor(e.target.value)} 
                                              className="w-full bg-background border border-borderGlass p-1.5 rounded-lg text-xs font-mono text-white text-center" 
                                          />
                                      </div>
                                      <div className="flex gap-1 pt-1">
                                          {['#14AEEA', '#00FFCC', '#FF5500', '#D4AF37'].map((col) => (
                                              <button key={col} type="button" onClick={() => setPrimaryColor(col)} className="w-5 h-5 rounded-md border border-white/20" style={{ backgroundColor: col }} />
                                          ))}
                                      </div>
                                  </div>

                                  {/* Untertitel Highlight */}
                                  <div className="space-y-2 bg-panel/50 p-3 rounded-xl border border-borderGlass/50">
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Untertitel Highlight</label>
                                      <div className="flex items-center gap-2">
                                          <input 
                                              type="color" 
                                              value={highlightColor} 
                                              onChange={(e) => setHighlightColor(e.target.value)} 
                                              className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border border-white/20 shrink-0" 
                                          />
                                          <input 
                                              type="text" 
                                              value={highlightColor} 
                                              onChange={(e) => setHighlightColor(e.target.value)} 
                                              className="w-full bg-background border border-borderGlass p-1.5 rounded-lg text-xs font-mono text-white text-center" 
                                          />
                                      </div>
                                      <div className="flex gap-1 pt-1">
                                          {['#D4AF37', '#14AEEA', '#FFFF00', '#00FF00', '#FF3B30'].map((col) => (
                                              <button key={col} type="button" onClick={() => setHighlightColor(col)} className="w-5 h-5 rounded-md border border-white/20" style={{ backgroundColor: col }} />
                                          ))}
                                      </div>
                                  </div>

                                  {/* Textfarbe */}
                                  <div className="space-y-2 bg-panel/50 p-3 rounded-xl border border-borderGlass/50">
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Textfarbe</label>
                                      <div className="flex items-center gap-2">
                                          <input 
                                              type="color" 
                                              value={textColor} 
                                              onChange={(e) => setTextColor(e.target.value)} 
                                              className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border border-white/20 shrink-0" 
                                          />
                                          <input 
                                              type="text" 
                                              value={textColor} 
                                              onChange={(e) => setTextColor(e.target.value)} 
                                              className="w-full bg-background border border-borderGlass p-1.5 rounded-lg text-xs font-mono text-white text-center" 
                                          />
                                      </div>
                                      <div className="flex gap-1 pt-1">
                                          {['#FFFFFF', '#F3F4F6', '#E5E7EB', '#000000'].map((col) => (
                                              <button key={col} type="button" onClick={() => setTextColor(col)} className="w-5 h-5 rounded-md border border-white/20" style={{ backgroundColor: col }} />
                                          ))}
                                      </div>
                                  </div>

                                  {/* Box / Backdrop Farbe */}
                                  <div className="space-y-2 bg-panel/50 p-3 rounded-xl border border-borderGlass/50">
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Box Hintergrund</label>
                                      <div className="flex items-center gap-2">
                                          <input 
                                              type="color" 
                                              value={boxColor} 
                                              onChange={(e) => setBoxColor(e.target.value)} 
                                              className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border border-white/20 shrink-0" 
                                          />
                                          <input 
                                              type="text" 
                                              value={boxColor} 
                                              onChange={(e) => setBoxColor(e.target.value)} 
                                              className="w-full bg-background border border-borderGlass p-1.5 rounded-lg text-xs font-mono text-white text-center" 
                                          />
                                      </div>
                                      <div className="flex gap-1 pt-1">
                                          {['#064A63', '#0B111A', '#18181B', '#000000'].map((col) => (
                                              <button key={col} type="button" onClick={() => setBoxColor(col)} className="w-5 h-5 rounded-md border border-white/20" style={{ backgroundColor: col }} />
                                          ))}
                                      </div>
                                  </div>
                              </div>
                          </div>

                          {/* 5. Logo, Call-to-Action & Wasserzeichen */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                                  <Layers className="w-4 h-4 text-mimaros-blue" /> Branding, Logo & CTA Button
                              </h3>
                              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                  {/* Logo Position */}
                                  <div className="space-y-2">
                                      <div className="flex justify-between items-center">
                                          <label className="text-[10px] font-bold text-textDim uppercase tracking-wider">Logo Overlay</label>
                                          <button 
                                              type="button" 
                                              onClick={() => setShowLogo(!showLogo)} 
                                              className="text-[10px] text-mimaros-blue font-bold"
                                          >
                                              {showLogo ? 'Aktiv' : 'Inaktiv'}
                                          </button>
                                      </div>
                                      <select 
                                          value={logoPosition} 
                                          onChange={(e) => setLogoPosition(e.target.value)} 
                                          disabled={!showLogo}
                                          className="w-full bg-panel border border-borderGlass p-2.5 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue disabled:opacity-40"
                                      >
                                          <option value="top-left">Oben Links</option>
                                          <option value="top-right">Oben Rechts</option>
                                          <option value="bottom-left">Unten Links</option>
                                          <option value="bottom-right">Unten Rechts</option>
                                      </select>
                                  </div>

                                  {/* CTA Button */}
                                  <div className="space-y-2">
                                      <div className="flex justify-between items-center">
                                          <label className="text-[10px] font-bold text-textDim uppercase tracking-wider">Call-to-Action Button</label>
                                          <button 
                                              type="button" 
                                              onClick={() => setShowCTA(!showCTA)} 
                                              className="text-[10px] text-mimaros-blue font-bold"
                                          >
                                              {showCTA ? 'Aktiv' : 'Inaktiv'}
                                          </button>
                                      </div>
                                      <select 
                                          value={globalSubtitleConfig.cta} 
                                          onChange={(e) => setGlobalSubtitleConfig({...globalSubtitleConfig, cta: e.target.value})} 
                                          disabled={!showCTA}
                                          className="w-full bg-panel border border-borderGlass p-2.5 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue disabled:opacity-40"
                                      >
                                          <option value="follow">Folgen für mehr</option>
                                          <option value="subscribe">Jetzt Abonnieren</option>
                                          <option value="more">Mehr Videos</option>
                                          <option value="none">Kein Button</option>
                                      </select>
                                  </div>

                                  {/* Wasserzeichen */}
                                  <div className="space-y-2">
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider">Wasserzeichen / Domain</label>
                                      <input 
                                          type="text" 
                                          value={globalSubtitleConfig.watermark_text} 
                                          onChange={(e) => setGlobalSubtitleConfig({...globalSubtitleConfig, watermark_text: e.target.value})} 
                                          placeholder="mimaros.eu" 
                                          className="w-full bg-panel border border-borderGlass p-2.5 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue"
                                      />
                                  </div>
                              </div>
                          </div>

                          {/* 6. Sprachen & KI Dubbing Panel */}
                          <div className="bg-background/40 p-5 rounded-2xl border border-borderGlass space-y-4">
                              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                                  <Volume2 className="w-4 h-4 text-mimaros-blue" /> Sprachen & KI Video-Übersetzung (Dubbing)
                              </h4>
                              <div className="grid grid-cols-2 gap-4">
                                  <div>
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Audio-Sprache (Original)</label>
                                      <select value={videoLang} onChange={(e) => setVideoLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2.5 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue">
                                          <option value="de">Deutsch</option>
                                          <option value="en">Englisch</option>
                                          <option value="es">Spanisch</option>
                                          <option value="auto">Auto-Erkennen</option>
                                      </select>
                                  </div>
                                  <div>
                                      <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Untertitel Zielsprache</label>
                                      <select value={subtitleLang} onChange={(e) => setSubtitleLang(e.target.value)} className="w-full bg-panel border border-borderGlass p-2.5 rounded-xl text-xs text-white outline-none focus:border-mimaros-blue">
                                          <option value="auto">Wie Video (Keine Übersetzung)</option>
                                          <option value="de">Deutsch</option>
                                          <option value="en">Englisch</option>
                                          <option value="es">Spanisch</option>
                                      </select>
                                  </div>
                              </div>

                              {/* Dubbing Toggle */}
                              {subtitleLang !== 'auto' && subtitleLang !== videoLang && (
                                  <div className="bg-panel/60 border border-mimaros-blue/40 rounded-xl p-4 space-y-3">
                                      <div className="flex items-center justify-between">
                                          <div>
                                              <p className="text-xs font-bold text-white flex items-center gap-2">
                                                  <Volume2 className="w-4 h-4 text-mimaros-blue" />
                                                  Audio ebenfalls übersetzen (KI Dubbing)
                                              </p>
                                              <p className="text-[10px] text-textDim mt-0.5">
                                                  Ersetzt die Originalstimme durch eine KI-Sprecherstimme in der Zielsprache.
                                              </p>
                                          </div>
                                          <button 
                                              type="button"
                                              onClick={() => setEnableDubbing(!enableDubbing)}
                                              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${enableDubbing ? 'bg-mimaros-blue shadow-blue-glow' : 'bg-background border border-borderGlass'}`}
                                          >
                                              <span className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ease-in-out ${enableDubbing ? 'translate-x-5' : 'translate-x-0'}`} />
                                          </button>
                                      </div>

                                      {enableDubbing && (
                                          <div className="pt-2 border-t border-borderGlass/30 flex items-center justify-between">
                                              <span className="text-xs text-textDim font-bold">Sprecherstimme Zielsprache:</span>
                                              <select 
                                                  value={selectedVoice} 
                                                  onChange={(e) => setSelectedVoice(e.target.value)}
                                                  className="bg-background border border-borderGlass text-xs text-white p-1.5 rounded-lg outline-none"
                                              >
                                                  <option value="alloy">Alloy (Dynamisch)</option>
                                                  <option value="echo">Echo (Klar & Neutral)</option>
                                                  <option value="nova">Nova (Weiblich/Sanft)</option>
                                                  <option value="onyx">Onyx (Tief & Markant)</option>
                                              </select>
                                          </div>
                                      )}
                                  </div>
                              )}
                          </div>

                          {/* Finaler Haupt-Button */}
                          <button 
                              onClick={handleProcess}
                              disabled={isProcessing}
                              className="w-full py-5 bg-gradient-to-r from-mimaros-blue via-mimaros-blue to-mimaros-gold text-white rounded-xl font-black text-xl shadow-2xl hover:opacity-95 transition-all uppercase tracking-wider flex items-center justify-center gap-3 disabled:opacity-50"
                          >
                              {isProcessing ? <Loader2 className="w-6 h-6 animate-spin" /> : <Sparkles className="w-6 h-6" />}
                              {isProcessing ? "Verarbeite Video..." : "🚀 Video jetzt generieren"}
                          </button>
                      </div>
                  </div>

                  {/* Right Column: Live Handy & Video Vorschau */}
                  <div className="lg:col-span-1 flex flex-col items-center space-y-4">
                      {/* Preview Switcher Header */}
                      <div className="w-full flex items-center justify-between bg-panel/60 p-1.5 rounded-xl border border-borderGlass">
                          <button
                              type="button"
                              onClick={() => setPreviewMode('css')}
                              className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${previewMode === 'css' ? 'bg-mimaros-blue text-white shadow-blue-glow' : 'text-textDim hover:text-white'}`}
                          >
                              <Eye className="w-3.5 h-3.5" /> Live Interaktiv
                          </button>
                          <button
                              type="button"
                              onClick={() => {
                                  setPreviewMode('video');
                                  handleGeneratePreview();
                              }}
                              className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${previewMode === 'video' ? 'bg-mimaros-gold text-black shadow-md' : 'text-textDim hover:text-white'}`}
                          >
                              <MonitorPlay className="w-3.5 h-3.5" /> Video Clip
                          </button>
                      </div>

                      {/* Phone Container */}
                      <div className="w-full max-w-[260px] bg-background rounded-3xl overflow-hidden shadow-2xl flex items-center justify-center aspect-[9/16] relative bg-cover bg-center transition-all duration-300" style={{
                          backgroundImage: previewMode === 'css' ? "url('https://images.unsplash.com/photo-1616469829941-c7200edec809?auto=format&fit=crop&w=600&q=80')" : 'none',
                          border: useMasterCi ? `4px solid ${primaryColor}` : '2px solid rgba(255,255,255,0.1)'
                      }}>
                          {previewMode === 'video' && globalPreviewUrl ? (
                              <div className="absolute inset-0 z-20 bg-black flex items-center justify-center">
                                  <video 
                                      src={globalPreviewUrl} 
                                      autoPlay 
                                      loop 
                                      muted 
                                      playsInline 
                                      className="w-full h-full object-cover" 
                                  />
                                  {isGlobalPreviewing && (
                                      <div className="absolute inset-0 bg-black/60 flex items-center justify-center gap-2 text-xs font-bold text-white">
                                          <Loader2 className="w-4 h-4 animate-spin text-mimaros-blue" /> Aktualisiere...
                                      </div>
                                  )}
                              </div>
                           ) : (
                               <>
                                   {/* MIMAROS.EU Brand Tag (Above Title) */}
                                   {useMasterCi && globalSubtitleConfig.watermark_text && (
                                       <div className="absolute top-2.5 left-0 right-0 z-25 flex justify-center pointer-events-none">
                                           <div className="bg-[#064A63]/90 border border-[#14AEEA]/60 backdrop-blur-md px-2.5 py-0.5 rounded-full text-[8px] text-[#D4AF37] font-bold tracking-widest uppercase shadow-md">
                                               {globalSubtitleConfig.watermark_text}
                                           </div>
                                       </div>
                                   )}

                                   {/* Logo */}
                                   {showLogo && (
                                       <div className={`absolute z-30 pointer-events-none ${logoPosition === 'top-left' ? 'top-2.5 left-2.5' : logoPosition === 'top-right' ? 'top-2.5 right-2.5' : logoPosition === 'bottom-left' ? 'bottom-2.5 left-2.5' : 'bottom-2.5 right-2.5'}`}>
                                           <LogoIcon className="w-5 h-5 drop-shadow-[0_0_8px_rgba(20,174,234,0.6)]" />
                                       </div>
                                   )}

                                   {/* Video Title Header (Positioned Below MIMAROS.EU) */}
                                   {showTitle && (
                                       <div 
                                           className={`absolute left-2 right-2 z-20 flex flex-col items-center justify-center text-center transition-all ${titlePosition === 'center' ? 'top-1/3 -translate-y-1/2' : titlePosition === 'bottom' ? 'bottom-24' : 'top-8'}`}
                                       >
                                      <div 
                                          className={`px-3 py-1.5 rounded-lg max-w-[95%] w-auto mx-auto uppercase font-bold tracking-wide transition-all ${titleStyle === 'box' ? 'shadow-xl' : titleStyle === 'outline' ? 'drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]' : 'drop-shadow-[0_0_10px_rgba(20,174,234,0.5)]'}`}
                                          style={{
                                              backgroundColor: titleStyle === 'box' ? (boxColor || '#064A63') : 'transparent',
                                              color: textColor || '#FFFFFF',
                                              fontFamily: fontName,
                                              fontSize: titleFontSize === 'large' ? '12px' : titleFontSize === 'xlarge' ? '14px' : '10px',
                                              border: titleStyle === 'outline' ? `2px solid ${primaryColor}` : 'none',
                                              lineHeight: 1.2
                                          }}
                                      >
                                          {hookHeader ? hookHeader.toUpperCase() : (videoMetadata?.title ? videoMetadata.title.toUpperCase() : "DER GEHEIME TRICK")}
                                      </div>
                                  </div>
                              )}

                                  {/* Subtitles Overlay - Safe Zone well above bottom overlays */}
                                  {showSubtitles && (
                                      <div className={`absolute left-2 right-2 z-20 flex flex-col items-center justify-center text-center ${globalSubtitleConfig.design === 'popup_bouncy' ? 'top-1/2 -translate-y-1/2' : 'bottom-20'}`}>
                                          <div 
                                              className="transition-all"
                                              style={{
                                                  fontFamily: fontName,
                                                  fontSize: subtitleFontSize === 'large' ? '13px' : subtitleFontSize === 'xlarge' ? '15px' : '11px'
                                              }}
                                          >
                                              {globalSubtitleConfig.design === 'mimaros_clean' && (
                                                  <div 
                                                      className="px-4 py-2 rounded-xl border border-[#14AEEA]/60 shadow-2xl backdrop-blur-md font-bold tracking-wide uppercase"
                                                      style={{
                                                          backgroundColor: `${boxColor}E6`,
                                                          color: textColor
                                                      }}
                                                  >
                                                      <span style={{ color: highlightColor }} className="font-bold">MIMAROS</span> CLEAN STIL
                                                  </div>
                                              )}

                                              {globalSubtitleConfig.design === 'karaoke' && (
                                                  <div 
                                                      className="px-3.5 py-1.5 rounded-xl font-extrabold uppercase tracking-wide drop-shadow-[0_3px_6px_rgba(0,0,0,1)]"
                                                      style={{ color: textColor }}
                                                  >
                                                      <span style={{ color: highlightColor }} className="drop-shadow-[0_0_8px_currentColor]">KARAOKE</span> HIGHLIGHT
                                                  </div>
                                              )}

                                              {globalSubtitleConfig.design === 'dynamic_box' && (
                                                  <div 
                                                      className="px-4 py-2 rounded-xl font-black uppercase shadow-2xl tracking-wider border border-white/20"
                                                      style={{ 
                                                          backgroundColor: `${boxColor}F2`,
                                                          color: textColor
                                                      }}
                                                  >
                                                      <span style={{ color: highlightColor }}>DYNAMIC</span> BOX STIL
                                                  </div>
                                              )}

                                              {globalSubtitleConfig.design === 'popup_bouncy' && (
                                                  <div 
                                                      className="px-4 py-2 rounded-2xl bg-[#064A63]/90 border border-[#14AEEA]/60 backdrop-blur-md font-black uppercase text-center animate-bounce shadow-2xl"
                                                      style={{ 
                                                          color: highlightColor,
                                                          fontSize: subtitleFontSize === 'large' ? '15px' : subtitleFontSize === 'xlarge' ? '17px' : '13px'
                                                      }}
                                                  >
                                                      BOUNCY!
                                                  </div>
                                              )}

                                              {globalSubtitleConfig.design === 'hormozi' && (
                                                  <div 
                                                      className="px-3.5 py-1.5 rounded-lg font-black uppercase tracking-tighter drop-shadow-[0_3px_6px_rgba(0,0,0,1)]"
                                                      style={{ fontFamily: 'Anton, sans-serif' }}
                                                  >
                                                      <span style={{ color: highlightColor }}>HORMOZI</span> <span className="text-[#00FF00]">STYLE</span>
                                                  </div>
                                              )}
                                          </div>
                                      </div>
                                  )}

                                  {/* Call-to-Action Overlay */}
                                  {showCTA && globalSubtitleConfig.cta !== 'none' && (
                                      <div className="absolute bottom-2 left-0 right-0 z-20 flex justify-center pointer-events-none">
                                          <div 
                                              className="px-3 py-1 rounded-full text-[9px] font-black uppercase shadow-lg tracking-wider text-white"
                                              style={{ 
                                                  backgroundColor: primaryColor,
                                                  fontFamily: fontName
                                              }}
                                          >
                                              {globalSubtitleConfig.cta === 'subscribe' ? 'JETZT ABONNIEREN' : globalSubtitleConfig.cta === 'more' ? 'MEHR VIDEOS' : 'FOLGEN FÜR MEHR'}
                                          </div>
                                      </div>
                                  )}
                              </>
                          )}
                      </div>

                      {/* Preview Refresh Button */}
                      <button
                          type="button"
                          onClick={handleGeneratePreview}
                          disabled={isGlobalPreviewing}
                          className="text-xs text-textDim hover:text-white bg-background/50 hover:bg-background px-4 py-2 rounded-xl border border-borderGlass flex items-center gap-2 transition-all shadow-sm"
                      >
                          <RefreshCw className={`w-3.5 h-3.5 ${isGlobalPreviewing ? 'animate-spin text-mimaros-blue' : ''}`} />
                          {isGlobalPreviewing ? "Rendere Vorschau..." : "Vorschau aktualisieren"}
                      </button>
                  </div>
              </div>
          )}

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

                           <div className="flex-1 flex flex-col gap-4 w-full">
                               <div className="flex justify-between items-start flex-wrap gap-2">
                                   <div>
                                       <span className="text-[10px] text-mimaros-gold font-bold uppercase tracking-wider flex items-center gap-1">
                                           <Sparkles className="w-3 h-3 text-mimaros-gold" /> Aus Video-Transkript generiert
                                       </span>
                                       <h4 className="font-heading font-bold text-xl text-white mt-0.5">#{idx+1} {clip.title}</h4>
                                   </div>
                                   <div className="flex flex-col items-center bg-mimaros-blue/10 border border-mimaros-blue/30 rounded-xl px-4 py-2">
                                       <span className="flex items-center gap-1 text-mimaros-gold font-bold text-xs uppercase tracking-wider"><Flame className="w-3 h-3"/> Viral Score</span>
                                       <span className="text-2xl font-black font-heading text-white">{clip.viralScore}<span className="text-sm text-textDim">/100</span></span>
                                   </div>
                               </div>

                               {/* Aus Transkript-Kontext generierter Titel & Social Media Text (Final bearbeitbar) */}
                               <div className="space-y-3 bg-background/50 p-4 rounded-xl border border-borderGlass">
                                   <div>
                                       <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Generierter Video-Titel (Bearbeitbar)</label>
                                       <input 
                                           type="text" 
                                           value={clip.title}
                                           onChange={(e) => {
                                               const updated = [...clips];
                                               updated[idx].title = e.target.value;
                                               setClips(updated);
                                           }}
                                           className="w-full bg-panel border border-borderGlass rounded-lg px-3 py-2 text-xs font-bold text-white outline-none focus:border-mimaros-blue"
                                       />
                                   </div>
                                   <div>
                                       <label className="block text-[10px] font-bold text-textDim uppercase tracking-wider mb-1">Generierte Social-Media Beschreibung</label>
                                       <textarea 
                                           rows={3}
                                           value={clip.social_media_caption || `🔥 ${clip.title}\n\n#shorts #content`}
                                           onChange={(e) => {
                                               const updated = [...clips];
                                               updated[idx].social_media_caption = e.target.value;
                                               setClips(updated);
                                           }}
                                           className="w-full bg-panel border border-borderGlass rounded-xl p-3 text-xs text-white outline-none focus:border-mimaros-blue leading-relaxed"
                                       />
                                   </div>
                               </div>

                               <div className="mt-auto pt-2 flex gap-3">
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
          {/* Header/Navbar mit sichtbarem Logo (Desktop & Mobile) */}
          <header className="w-full border-b border-borderGlass bg-panel/85 backdrop-blur-xl sticky top-0 z-30 px-4 sm:px-6 py-3.5 flex items-center justify-between shadow-glass">
             <div className="flex items-center gap-3 shrink-0">
                 <Logo className="w-9 h-9 sm:w-10 sm:h-10 shrink-0 block drop-shadow-[0_0_12px_rgba(20,174,234,0.5)]" />
                 <div className="flex flex-col">
                     <h1 className="font-heading font-bold text-base sm:text-lg tracking-tight text-white leading-none">MIMAROS</h1>
                     <span className="text-[9px] sm:text-[10px] font-bold text-mimaros-blue uppercase block mt-0.5 tracking-wider">AutoShorts AI</span>
                 </div>
             </div>
             <div className="flex items-center gap-3">
                 <span className="hidden sm:inline-flex text-[10px] font-mono font-bold text-mimaros-gold bg-mimaros-gold/10 px-3 py-1 rounded-full border border-mimaros-gold/30">
                     PRO v3.0
                 </span>
                 <button onClick={() => setIsMobileMenuOpen(true)} className="md:hidden text-white p-1.5 hover:bg-background/40 rounded-lg">
                     <Menu className="w-6 h-6" />
                 </button>
             </div>
          </header>
          
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
      {/* Splash Screen / Ladebildschirm mit neuem minimalistischem Logo & responsivem Ladebalken */}
      {isProcessing && (
          <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/95 backdrop-blur-2xl p-4 sm:p-6 overflow-hidden max-w-full">
              <div className="w-24 h-24 sm:w-28 sm:h-28 mb-6 animate-pulse drop-shadow-[0_0_30px_rgba(86,204,242,0.7)] flex items-center justify-center shrink-0 block">
                  <Logo className="w-full h-full shrink-0 block" />
              </div>
              <h3 className="text-xl sm:text-2xl font-black font-heading text-white tracking-wide mb-2 text-center">
                  Verarbeite Video...
              </h3>
              <p className="text-textDim text-xs sm:text-sm max-w-md text-center mb-6 px-4 leading-relaxed">
                  {statusMessage || "Smart Trimming, Untertitelung & Design-Export werden angewendet."}
              </p>

              {/* Responsiver Ladebalken */}
              <div className="w-full max-w-xs sm:max-w-md bg-panel border border-borderGlass rounded-full p-1 shadow-2xl relative overflow-hidden">
                  <div 
                      className="bg-gradient-to-r from-[#56CCF2] to-[#F2994A] h-3 sm:h-4 rounded-full transition-all duration-500 relative"
                      style={{ width: `${Math.max(10, Math.min(100, parseInt(statusMessage.match(/\((\d+)%\)/)?.[1] || '45')))}%` }}
                  >
                      <div className="absolute inset-0 bg-white/25 animate-pulse rounded-full" />
                  </div>
              </div>
          </div>
      )}
    </div>
  );
}


