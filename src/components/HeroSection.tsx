import React, { useState, useEffect } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { ProfileData } from '../types.ts';

interface HeroSectionProps {
  isLightMode: boolean;
  profileData: ProfileData | null;
  onExploreProjects: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  isLightMode,
  profileData,
  onExploreProjects,
}) => {
  const phrases = [
    'From ideas to practical software, end to end.',
    'Learning data science and applied AI.',
    'Building useful, reliable systems.',
    'Governed software evolution & telemetry pipelines.',
  ];

  const [phraseIndex, setPhraseIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  // Typewriter effect
  useEffect(() => {
    const currentPhrase = phrases[phraseIndex];
    const typingSpeed = isDeleting ? 30 : 55;

    if (!isDeleting && displayedText === currentPhrase) {
      const timeout = setTimeout(() => setIsDeleting(true), 2400);
      return () => clearTimeout(timeout);
    }

    if (isDeleting && displayedText === '') {
      setIsDeleting(false);
      setPhraseIndex((prev) => (prev + 1) % phrases.length);
      return;
    }

    const timeout = setTimeout(() => {
      setDisplayedText(
        isDeleting
          ? currentPhrase.substring(0, displayedText.length - 1)
          : currentPhrase.substring(0, displayedText.length + 1)
      );
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [displayedText, isDeleting, phraseIndex]);

  return (
    <section className="mb-12">
      {/* Top File Path Header (matches Screenshot 192221.png: vighriday / README.md) */}
      <div className="flex items-center space-x-2 font-mono text-xs sm:text-sm mb-2.5 opacity-80 px-1">
        <span className={isLightMode ? 'text-[#0D604B] font-semibold' : 'text-[#8DE0C1] font-semibold'}>
          Sarthaksulkhlan
        </span>
        <span className="opacity-40">/</span>
        <span className={isLightMode ? 'text-gray-600' : 'text-gray-300'}>README.md</span>
      </div>

      {/* Main Hero Card Container */}
      <div
        className={`relative overflow-hidden rounded-2xl sm:rounded-3xl border transition-all duration-300 ${
          isLightMode
            ? 'bg-[#FFFFFF] border-[#BAD6CB] shadow-[0_12px_40px_rgba(13,96,75,0.08)]'
            : 'bg-[#080D0F] border-[#1B3937] shadow-[0_16px_50px_rgba(0,0,0,0.6)]'
        }`}
      >
        {/* Subtle scanline background effect */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.035]"
          style={{
            backgroundImage:
              'repeating-linear-gradient(0deg, #000, #000 2px, transparent 2px, transparent 4px)',
          }}
        />

        {/* Ambient radial glow in emerald/cyan */}
        <div
          className={`absolute top-0 right-1/4 w-96 h-48 pointer-events-none blur-3xl opacity-20 ${
            isLightMode ? 'bg-[#47B68D]' : 'bg-[#00E5A3]'
          }`}
        />

        <div className="relative p-6 sm:p-10 md:p-12">
          {/* Top Right Status: ONLINE with glowing indicator */}
          <div className="absolute top-6 right-6 sm:top-8 sm:right-10 flex items-center space-x-2 font-mono text-xs font-semibold tracking-wider">
            <span className={isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'}>ONLINE</span>
            <span className="relative flex h-2.5 w-2.5">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isLightMode ? 'bg-[#0D604B]' : 'bg-[#00E5A3]'
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  isLightMode ? 'bg-[#0D604B]' : 'bg-[#00E5A3]'
                }`}
              />
            </span>
          </div>

          {/* Bold Name with Scanline Hatching Treatment */}
          <div className="mt-2 sm:mt-4">
            <h1
              className={`text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight select-none relative inline-block ${
                isLightMode ? 'text-[#11231F]' : 'text-[#F0F3EE]'
              }`}
              style={{
                fontFamily:
                  "'JetBrains Mono', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                letterSpacing: '-0.03em',
              }}
            >
              {/* Lined scanline texture overlay matching Screenshot 192221.png */}
              <span
                className="relative inline-block"
                style={{
                  background: isLightMode
                    ? 'linear-gradient(180deg, #11231F 0%, #1A3930 100%)'
                    : 'linear-gradient(180deg, #FFFFFF 0%, #A3C9BE 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Sarthak Sulkhlan
              </span>
            </h1>

            {/* Sub-header in uppercase with bullet separators */}
            <div
              className={`mt-3 sm:mt-4 text-xs sm:text-sm md:text-base font-mono font-semibold tracking-wider sm:tracking-widest uppercase flex flex-wrap items-center gap-2 sm:gap-3 ${
                isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'
              }`}
            >
              <span>B.Tech CSE (Data Science)</span>
              <span className="opacity-40">·</span>
              <span>Applied AI</span>
              <span className="opacity-40">·</span>
              <span>Software Systems</span>
            </div>
          </div>

          {/* Sleek Horizontal Glowing Separator with gradient beam */}
          <div className="relative my-7 sm:my-8 h-[2px] w-full max-w-2xl bg-black/10 dark:bg-white/5 overflow-hidden rounded-full">
            <div
              className={`absolute inset-0 ${
                isLightMode
                  ? 'bg-gradient-to-r from-[#0D604B]/60 via-[#47B68D] to-transparent'
                  : 'bg-gradient-to-r from-[#00E5A3] via-[#47B68D]/80 to-transparent'
              }`}
            />
            {/* Moving light pulse */}
            <div
              className={`absolute top-0 bottom-0 w-32 animate-[shimmer_3s_infinite] ${
                isLightMode ? 'bg-white/60' : 'bg-white/80'
              }`}
              style={{
                filter: 'blur(2px)',
              }}
            />
          </div>

          {/* Typewriter Prompt Area matching Screenshot 192221.png: "» Evidence be█" */}
          <div className="flex items-start sm:items-center space-x-2.5 font-mono text-base sm:text-xl min-h-[38px]">
            <span
              className={`font-bold text-lg sm:text-2xl select-none ${
                isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'
              }`}
            >
              »
            </span>
            <span
              className={`font-medium ${
                isLightMode ? 'text-[#11231F]' : 'text-[#E0ECE7]'
              }`}
            >
              {displayedText}
            </span>
            {/* Blinking Solid Block Cursor matching image */}
            <span
              className={`inline-block w-2.5 sm:w-3 h-5 sm:h-6 align-middle animate-pulse ${
                isLightMode ? 'bg-[#0D604B]' : 'bg-[#00E5A3]'
              }`}
            />
          </div>

          {/* Quick Actions Footer inside card */}
          <div className="mt-8 pt-6 border-t border-inherit flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={onExploreProjects}
                className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold flex items-center space-x-2 transition-all cursor-pointer shadow-sm ${
                  isLightMode
                    ? 'bg-[#0D604B] text-white hover:bg-[#147B61]'
                    : 'bg-[#47B68D] text-[#080D0F] hover:bg-[#8DE0C1]'
                }`}
              >
                <span>Explore Verified Work</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
              <a
                href="https://github.com/Sarthaksulkhlan"
                target="_blank"
                rel="noreferrer"
                className={`px-3 py-2 rounded-xl text-xs sm:text-sm font-mono border transition-all ${
                  isLightMode
                    ? 'border-[#BAD6CB] bg-[#F4F8F6] text-[#11231F] hover:bg-[#E2F0EA]'
                    : 'border-[#1B3937] bg-[#101B1D] text-[#F0F3EE] hover:bg-[#14272A]'
                }`}
              >
                github.com/Sarthaksulkhlan
              </a>
            </div>

            <div className="flex items-center space-x-3 text-xs font-mono opacity-75">
              <span>Verified Repos: {profileData?.public_repo_count ?? 4}</span>
              <span>·</span>
              <span>Languages: {Object.keys(profileData?.languages ?? {}).length || 9}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
