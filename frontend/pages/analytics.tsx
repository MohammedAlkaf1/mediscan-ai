import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import TrendChart from '@/components/TrendChart';
import { getAllTrends, getTrend, TrendOverview, TrendResult } from '@/lib/api';
import { useAuth } from '@/lib/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine } from '@fortawesome/free-solid-svg-icons';

export default function AnalyticsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [overviews, setOverviews] = useState<TrendOverview[]>([]);
  const [selectedTest, setSelectedTest] = useState<string | null>(null);
  const [trendData, setTrendData] = useState<TrendResult | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingTrend, setLoadingTrend] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [authLoading, isAuthenticated]);

  // Load available trend tests
  useEffect(() => {
    if (!isAuthenticated) return;
    const load = async () => {
      try {
        setLoadingOverview(true);
        const data = await getAllTrends();
        setOverviews(data);
        if (data.length > 0) {
          setSelectedTest(data[0].test_name);
        }
      } catch {
        setError('Failed to load analytics data.');
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, [isAuthenticated]);

  // Load trend for selected test
  useEffect(() => {
    if (!selectedTest) return;
    const load = async () => {
      try {
        setLoadingTrend(true);
        setError(null);
        const data = await getTrend(selectedTest);
        setTrendData(data);
      } catch {
        setError(`No trend data found for "${selectedTest}".`);
        setTrendData(null);
      } finally {
        setLoadingTrend(false);
      }
    };
    load();
  }, [selectedTest]);

  if (authLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-2"
            style={{ borderColor: '#526D82' }}
          />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#DDE6ED' }}>Health Trends</h1>
          <p style={{ color: '#9DB2BF' }}>
            Track how your lab values have changed across multiple reports over time.
          </p>
        </div>

        {loadingOverview ? (
          <div className="flex items-center justify-center min-h-[300px]">
            <div className="text-center">
              <div
                className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4"
                style={{ borderColor: '#526D82' }}
              />
              <p style={{ color: '#9DB2BF' }}>Loading analytics…</p>
            </div>
          </div>
        ) : overviews.length === 0 ? (
          /* Empty state */
          <div className="rounded-2xl shadow-lg p-12 text-center border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
            <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style={{ backgroundColor: '#9DB2BF' }}>
              <FontAwesomeIcon icon={faChartLine} className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold mb-3" style={{ color: '#27374D' }}>Not Enough Data Yet</h2>
            <p className="max-w-md mx-auto mb-2" style={{ color: '#526D82' }}>
              Trends require at least <strong>2 reports</strong> with the same lab test.
              Upload more reports to start seeing your health trends over time.
            </p>
            <p className="text-sm mb-8" style={{ color: '#9DB2BF' }}>
              For example, if you upload multiple CBC reports, you'll be able to track how
              your Hemoglobin, WBC, and other values change over time.
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 text-white rounded-xl font-semibold shadow-lg transition-colors"
              style={{ backgroundColor: '#526D82' }}
            >
              Upload a Report
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Test selector sidebar */}
            <div className="lg:col-span-1">
              <div className="rounded-2xl shadow-lg border overflow-hidden" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                <div className="px-4 py-3 border-b" style={{ backgroundColor: '#9DB2BF', borderColor: '#526D82' }}>
                  <h2 className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#526D82' }}>
                    Available Tests
                  </h2>
                </div>
                <ul className="divide-y" style={{ borderColor: '#DDE6ED' }}>
                  {overviews.map((o) => (
                    <li key={o.test_name}>
                      <button
                        onClick={() => setSelectedTest(o.test_name)}
                        className="w-full text-left px-4 py-3.5 text-sm transition-all border-l-4"
                        style={
                          selectedTest === o.test_name
                            ? { backgroundColor: '#DDE6ED', color: '#27374D', fontWeight: 600, borderLeftColor: '#526D82' }
                            : { color: '#526D82', borderLeftColor: 'transparent' }
                        }
                      >
                        <div className="font-medium">{o.test_name}</div>
                        <div className="text-xs mt-0.5" style={{ color: '#9DB2BF' }}>
                          {o.count} measurement{o.count !== 1 ? 's' : ''}
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 p-4 rounded-xl border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                <p className="text-xs leading-relaxed" style={{ color: '#526D82' }}>
                  <strong>💡 Tip:</strong> Upload lab reports regularly to build a richer trend
                  history. Trends help you and your doctor track progress over time.
                </p>
              </div>
            </div>

            {/* Chart area */}
            <div className="lg:col-span-3">
              {loadingTrend ? (
                <div className="rounded-2xl shadow-lg border flex items-center justify-center min-h-[300px]" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                  <div className="text-center">
                    <div
                      className="animate-spin rounded-full h-10 w-10 border-b-2 mx-auto mb-3"
                      style={{ borderColor: '#526D82' }}
                    />
                    <p className="text-sm" style={{ color: '#9DB2BF' }}>Loading trend data…</p>
                  </div>
                </div>
              ) : error ? (
                <div className="rounded-2xl shadow-lg border p-8 text-center min-h-[200px] flex items-center justify-center" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                  <p style={{ color: '#9DB2BF' }}>{error}</p>
                </div>
              ) : trendData ? (
                <div className="space-y-6">
                  {/* Chart card */}
                  <div className="rounded-2xl shadow-lg border p-6" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                    <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
                      <div>
                        <h2 className="text-xl font-bold" style={{ color: '#27374D' }}>
                          {trendData.canonical_name}
                        </h2>
                        <p className="text-sm mt-0.5" style={{ color: '#9DB2BF' }}>
                          {trendData.data_points.length} measurements over time
                        </p>
                      </div>
                      <TrendBadge trend={trendData.trend} />
                    </div>

                    <TrendChart
                      dataPoints={trendData.data_points}
                      testName={trendData.canonical_name}
                      trend={trendData.trend}
                    />
                  </div>

                  {/* Data table */}
                  <div className="rounded-2xl shadow-lg border overflow-hidden" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                    <div className="px-6 py-4 border-b" style={{ backgroundColor: '#9DB2BF', borderColor: '#526D82' }}>
                      <h3 className="font-semibold" style={{ color: '#27374D' }}>Measurement History</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y" style={{ borderColor: '#DDE6ED' }}>
                        <thead style={{ backgroundColor: '#DDE6ED' }}>
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>Date</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>Value</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>Reference</th>
                            <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                          {[...trendData.data_points].reverse().map((dp, i) => (
                            <tr key={i} className="hover:bg-gray-50">
                              <td className="px-6 py-3 text-sm" style={{ color: '#526D82' }}>
                                {dp.date
                                  ? new Date(dp.date).toLocaleDateString('en-US', {
                                      year: 'numeric', month: 'short', day: 'numeric',
                                    })
                                  : '—'}
                              </td>
                              <td className="px-6 py-3 text-sm font-semibold" style={{ color: '#27374D' }}>
                                {String(dp.value)} {dp.unit || ''}
                              </td>
                              <td className="px-6 py-3 text-sm" style={{ color: '#9DB2BF' }}>
                                {dp.ref_range || '—'}
                              </td>
                              <td className="px-6 py-3">
                                <StatusPill status={dp.status} />
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Disclaimer */}
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800">
                    ⚠️ <strong>Reminder:</strong> These trends are for informational purposes only.
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl shadow-lg border flex items-center justify-center min-h-[300px]" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                  <p style={{ color: '#9DB2BF' }}>Select a test to see its trend</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

function TrendBadge({ trend }: { trend: string }) {
  const configs: Record<string, { label: string; bg: string; color: string; icon: string }> = {
    increasing:        { label: 'Increasing',       bg: '#fffbeb', color: '#d97706', icon: '↑' },
    decreasing:        { label: 'Decreasing',       bg: '#DDE6ED', color: '#526D82', icon: '↓' },
    stable:            { label: 'Stable',           bg: '#f0fdf4', color: '#16a34a', icon: '→' },
    insufficient_data: { label: 'Not enough data',  bg: '#f8fafc', color: '#9DB2BF', icon: '…' },
  };
  const cfg = configs[trend] || configs.insufficient_data;
  return (
    <span
      className="px-3 py-1.5 rounded-full text-sm font-semibold"
      style={{ backgroundColor: cfg.bg, color: cfg.color }}
    >
      {cfg.icon} {cfg.label}
    </span>
  );
}

function StatusPill({ status }: { status: string }) {
  const styles: Record<string, { bg: string; color: string }> = {
    normal:  { bg: '#f0fdf4', color: '#16a34a' },
    high:    { bg: '#fef2f2', color: '#dc2626' },
    low:     { bg: '#eff6ff', color: '#2563eb' },
    unknown: { bg: '#f8fafc', color: '#9DB2BF' },
  };
  const s = styles[status] || styles.unknown;
  return (
    <span
      className="px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize"
      style={{ backgroundColor: s.bg, color: s.color }}
    >
      {status}
    </span>
  );
}
