import React from 'react';
import { GraduationCap, Briefcase, BookOpen, Code2, CheckCircle2, MapPin } from 'lucide-react';
import { ProfileData } from '../types.ts';

interface AboutSectionProps {
  isLightMode: boolean;
  profileData: ProfileData | null;
}

export const AboutSection: React.FC<AboutSectionProps> = ({ isLightMode, profileData }) => {
  return (
    <section className="mb-10">
      <div className={`p-6 sm:p-8 rounded-2xl border ${
        isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#101B1D] border-[#285047]'
      }`}>
        <div className="flex flex-col lg:flex-row gap-8 items-start">
          {/* Portrait Column */}
          <div className="w-full lg:w-72 shrink-0 flex flex-col items-center">
            <div className={`relative p-2 rounded-2xl border shadow-lg ${
              isLightMode ? 'bg-[#E2F0EA] border-[#BAD6CB]' : 'bg-[#14272A] border-[#285047]'
            }`}>
              <img
                src="/assets/profile-portrait.png"
                alt="Stylized emerald halftone portrait of Sarthak Sulkhlan"
                className="w-56 h-auto rounded-xl object-cover"
                loading="lazy"
              />
              <div className="mt-2 text-center">
                <span className={`text-[11px] font-mono font-medium px-2 py-0.5 rounded border inline-block ${
                  isLightMode
                    ? 'bg-white border-[#BAD6CB] text-[#0D604B]'
                    : 'bg-[#101B1D] border-[#285047] text-[#8DE0C1]'
                }`}>
                  emerald halftone · 480×600
                </span>
              </div>
            </div>

            <div className={`mt-4 w-full p-3 rounded-xl border text-xs font-mono space-y-1.5 ${
              isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#0D1214] border-[#285047]'
            }`}>
              <div className="flex justify-between">
                <span className="opacity-70">Github:</span>
                <span className="font-semibold">@Sarthaksulkhlan</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">Focus:</span>
                <span className="font-semibold text-right">Data Science & Systems</span>
              </div>
              <div className="flex justify-between">
                <span className="opacity-70">Verified Repos:</span>
                <span className="font-semibold">{profileData?.public_repo_count ?? 4}</span>
              </div>
            </div>
          </div>

          {/* Details Column */}
          <div className="flex-1 space-y-6">
            <div>
              <div className="flex items-center space-x-2 font-mono text-xs opacity-75 mb-1">
                <span>sarthak@systems</span>
                <span>/</span>
                <span>about</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Computer Science & Data Science Engineer
              </h2>
              <p className={`mt-3 text-sm sm:text-base leading-relaxed ${
                isLightMode ? 'text-[#385249]' : 'text-[#D9E0DA]'
              }`}>
                I'm a computer science student who learns by building. I enjoy taking an idea through implementation,
                observing how a system behaves, and using that empirical evidence to iterate and improve it. My focus is on
                governed software evolution, reliable telemetry data pipelines, and applied generative AI systems.
              </p>
            </div>

            {/* Quick Spec Grid */}
            <div className={`grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 rounded-xl border font-mono text-xs ${
              isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#0D1214] border-[#285047]'
            }`}>
              <div className="flex items-start space-x-2">
                <span className="opacity-60 font-semibold min-w-20">STUDY:</span>
                <span>B.Tech, CSE (Data Science)</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="opacity-60 font-semibold min-w-20">PROJECTS:</span>
                <span>Verified software, telemetry, voice</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="opacity-60 font-semibold min-w-20">LEARNING:</span>
                <span>Java problem solving · Python · GenAI</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="opacity-60 font-semibold min-w-20">FOCUS:</span>
                <span>Practical, reliable software systems</span>
              </div>
            </div>

            {/* Experience & Education Dual Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Experience */}
              <div className={`p-4 rounded-xl border space-y-2 ${
                isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#14272A] border-[#285047]'
              }`}>
                <div className="flex items-center space-x-2 text-xs font-mono font-semibold tracking-wide uppercase opacity-75">
                  <Briefcase className="w-3.5 h-3.5" />
                  <span>Work Experience</span>
                </div>
                <div>
                  <h3 className="font-bold text-sm">AI Intern</h3>
                  <p className={`text-xs ${isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'}`}>
                    Prajjo HR — Canvas Technologies
                  </p>
                </div>
                <div className="flex items-center justify-between text-xs opacity-75 font-mono pt-1">
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3 h-3" />
                    <span>Noida, India</span>
                  </span>
                  <span>June 2026 – August 2026</span>
                </div>
              </div>

              {/* Education */}
              <div className={`p-4 rounded-xl border space-y-2 ${
                isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#14272A] border-[#285047]'
              }`}>
                <div className="flex items-center space-x-2 text-xs font-mono font-semibold tracking-wide uppercase opacity-75">
                  <GraduationCap className="w-3.5 h-3.5" />
                  <span>Education</span>
                </div>
                <div>
                  <h3 className="font-bold text-sm">B.Tech, CSE (Data Science)</h3>
                  <p className="text-xs opacity-85">
                    JSS Academy of Technical Education · AKTU
                  </p>
                </div>
                <div className="text-xs opacity-75 font-mono pt-1">
                  <span>2024–2028 · Coursework in DSA, DBMS, OS, Networks</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
