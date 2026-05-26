import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import StatusBadge from '@/components/StatusBadge';
import ResultsTable from '@/components/ResultsTable';
import SummaryCards from '@/components/SummaryCards';
import DisclaimerBox from '@/components/DisclaimerBox';
import { getSharedReport, downloadReportPDF, Report } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faLock,
  faCircleXmark,
  faFileArrowDown,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons';

const MEDICAL_DISCLAIMER =
  'MediScan AI is for educational and informational purposes only. It does not provide medical diagnosis, treatment, or professional medical advice. Always consult a licensed healthcare professional before making any health-related decisions.';

export default function SharedReportPage() {
  const router = useRouter();
  const { token } = router.query;

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [needsPassword, setNeedsPassword] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    if (token && typeof token === 'string') {
      fetchSharedReport(token);
    }
  }, [token]);

  const fetchSharedReport = async (shareToken: string, pwd?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSharedReport(shareToken, pwd);
      setReport(data);
      setNeedsPassword(false);
    } catch (err: any) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail || '';

      if (status === 403 && detail.toLowerCase().includes('password')) {
        setNeedsPassword(true);
        if (pwd) setPasswordError('Incorrect password. Please try again.');
      } else if (status === 403) {
        setError('This share link has expired, been revoked, or has reached its access limit.');
      } else if (status === 404) {
        setError('Share link not found.');
      } else {
        setError('Failed to load shared report. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) return;
    setPasswordError(null);
    fetchSharedReport(token as string, password);
  };

  const handleDownloadPDF = async () => {
    if (!report) return;
    try {
      setDownloading(true);
      await downloadReportPDF(report.id);
    } catch {
      // silent
    } finally {
      setDownloading(false);
    }
  };

  // ── Password gate ─────────────────────────────────────────────────────────
  if (!loading && needsPassword) {
    return (
      <>
        <Head><title>Protected Report – MediScan AI</title></Head>
        <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: '#27374D' }}>
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-8 text-center" style={{ border: '1px solid #DDE6ED' }}>
            <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: '#DDE6ED' }}>
              <FontAwesomeIcon icon={faLock} className="w-8 h-8" style={{ color: '#526D82' }} />
            </div>
            <h2 className="text-2xl font-bold mb-2" style={{ color: '#27374D' }}>Password Protected</h2>
            <p className="mb-6" style={{ color: '#526D82' }}>This report is password-protected. Enter the password to view it.</p>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full px-4 py-3 border-2 rounded-xl focus:outline-none transition-colors"
                style={{ borderColor: '#DDE6ED' }}
                autoFocus
              />
              {passwordError && (
                <p className="text-sm text-red-600 text-left">{passwordError}</p>
              )}
              <button
                type="submit"
                className="w-full py-3 text-white rounded-xl font-semibold transition-colors"
                style={{ backgroundColor: '#526D82' }}
              >
                View Report
              </button>
            </form>
          </div>
        </div>
      </>
    );
  }

  // ── Loading ───────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <>
        <Head><title>Loading Report – MediScan AI</title></Head>
        <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#27374D' }}>
          <div className="text-center">
            <div
              className="animate-spin rounded-full h-14 w-14 border-b-2 mx-auto mb-4"
              style={{ borderColor: '#526D82' }}
            />
            <p className="font-medium" style={{ color: '#9DB2BF' }}>Loading shared report…</p>
          </div>
        </div>
      </>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <>
        <Head><title>Link Error – MediScan AI</title></Head>
        <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: '#27374D' }}>
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-8 text-center" style={{ border: '1px solid #DDE6ED' }}>
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FontAwesomeIcon icon={faCircleXmark} className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold mb-2" style={{ color: '#27374D' }}>Link Unavailable</h2>
            <p className="mb-6" style={{ color: '#526D82' }}>{error}</p>
            <a
              href="/"
              className="inline-block px-6 py-2.5 text-white rounded-xl font-semibold transition-colors"
              style={{ backgroundColor: '#526D82' }}
            >
              Go to MediScan AI
            </a>
          </div>
        </div>
      </>
    );
  }

  if (!report) return null;

  // ── Report view ───────────────────────────────────────────────────────────
  return (
    <>
      <Head>
        <title>
          {report.title || report.report_type || 'Lab Report'} – MediScan AI (Shared)
        </title>
      </Head>
      <div className="min-h-screen" style={{ backgroundColor: '#27374D' }}>
        {/* Shared banner */}
        <div
          className="text-white py-3 px-4 text-center text-sm font-medium"
          style={{ backgroundColor: '#526D82' }}
        >
          <span className="mr-2">🔗</span>
          You are viewing a shared read-only report via MediScan AI
          <a href="/" className="ml-4 underline hover:no-underline" style={{ color: '#DDE6ED' }}>
            Try MediScan AI →
          </a>
        </div>

        {/* Header */}
        <header className="bg-white border-b shadow-sm" style={{ borderColor: '#DDE6ED' }}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: '#526D82' }}
              >
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 20 20">
                  <rect x="8.5" y="3" width="3" height="14" rx="1.2" fill="white" />
                  <rect x="3" y="8.5" width="14" height="3" rx="1.2" fill="white" />
                </svg>
              </div>
              <div>
                <span className="font-bold" style={{ color: '#27374D' }}>MediScan AI</span>
                <span
                  className="ml-2 px-2 py-0.5 text-xs rounded-full font-medium"
                  style={{ backgroundColor: '#DDE6ED', color: '#526D82' }}
                >
                  Shared Report
                </span>
              </div>
            </div>
            <a
              href="/"
              className="hidden sm:block px-4 py-2 text-white rounded-lg text-sm font-medium transition-colors"
              style={{ backgroundColor: '#526D82' }}
            >
              Analyse Your Reports →
            </a>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Disclaimer */}
          <DisclaimerBox message={MEDICAL_DISCLAIMER} />

          {/* Title row */}
          <div className="mt-6 mb-8 flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2" style={{ color: '#DDE6ED' }}>
                {report.title || report.report_type || 'Medical Lab Report'}
              </h1>
              <p style={{ color: '#9DB2BF' }}>
                Generated on {new Date(report.created_at).toLocaleDateString('en-US', {
                  year: 'numeric', month: 'long', day: 'numeric',
                })}
              </p>
              {report.notes && (
                <p className="mt-1 italic" style={{ color: '#9DB2BF' }}>"{report.notes}"</p>
              )}
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <StatusBadge status={report.status as any} size="lg" />
              <button
                onClick={handleDownloadPDF}
                disabled={downloading || report.status !== 'done'}
                className="px-4 py-2 border-2 rounded-lg font-semibold text-sm disabled:opacity-50 transition-all flex items-center gap-2"
                style={{ borderColor: '#526D82', color: '#526D82', backgroundColor: '#ffffff' }}
              >
                <FontAwesomeIcon
                  icon={downloading ? faSpinner : faFileArrowDown}
                  className={`w-4 h-4 ${downloading ? 'animate-spin' : ''}`}
                />
                {downloading ? 'Downloading…' : 'Download PDF'}
              </button>
            </div>
          </div>

          {/* Summary cards */}
          {report.lab_results.length > 0 && (
            <div className="mb-8">
              <SummaryCards results={report.lab_results} />
            </div>
          )}

          {/* Results table */}
          <div className="rounded-xl shadow-lg mb-8 overflow-hidden" style={{ backgroundColor: '#DDE6ED', border: '1px solid #9DB2BF' }}>
            <div className="px-6 py-4 border-b" style={{ backgroundColor: '#DDE6ED', borderColor: '#c5d4df' }}>
              <h2 className="text-xl font-semibold" style={{ color: '#27374D' }}>Lab Results</h2>
            </div>
            <ResultsTable results={report.lab_results} />
          </div>

          {/* AI explanation */}
          {report.explanation && (
            <>
              {report.explanation.summary && (
                <div className="rounded-2xl shadow-lg p-8 mb-6 border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                  <div className="flex items-start gap-3 mb-5">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: '#DDE6ED' }}
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: '#526D82' }}>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold" style={{ color: '#27374D' }}>Understanding Your Results</h2>
                      <p className="text-sm" style={{ color: '#9DB2BF' }}>AI-generated educational explanation</p>
                    </div>
                  </div>
                  <div className="leading-relaxed whitespace-pre-line" style={{ color: '#526D82' }}>
                    {report.explanation.summary}
                  </div>
                </div>
              )}

              {report.explanation.tips && (
                <div className="rounded-2xl shadow-lg p-8 mb-6 border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                  <div className="flex items-start gap-3 mb-5">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: '#526D82' }}
                    >
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold" style={{ color: '#27374D' }}>Wellness Tips</h2>
                      <p className="text-sm" style={{ color: '#526D82' }}>General lifestyle suggestions based on these results</p>
                    </div>
                  </div>
                  <div className="leading-relaxed whitespace-pre-line" style={{ color: '#27374D' }}>
                    {report.explanation.tips}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Disclaimer footer */}
          <div className="mt-8 p-6 bg-amber-50 border-2 border-amber-200 rounded-2xl">
            <div className="flex items-start gap-3">
              <span className="text-2xl flex-shrink-0">⚠️</span>
              <div>
                <h3 className="font-bold text-amber-900 mb-1">Medical Disclaimer</h3>
                <p className="text-amber-800 text-sm leading-relaxed">{MEDICAL_DISCLAIMER}</p>
              </div>
            </div>
          </div>
        </main>

        <footer className="border-t bg-white mt-12 py-6 text-center text-sm" style={{ borderColor: '#DDE6ED', color: '#9DB2BF' }}>
          <p>
            Powered by{' '}
            <a href="/" className="font-medium hover:underline" style={{ color: '#526D82' }}>MediScan AI</a>
            {' '} · For educational use only · Not medical advice
          </p>
        </footer>
      </div>
    </>
  );
}
