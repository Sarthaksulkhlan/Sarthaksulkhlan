import React from 'react';
import { ExternalLink, Code, Database, Cpu, Wrench, CheckCircle } from 'lucide-react';

interface SkillsSectionProps {
  isLightMode: boolean;
}

export const SkillsSection: React.FC<SkillsSectionProps> = ({ isLightMode }) => {
  const skillGroups = [
    {
      title: 'LANGUAGES',
      icon: <Code className="w-4 h-4" />,
      skills: [
        { name: 'Python', slug: 'python', url: 'https://www.python.org/', note: 'Data pipelines & agent telemetry' },
        { name: 'Java (learning)', slug: 'java', url: 'https://dev.java/learn/', note: 'DSA & problem solving' },
        { name: 'JavaScript', slug: 'js', url: 'https://developer.mozilla.org/en-US/docs/Web/JavaScript', note: 'Frontend & asynchronous scripting' },
        { name: 'TypeScript', slug: 'ts', url: 'https://www.typescriptlang.org/docs/', note: 'Primary system language (75.7% source bytes)' },
      ],
    },
    {
      title: 'FRAMEWORKS & DEVELOPMENT',
      icon: <Cpu className="w-4 h-4" />,
      skills: [
        { name: 'React', slug: 'react', url: 'https://react.dev/', note: 'React 19, interactive dashboards' },
        { name: 'Flask', slug: 'flask', url: 'https://flask.palletsprojects.com/', note: 'Python telemetry APIs' },
        { name: 'Express', slug: 'express', url: 'https://expressjs.com/', note: 'Voice orchestration service' },
        { name: 'Node.js', slug: 'nodejs', url: 'https://nodejs.org/en/learn', note: 'Backend runtimes & tools' },
      ],
    },
    {
      title: 'AI & DATA SYSTEMS',
      icon: <Database className="w-4 h-4" />,
      skills: [
        { name: 'Generative AI (Gemini)', slug: 'ai', url: 'https://ai.google.dev/gemini-api/docs', note: 'Multimodal voice & context' },
        { name: 'MCP (Model Context)', slug: 'ai', url: 'https://modelcontextprotocol.io/docs', note: 'Governed protocol in EPOCH' },
        { name: 'LiveKit', slug: 'ai', url: 'https://docs.livekit.io/', note: 'Real-time WebRTC audio in MatrixCore' },
        { name: 'Qdrant', slug: 'ai', url: 'https://qdrant.tech/documentation/', note: 'Vector memory & semantic retrieval' },
      ],
    },
    {
      title: 'DATABASES & CLOUD',
      icon: <Wrench className="w-4 h-4" />,
      skills: [
        { name: 'PostgreSQL', slug: 'postgres', url: 'https://www.postgresql.org/docs/', note: 'Supabase relational storage' },
        { name: 'SQLite', slug: 'sqlite', url: 'https://www.sqlite.org/docs.html', note: 'In-process storage in EPOCH' },
        { name: 'Supabase', slug: 'supabase', url: 'https://supabase.com/docs', note: 'Managed Postgres & auth' },
        { name: 'GitHub Actions', slug: 'githubactions', url: 'https://docs.github.com/en/actions', note: 'Daily telemetry automation CI/CD' },
      ],
    },
  ];

  return (
    <section className="mb-10">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">Hands-on Engineering</h2>
          <p className="text-xs sm:text-sm opacity-75">
            Technologies backed by verified project codebases and documented systems
          </p>
        </div>
        <div className={`hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-mono ${
          isLightMode ? 'bg-white border-[#BAD6CB] text-[#0D604B]' : 'bg-[#101B1D] border-[#285047] text-[#8DE0C1]'
        }`}>
          <CheckCircle className="w-3.5 h-3.5" />
          <span>Evidence-Based Map</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {skillGroups.map((group, idx) => (
          <div
            key={idx}
            className={`p-5 rounded-2xl border transition-all ${
              isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#101B1D] border-[#285047]'
            }`}
          >
            <div className="flex items-center space-x-2 text-xs font-mono font-bold tracking-wider mb-4 opacity-80">
              {group.icon}
              <span>{group.title}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {group.skills.map((skill, sIdx) => (
                <a
                  key={sIdx}
                  href={skill.url}
                  target="_blank"
                  rel="noreferrer"
                  className={`p-3 rounded-xl border transition-all flex items-start space-x-3 group ${
                    isLightMode
                      ? 'bg-[#F4F8F6] border-[#BAD6CB] hover:bg-[#E2F0EA] hover:border-[#147B61]'
                      : 'bg-[#14272A] border-[#285047] hover:bg-[#1B3937] hover:border-[#8DE0C1]'
                  }`}
                >
                  <img
                    src={`https://skillicons.dev/icons?i=${skill.slug}&theme=dark`}
                    alt={`${skill.name} icon`}
                    className="w-8 h-8 rounded-md shrink-0 shadow-sm"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs tracking-tight truncate group-hover:underline">
                        {skill.name}
                      </span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-1" />
                    </div>
                    <p className="text-[11px] opacity-70 truncate mt-0.5 font-mono">
                      {skill.note}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
