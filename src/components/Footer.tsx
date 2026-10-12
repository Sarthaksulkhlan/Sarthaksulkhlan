import React from 'react';
import { ExternalLink, Heart, Terminal } from 'lucide-react';
import { GithubIcon } from './GithubIcon.tsx';

interface FooterProps {
  isLightMode: boolean;
}

export const Footer: React.FC<FooterProps> = ({ isLightMode }) => {
  return (
    <footer className={`border-t py-8 px-4 transition-colors font-mono text-xs ${
      isLightMode
        ? 'bg-[#FFFFFF] border-[#BAD6CB] text-[#466058]'
        : 'bg-[#080D0F] border-[#285047] text-[#B3C3BE]'
    }`}>
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 opacity-75" />
          <span>Sarthak Sulkhlan · Profile Studio & Telemetry Workbench</span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs">
          <a
            href="https://github.com/Sarthaksulkhlan"
            target="_blank"
            rel="noreferrer"
            className="hover:underline flex items-center space-x-1"
          >
            <GithubIcon className="w-3.5 h-3.5" />
            <span>GitHub Profile</span>
          </a>

          <a
            href="https://github.com/Sarthaksulkhlan/Sarthaksulkhlan"
            target="_blank"
            rel="noreferrer"
            className="hover:underline flex items-center space-x-1"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Profile Source</span>
          </a>

          <span>B.Tech CSE (Data Science) · JSSATE</span>
        </div>
      </div>
      <div className="max-w-6xl mx-auto mt-4 text-[11px] opacity-60 text-center md:text-left">
        Four self-hosted GIFs provide typewriter hero, telemetry reveal, snake path, and five Pac-Man paths with static SVG fallbacks.
      </div>
    </footer>
  );
};
