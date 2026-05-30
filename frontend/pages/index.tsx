import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import FileUploader from '@/components/FileUploader';
import DisclaimerBox from '@/components/DisclaimerBox';
import { uploadReport, createDemoReport, getReportStatus, getDashboardStats, DashboardStats } from '@/lib/api';
import { useAuth } from '@/lib/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faMagnifyingGlass,
  faChartBar,
  faLightbulb,
  faBolt,
  faCircleExclamation,
  faXmark,
} from '@fortawesome/free-solid-svg-icons';

const DISCLAIMER =
  'MediScan AI is for educational and informational purposes only. It does not provide medical diagnosis, treatment, or professional medical advice. Always consult a licensed healthcare professional before making any health-related decisions.';

// Processing step messages
const STEPS = [
  { key: 'uploading',    label: 'Uploading report…',         icon: '📤' },
  { key: 'extracting',   label: 'Extracting text (OCR)…',    icon: '🔍' },
  { key: 'parsing',      label: 'Parsing lab results…',      icon: '🧪' },
  { key: 'ai',           label: 'Generating AI explanation…', icon: '🤖' },
  { key: 'finalizing',   label: 'Finalizing report…',        icon: '✅' },
];

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [saveReport, setSaveReport] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Load dashboard stats and auto-refresh every 30 s
  useEffect(() => {
    const loadStats = async () => {
      try {
        setStatsLoading(true);
        const data = await getDashboardStats();
        setStats(data);
      } catch {
        // Stats are optional – don't block the page
      } finally {
        setStatsLoading(false);
      }
    };
    loadStats();
    const interval = setInterval(loadStats, 30_000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = async (file: File) => {
    setError(null);
    setLoading(true);
    setStepIndex(0);

    try {
      // Step 1 – upload
      const response = await uploadReport(file, saveReport);
      setStepIndex(1);

      // Poll until done
      await pollReportStatus(response.id);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Upload failed. Please try again.';
      setError(msg);
      setLoading(false);
    }
  };

  const pollReportStatus = async (reportId: string) => {
    const maxAttempts = 90; // 90s timeout
    let attempts = 0;

    const stepTimers = [
      setTimeout(() => setStepIndex(2), 3000),
      setTimeout(() => setStepIndex(3), 8000),
      setTimeout(() => setStepIndex(4), 15000),
    ];

    const clearTimers = () => stepTimers.forEach(clearTimeout);

    const check = async (): Promise<void> => {
      try {
        const status = await getReportStatus(reportId);

        if (status.status === 'done') {
          clearTimers();
          setStepIndex(4);
          setTimeout(() => router.push(`/reports/${reportId}`), 500);
        } else if (status.status === 'failed') {
          clearTimers();
          setError(status.error_message || 'Processing failed. Please try again.');
          setLoading(false);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(check, 1000);
        } else {
          clearTimers();
          setError('Processing is taking longer than expected. Please check the History page.');
          setLoading(false);
        }
      } catch {
        clearTimers();
        setError('Lost connection while processing. Please check the History page.');
        setLoading(false);
      }
    };

    await check();
  };

  const handleDemoReport = async () => {
    setError(null);
    setLoading(true);
    setStepIndex(0);
    try {
      const report = await createDemoReport();
      router.push(`/reports/${report.id}`);
    } catch {
      setError('Failed to create demo report. Please try again.');
      setLoading(false);
    }
  };

  const statItems = [
    {
      label: 'Total Reports',
      value: stats?.total_reports ?? '–',
      icon: '📋',
      bg: '#DDE6ED',
      textColor: '#27374D',
    },
    {
      label: 'Normal Results',
      value: stats?.result_counts.normal ?? '–',
      icon: '✅',
      bg: '#f0fdf4',
      textColor: '#16a34a',
    },
    {
      label: 'High Results',
      value: stats?.result_counts.high ?? '–',
      icon: '⬆️',
      bg: '#fef2f2',
      textColor: '#dc2626',
    },
    {
      label: 'Low Results',
      value: stats?.result_counts.low ?? '–',
      icon: '⬇️',
      bg: '#fffbeb',
      textColor: '#d97706',
    },
  ];

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* ── Hero ─────────────────────────────────────────────────────────── */}
        <div className="text-center mb-10">
          <div className="inline-block mb-4">
            <span
              className="px-4 py-1.5 rounded-full text-sm font-semibold shadow-sm"
              style={{ backgroundColor: '#DDE6ED', color: '#526D82' }}
            >
              AI-Powered Lab Report Analysis
            </span>
          </div>
          <h2 className="text-5xl font-extrabold mb-4 tracking-tight leading-tight" style={{ color: '#DDE6ED' }}>
            Understand Your
            <span style={{ color: '#9DB2BF' }}> Lab Results</span>
          </h2>
          <p className="text-xl max-w-2xl mx-auto leading-relaxed" style={{ color: '#9DB2BF' }}>
            Upload your medical lab report and receive instant AI-powered explanations
            with colour-coded results and personalised health insights.
          </p>
        </div>

        {/* ── Stats row ─────────────────────────────────────────────────────── */}
        {(stats || statsLoading) && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {statItems.map((item) => (
              <div
                key={item.label}
                className="rounded-2xl p-5 flex flex-col items-center text-center shadow-sm"
                style={{ backgroundColor: item.bg }}
              >
                <span className="text-2xl mb-1">{item.icon}</span>
                <span className="text-3xl font-bold" style={{ color: item.textColor }}>
                  {statsLoading ? (
                    <span className="inline-block w-8 h-6 bg-gray-200 animate-pulse rounded" />
                  ) : (
                    item.value
                  )}
                </span>
                <span className="text-xs font-medium mt-1" style={{ color: '#526D82' }}>{item.label}</span>
              </div>
            ))}
          </div>
        )}

        {/* ── Upload card ──────────────────────────────────────────────────── */}
        <div className="rounded-2xl shadow-xl p-8 mb-6 border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
          <h3 className="text-lg font-semibold mb-5 flex items-center gap-2" style={{ color: '#27374D' }}>
            <span className="text-xl">📤</span> Upload Lab Report
          </h3>
          <FileUploader onFileSelect={handleFileSelect} loading={loading} />

          {/* Processing steps */}
          {loading && (
            <div className="mt-6 space-y-2">
              {STEPS.map((step, i) => (
                <div
                  key={step.key}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-500"
                  style={
                    i === stepIndex
                      ? { backgroundColor: '#DDE6ED', border: '1px solid #9DB2BF' }
                      : { opacity: i < stepIndex ? 0.5 : 0.3 }
                  }
                >
                  <span className="text-lg flex-shrink-0">
                    {i < stepIndex ? '✅' : i === stepIndex ? (
                      <span className="inline-block animate-pulse">{step.icon}</span>
                    ) : step.icon}
                  </span>
                  <span
                    className="text-sm font-medium"
                    style={{ color: i === stepIndex ? '#27374D' : '#9DB2BF' }}
                  >
                    {step.label}
                  </span>
                  {i === stepIndex && (
                    <div
                      className="ml-auto w-4 h-4 border-2 border-t-transparent rounded-full animate-spin flex-shrink-0"
                      style={{ borderColor: '#526D82', borderTopColor: 'transparent' }}
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Save option */}
          {!loading && (
            <div className="mt-5 flex items-center gap-2">
              <input
                type="checkbox"
                id="saveReport"
                checked={saveReport}
                onChange={(e) => setSaveReport(e.target.checked)}
                className="w-4 h-4 rounded"
                style={{ accentColor: '#526D82' }}
              />
              <label htmlFor="saveReport" className="text-sm select-none cursor-pointer" style={{ color: '#526D82' }}>
                Keep the uploaded file after processing{' '}
                <span style={{ color: '#9DB2BF' }}>(default: deleted for privacy)</span>
              </label>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-5 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
              <FontAwesomeIcon icon={faCircleExclamation} className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800 font-medium">{error}</p>
              <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600 flex-shrink-0">
                <FontAwesomeIcon icon={faXmark} className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Demo button */}
        <div className="text-center mb-12">
          <button
            onClick={handleDemoReport}
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-3 border-2 shadow-sm text-base font-semibold rounded-xl transition-all disabled:opacity-50"
            style={{ borderColor: '#9DB2BF', color: '#DDE6ED', backgroundColor: 'transparent' }}
          >
            <FontAwesomeIcon icon={faBolt} className="w-5 h-5" style={{ color: '#9DB2BF' }} />
            Try Demo Report
          </button>
          <p className="mt-2 text-sm" style={{ color: '#9DB2BF' }}>See how it works with sample data — no upload needed</p>
        </div>

        {/* Medical disclaimer */}
        <div className="mb-10">
          <DisclaimerBox message={DISCLAIMER} />
        </div>

        {/* ── Feature cards ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'Smart OCR',
              desc: 'Advanced AI extracts text from images and PDFs automatically, even from scanned documents.',
              icon: faMagnifyingGlass,
              iconBg: '#526D82',
            },
            {
              title: 'Color-Coded Results',
              desc: 'Instantly see which values are normal, high, or low with intuitive color indicators.',
              icon: faChartBar,
              iconBg: '#9DB2BF',
            },
            {
              title: 'AI Explanations',
              desc: 'Receive personalised, easy-to-understand explanations of your lab results powered by Gemini AI.',
              icon: faLightbulb,
              iconBg: '#27374D',
            },
          ].map((card) => (
            <div
              key={card.title}
              className="text-center p-6 rounded-2xl shadow-sm border hover:shadow-lg transition-all duration-300 group"
              style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}
            >
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300"
                style={{ backgroundColor: card.iconBg }}
              >
                <FontAwesomeIcon icon={card.icon} className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-bold mb-2" style={{ color: '#27374D' }}>{card.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#526D82' }}>{card.desc}</p>
            </div>
          ))}
        </div>

        {/* Quick navigation for authenticated users */}
        {isAuthenticated && stats && stats.total_reports > 0 && (
          <div
            className="mt-8 rounded-2xl p-6 text-white"
            style={{ backgroundColor: '#526D82' }}
          >
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h3 className="text-xl font-bold mb-1">You have {stats.total_reports} report{stats.total_reports !== 1 ? 's' : ''}</h3>
                <p className="text-sm" style={{ color: '#DDE6ED' }}>
                  View your history or track health trends over time
                </p>
              </div>
              <div className="flex gap-3 flex-wrap">
                <button
                  onClick={() => router.push('/reports')}
                  className="px-5 py-2.5 rounded-xl font-semibold text-sm shadow-md transition-colors"
                  style={{ backgroundColor: '#DDE6ED', color: '#27374D' }}
                >
                  View History →
                </button>
                <button
                  onClick={() => router.push('/analytics')}
                  className="px-5 py-2.5 rounded-xl font-semibold text-sm transition-colors border"
                  style={{ backgroundColor: 'transparent', color: '#DDE6ED', borderColor: '#9DB2BF' }}
                >
                  Trends & Analytics →
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
