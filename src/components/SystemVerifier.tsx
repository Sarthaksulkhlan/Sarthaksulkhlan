import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Terminal, Check } from 'lucide-react';
import { VerifyResult } from '../types.ts';

interface SystemVerifierProps {
  isLightMode: boolean;
}

export const SystemVerifier: React.FC<SystemVerifierProps> = ({ isLightMode }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<VerifyResult | null>(null);

  const runVerification = () => {
    setLoading(true);
    fetch('/api/verify', { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        setResult(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    runVerification();
  }, []);

  return (
    <section className="mb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight">System Integrity Verifier</h2>
          <p className="text-xs sm:text-sm opacity-75">
            Automated verification suite conforming to verify_readme.py and GitHub verify.yml workflow
          </p>
        </div>

        <button
          onClick={runVerification}
          disabled={loading}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-mono font-semibold flex items-center space-x-2 transition-all cursor-pointer ${
            isLightMode
              ? 'bg-[#0D604B] text-white hover:bg-[#147B61]'
              : 'bg-[#47B68D] text-[#0D1214] hover:bg-[#8DE0C1]'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Running Suite...' : 'Re-run Diagnostics'}</span>
        </button>
      </div>

      <div className={`p-6 sm:p-7 rounded-2xl border ${
        isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#101B1D] border-[#285047]'
      }`}>
        {/* Overall Status Banner */}
        <div className={`p-4 rounded-xl border mb-6 flex items-center justify-between ${
          result?.verified
            ? isLightMode
              ? 'bg-[#E2F0EA] border-[#BAD6CB] text-[#0D604B]'
              : 'bg-[#14272A] border-[#285047] text-[#8DE0C1]'
            : 'bg-red-500/10 border-red-500/30 text-red-400'
        }`}>
          <div className="flex items-center space-x-3">
            {result?.verified ? (
              <ShieldCheck className="w-6 h-6 shrink-0" />
            ) : (
              <XCircle className="w-6 h-6 shrink-0" />
            )}
            <div>
              <div className="font-bold text-sm sm:text-base font-mono">
                {result?.verified ? 'ALL INTEGRITY CHECKS PASSED' : 'DIAGNOSTIC ISSUES DETECTED'}
              </div>
              <div className="text-xs opacity-85">
                {result?.verified
                  ? 'All generated markers, asset binaries, schema rules, and contrast ratios are compliant.'
                  : 'Review the failing checks below.'}
              </div>
            </div>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-black/10">
            {result?.checks.filter((c) => c.status === 'pass').length ?? 0} / {result?.checks.length ?? 0} PASS
          </span>
        </div>

        {/* Diagnostic Checklist */}
        <div className="space-y-3 font-mono text-xs">
          {result?.checks.map((check, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border flex items-start space-x-3 transition-all ${
                isLightMode ? 'bg-[#F4F8F6] border-[#BAD6CB]' : 'bg-[#0D1214] border-[#285047]'
              }`}
            >
              {check.status === 'pass' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              ) : check.status === 'warn' ? (
                <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm tracking-tight">{check.check}</span>
                  <span className={`text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded ${
                    check.status === 'pass'
                      ? 'bg-emerald-500/15 text-emerald-500'
                      : check.status === 'warn'
                        ? 'bg-amber-500/15 text-amber-500'
                        : 'bg-red-500/15 text-red-500'
                  }`}>
                    {check.status}
                  </span>
                </div>
                <p className="opacity-75 text-xs mt-1 font-sans">{check.detail}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Verification Command Info */}
        <div className={`mt-6 p-4 rounded-xl border text-xs font-mono space-y-2 ${
          isLightMode ? 'bg-[#E2F0EA]/50 border-[#BAD6CB]' : 'bg-[#14272A]/50 border-[#285047]'
        }`}>
          <div className="flex items-center space-x-2 font-semibold">
            <Terminal className="w-3.5 h-3.5" />
            <span>Workflow Equivalent Commands:</span>
          </div>
          <div className="opacity-75 space-y-1">
            <p>• <code>node server.ts</code> — boots dev & API server with verified assets</p>
            <p>• <code>POST /api/verify</code> — executes marker, schema, and asset integrity validation</p>
            <p>• <code>POST /api/refresh</code> — updates cached data from GitHub public REST API</p>
          </div>
        </div>
      </div>
    </section>
  );
};
