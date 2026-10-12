import React, { useState, useEffect } from 'react';
import { Header } from './components/Header.tsx';
import { HeroSection } from './components/HeroSection.tsx';
import { AboutSection } from './components/AboutSection.tsx';
import { SkillsSection } from './components/SkillsSection.tsx';
import { ProjectsSection } from './components/ProjectsSection.tsx';
import { TelemetrySection } from './components/TelemetrySection.tsx';
import { ContributionArtSection } from './components/ContributionArtSection.tsx';
import { ReadmeStudio } from './components/ReadmeStudio.tsx';
import { SystemVerifier } from './components/SystemVerifier.tsx';
import { Footer } from './components/Footer.tsx';
import { ProfileData } from './types.ts';

export default function App() {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [isLightMode, setIsLightMode] = useState<boolean>(false);
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [refreshNotice, setRefreshNotice] = useState<string | null>(null);

  const fetchProfile = () => {
    fetch('/api/profile')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.repos) {
          setProfileData(data);
        }
      })
      .catch((err) => {
        console.error('Failed to load profile data', err);
      });
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshNotice(null);
    try {
      const res = await fetch('/api/refresh', { method: 'POST' });
      const result = await res.json();
      if (result.data) {
        setProfileData(result.data);
      }
      setRefreshNotice(result.message || 'Telemetry updated');
      setTimeout(() => setRefreshNotice(null), 4000);
    } catch (err: any) {
      setRefreshNotice(`Refresh failed: ${err.message}`);
      setTimeout(() => setRefreshNotice(null), 4000);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      isLightMode
        ? 'bg-[#F4F8F6] text-[#11231F]'
        : 'bg-[#0D1214] text-[#F0F3EE]'
    }`}>
      {/* Toast Notification */}
      {refreshNotice && (
        <div className="fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-xl border shadow-xl text-xs font-mono bg-black/90 text-white border-emerald-500/50 flex items-center space-x-2 animate-bounce">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>{refreshNotice}</span>
        </div>
      )}

      {/* Main Navigation */}
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        isLightMode={isLightMode}
        setIsLightMode={setIsLightMode}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
        lastRefresh={profileData?.last_successful_refresh_utc}
      />

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {currentTab === 'overview' && (
          <div>
            <HeroSection
              isLightMode={isLightMode}
              profileData={profileData}
              onExploreProjects={() => setCurrentTab('projects')}
            />
            <TelemetrySection
              isLightMode={isLightMode}
              profileData={profileData}
              onRefresh={handleRefresh}
              isRefreshing={isRefreshing}
            />
            <ContributionArtSection isLightMode={isLightMode} />
            <AboutSection isLightMode={isLightMode} profileData={profileData} />
            <SkillsSection isLightMode={isLightMode} />
            <ProjectsSection isLightMode={isLightMode} profileData={profileData} />
          </div>
        )}

        {currentTab === 'projects' && (
          <div>
            <ProjectsSection isLightMode={isLightMode} profileData={profileData} />
            <SkillsSection isLightMode={isLightMode} />
          </div>
        )}

        {currentTab === 'telemetry' && (
          <div>
            <TelemetrySection
              isLightMode={isLightMode}
              profileData={profileData}
              onRefresh={handleRefresh}
              isRefreshing={isRefreshing}
            />
          </div>
        )}

        {currentTab === 'contribution' && (
          <div>
            <ContributionArtSection isLightMode={isLightMode} />
          </div>
        )}

        {currentTab === 'readme' && (
          <div>
            <ReadmeStudio isLightMode={isLightMode} />
          </div>
        )}

        {currentTab === 'verifier' && (
          <div>
            <SystemVerifier isLightMode={isLightMode} />
          </div>
        )}
      </main>

      <Footer isLightMode={isLightMode} />
    </div>
  );
}
