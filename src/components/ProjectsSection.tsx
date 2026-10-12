import React from 'react';
import { ExternalLink, Star, ArrowRight, Layers, Cpu, ShieldAlert, Sparkles } from 'lucide-react';
import { GithubIcon } from './GithubIcon.tsx';
import { ProfileData } from '../types.ts';

interface ProjectsSectionProps {
  isLightMode: boolean;
  profileData: ProfileData | null;
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({ isLightMode, profileData }) => {
  const verifiedProjects = [
    {
      id: 'epoch',
      name: 'EPOCH',
      repoName: 'epoch-software.evolution',
      eyebrow: '01 / SYSTEM EVOLUTION / HACKATHON PROTOTYPE',
      badge: 'Governed AI Workbench',
      description:
        'A governed software-evolution workbench for a watched payments service: records approved changes, checks invariants, tracks drift and incidents, and measures alternative futures at a human approval gate. The repository includes a runnable demo and guarded public console.',
      stack: ['TypeScript', 'Hono', 'React 19', 'SQLite', 'MCP'],
      domain: 'change → invariants → review',
      demoUrl: 'https://epoch-wj5b.onrender.com/',
      repoUrl: 'https://github.com/Sarthaksulkhlan/epoch-software.evolution',
      stars: 2,
      architecture: [
        'MCP (Model Context Protocol) driven change proposals',
        'Invariant enforcement before execution',
        'Counterfactual simulation engine for drift prediction',
        'Guarded human-in-the-loop approval gate',
      ],
    },
    {
      id: 'asset-sentinel',
      name: 'Asset Sentinel',
      repoName: 'Asset-Sentinel',
      eyebrow: '02 / ENDPOINT TELEMETRY / FLEET VISIBILITY',
      badge: 'Live Fleet Telemetry',
      description:
        'A Windows monitoring system that sends heartbeat, hardware, session, and foreground-application signals through a Python agent and Flask API into a Supabase PostgreSQL store and React dashboard. Its README documents an end-to-end deployment and a demo using demonstration data.',
      stack: ['Python', 'Flask', 'PostgreSQL', 'React', 'TypeScript'],
      domain: 'devices → telemetry → operations',
      demoUrl: 'https://assetsentinel.onrender.com',
      repoUrl: 'https://github.com/Sarthaksulkhlan/Asset-Sentinel',
      stars: 0,
      architecture: [
        'Lightweight Python background telemetry daemon',
        'Hardware stats (CPU, RAM, storage, process sessions)',
        'Flask API gateway ingestion pipeline',
        'Supabase PostgreSQL relational event persistence',
      ],
    },
    {
      id: 'matrixcore',
      name: 'MatrixCore',
      repoName: 'Nexis---Starforge',
      eyebrow: '03 / VOICE SYSTEMS / HACKATHON DEMO',
      badge: 'Multimodal Voice Agent',
      description:
        'An adaptive voice-agent demo with a browser client, an Express service, and a Python LiveKit agent. The documented voice path connects LiveKit, Gemini, Qdrant retrieval, and Rime speech; local use requires external service credentials.',
      stack: ['TypeScript', 'Express', 'Python', 'LiveKit', 'Gemini'],
      domain: 'voice → reasoning → response',
      demoUrl: null,
      repoUrl: 'https://github.com/Sarthaksulkhlan/Nexis---Starforge',
      stars: 0,
      architecture: [
        'WebRTC real-time audio streaming via LiveKit',
        'Google Gemini generative multimodal reasoning',
        'Semantic retrieval memory indexed in Qdrant',
        'Sub-second speech synthesis with Rime voice engine',
      ],
    },
    {
      id: 'medikiosk',
      name: 'MediKiosk',
      repoName: 'MediKiosk',
      eyebrow: '04 / INTERFACE / CLINICAL ACCESS',
      badge: 'Interactive Healthcare UI',
      description:
        'Specialized kiosk interface for automated patient check-in, triage workflow, and healthcare record management designed for responsive client-side reliability.',
      stack: ['TypeScript', 'React', 'Vite'],
      domain: 'patient → triage → admission',
      demoUrl: null,
      repoUrl: 'https://github.com/Sarthaksulkhlan/MediKiosk',
      stars: 0,
      architecture: [
        'Touch-first responsive kiosk terminal interface',
        'Type-safe patient session workflow validation',
        'Client-side state orchestration and offline resilience',
      ],
    },
  ];

  return (
    <section className="mb-10" id="projects-section">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-2">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">Selected Work & Systems</h2>
          <p className="text-xs sm:text-sm opacity-75">
            Documented repositories, architecture topologies, and verified live demos
          </p>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs opacity-80">
          <span>Total Stars: {profileData?.public_repo_stars ?? 2}</span>
          <span>·</span>
          <span>Public Repos: {profileData?.public_repo_count ?? 4}</span>
        </div>
      </div>

      <div className="space-y-6">
        {verifiedProjects.map((project) => (
          <div
            key={project.id}
            className={`p-6 sm:p-7 rounded-2xl border transition-all ${
              isLightMode
                ? 'bg-white border-[#BAD6CB] hover:border-[#147B61] shadow-sm'
                : 'bg-[#101B1D] border-[#285047] hover:border-[#8DE0C1] shadow-md'
            }`}
          >
            {/* Header info */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded border ${
                  isLightMode
                    ? 'bg-[#E2F0EA] border-[#BAD6CB] text-[#0D604B]'
                    : 'bg-[#14272A] border-[#285047] text-[#8DE0C1]'
                }`}>
                  {project.eyebrow}
                </span>
                <span className={`text-xs font-mono px-2 py-0.5 rounded ${
                  isLightMode ? 'bg-gray-100 text-gray-700' : 'bg-white/10 text-gray-300'
                }`}>
                  {project.badge}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                {project.demoUrl && (
                  <a
                    href={project.demoUrl}
                    target="_blank"
                    rel="noreferrer"
                    className={`px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-1 transition-all ${
                      isLightMode
                        ? 'bg-[#0D604B] text-white hover:bg-[#147B61]'
                        : 'bg-[#47B68D] text-[#0D1214] hover:bg-[#8DE0C1]'
                    }`}
                  >
                    <span>Live Demo</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
                <a
                  href={project.repoUrl}
                  target="_blank"
                  rel="noreferrer"
                  className={`px-3 py-1 rounded-md text-xs font-mono border flex items-center space-x-1 transition-all ${
                    isLightMode
                      ? 'border-[#BAD6CB] bg-[#F4F8F6] hover:bg-[#E2F0EA] text-[#11231F]'
                      : 'border-[#285047] bg-[#14272A] hover:bg-[#1B3937] text-[#F0F3EE]'
                  }`}
                >
                  <GithubIcon className="w-3.5 h-3.5" />
                  <span>Repo</span>
                  {project.stars > 0 && (
                    <span className="flex items-center space-x-0.5 ml-1 opacity-75">
                      <Star className="w-3 h-3 fill-current" />
                      <span>{project.stars}</span>
                    </span>
                  )}
                </a>
              </div>
            </div>

            {/* Title & Domain */}
            <div className="mb-3">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight">{project.name}</h3>
              <div className="flex items-center space-x-2 mt-1 font-mono text-xs opacity-75">
                <span className={isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'}>Domain pipeline:</span>
                <code>{project.domain}</code>
              </div>
            </div>

            {/* Description */}
            <p className={`text-sm leading-relaxed mb-4 ${
              isLightMode ? 'text-[#385249]' : 'text-[#D9E0DA]'
            }`}>
              {project.description}
            </p>

            {/* Architecture Highlights */}
            <div className={`p-4 rounded-xl border mb-4 text-xs font-mono ${
              isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#0D1214] border-[#285047]'
            }`}>
              <div className="font-semibold opacity-70 mb-2 uppercase text-[11px] tracking-wider">
                System Topology & Architecture:
              </div>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {project.architecture.map((arch, aIdx) => (
                  <li key={aIdx} className="flex items-start space-x-2">
                    <span className={`inline-block w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${
                      isLightMode ? 'bg-[#0D604B]' : 'bg-[#8DE0C1]'
                    }`} />
                    <span>{arch}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Technology Stack tags */}
            <div className="flex flex-wrap gap-1.5 items-center">
              <span className="text-xs font-mono opacity-60 mr-1">Stack:</span>
              {project.stack.map((tech, tIdx) => (
                <span
                  key={tIdx}
                  className={`text-xs px-2.5 py-0.5 rounded-md font-mono border ${
                    isLightMode
                      ? 'bg-white border-[#BAD6CB] text-[#11231F]'
                      : 'bg-[#14272A] border-[#285047] text-[#8DE0C1]'
                  }`}
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
