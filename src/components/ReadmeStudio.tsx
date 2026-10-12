import React, { useState, useEffect } from 'react';
import { FileText, Copy, Check, Download, Eye, Code, Terminal, Sparkles } from 'lucide-react';

interface ReadmeStudioProps {
  isLightMode: boolean;
}

export const ReadmeStudio: React.FC<ReadmeStudioProps> = ({ isLightMode }) => {
  const [markdown, setMarkdown] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'preview' | 'raw'>('preview');

  useEffect(() => {
    fetch('/api/readme')
      .then((res) => res.json())
      .then((data) => {
        if (data.content) {
          setMarkdown(data.content);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'README.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="mb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">README Studio & Document Workbench</h2>
          <p className="text-xs sm:text-sm opacity-75">
            Real-time inspection and export of the generated GitHub profile README
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 p-1 rounded-xl border border-inherit">
            <button
              onClick={() => setViewMode('preview')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium flex items-center space-x-1 cursor-pointer ${
                viewMode === 'preview'
                  ? isLightMode
                    ? 'bg-[#0D604B] text-white shadow-sm'
                    : 'bg-[#285047] text-[#8DE0C1] shadow-sm'
                  : 'opacity-70 hover:opacity-100'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium flex items-center space-x-1 cursor-pointer ${
                viewMode === 'raw'
                  ? isLightMode
                    ? 'bg-[#0D604B] text-white shadow-sm'
                    : 'bg-[#285047] text-[#8DE0C1] shadow-sm'
                  : 'opacity-70 hover:opacity-100'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Raw Source</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className={`p-2 rounded-xl border text-xs font-mono transition-all flex items-center space-x-1 cursor-pointer ${
              isLightMode
                ? 'bg-white border-[#BAD6CB] hover:bg-[#E2F0EA] text-[#0D604B]'
                : 'bg-[#101B1D] border-[#285047] hover:bg-[#14272A] text-[#8DE0C1]'
            }`}
          >
            {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
            <span className="hidden sm:inline">{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownload}
            className={`p-2 rounded-xl border text-xs font-mono transition-all flex items-center space-x-1 cursor-pointer ${
              isLightMode
                ? 'bg-white border-[#BAD6CB] hover:bg-[#E2F0EA] text-[#0D604B]'
                : 'bg-[#101B1D] border-[#285047] hover:bg-[#14272A] text-[#8DE0C1]'
            }`}
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Export</span>
          </button>
        </div>
      </div>

      {/* Editor / Viewer Frame */}
      <div className={`rounded-2xl border overflow-hidden ${
        isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#101B1D] border-[#285047]'
      }`}>
        <div className={`px-4 py-3 border-b flex items-center justify-between text-xs font-mono ${
          isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#0D1214] border-[#285047]'
        }`}>
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 opacity-75" />
            <span>README.md</span>
            <span className="opacity-50">·</span>
            <span className="text-[11px] opacity-75">{markdown.length.toLocaleString()} characters</span>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
              markdown.includes('<!-- PROFILE:GENERATED:START -->')
                ? 'bg-emerald-500/10 text-emerald-500'
                : 'bg-red-500/10 text-red-500'
            }`}>
              GEN-MARKERS ACTIVE
            </span>
          </div>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="py-20 text-center font-mono text-sm opacity-60">
              Loading README stream...
            </div>
          ) : viewMode === 'raw' ? (
            <pre className={`p-4 rounded-xl text-xs overflow-x-auto font-mono whitespace-pre leading-relaxed ${
              isLightMode ? 'bg-[#F4F8F6] text-[#11231F]' : 'bg-[#080D0F] text-[#F0F3EE]'
            }`}>
              {markdown}
            </pre>
          ) : (
            <div className="prose max-w-none space-y-6 text-sm leading-relaxed">
              <div className="p-4 rounded-xl border border-dashed text-xs font-mono opacity-80 mb-6">
                {'<!-- PROFILE:GENERATED:START -->'} (Automated Marker Boundary)
              </div>

              {/* Rendered preview sections */}
              <div className="space-y-6">
                <div className="flex justify-center">
                  <img src="/assets/hero.svg" alt="Hero banner" className="w-full max-w-2xl rounded-lg" />
                </div>

                <div className="flex flex-wrap gap-2 text-xs font-mono justify-center border-y py-3 border-inherit">
                  <span className="font-bold">Explore:</span>
                  <a href="#about" className="hover:underline">About</a> ·
                  <a href="#hands-on-engineering" className="hover:underline">Hands-on Engineering</a> ·
                  <a href="#selected-work" className="hover:underline">Selected Work</a> ·
                  <a href="#experience" className="hover:underline">Experience</a> ·
                  <a href="#education" className="hover:underline">Education</a> ·
                  <a href="#telemetry" className="hover:underline">Telemetry</a> ·
                  <a href="#contribution-art" className="hover:underline">Contribution Art</a>
                </div>

                <div className="space-y-3">
                  <h3 className="text-lg font-bold border-b pb-2">About Sarthak Sulkhlan</h3>
                  <div className="flex flex-col sm:flex-row gap-4 items-center">
                    <img src="/assets/profile-portrait.png" alt="Portrait" className="w-36 rounded-lg border" />
                    <div className="text-xs space-y-2 flex-1">
                      <p><strong>Study:</strong> B.Tech, Computer Science and Engineering (Data Science)</p>
                      <p><strong>Interests:</strong> Software engineering · data science · applied AI</p>
                      <p><strong>Repositories:</strong> EPOCH, Asset Sentinel, MatrixCore, MediKiosk</p>
                      <p><strong>Focus:</strong> Building practical, reliable software systems</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-lg font-bold border-b pb-2">Telemetry</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <img src="/assets/activity.svg" alt="Activity chart" className="w-full rounded border" />
                    <img src="/assets/language-stats.svg" alt="Language statistics" className="w-full rounded border" />
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-lg font-bold border-b pb-2">Contribution Art</h3>
                  <div className="flex justify-center">
                    <img src="/assets/contribution-art.svg" alt="Contribution art" className="w-full max-w-xl rounded border" />
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-xl border border-dashed text-xs font-mono opacity-80 mt-6">
                {'<!-- PROFILE:GENERATED:END -->'} (Automated Marker Boundary)
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
