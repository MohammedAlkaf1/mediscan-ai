import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import SummaryCards from '@/components/SummaryCards';
import ResultsTable from '@/components/ResultsTable';
import StatusBadge from '@/components/StatusBadge';
import ShareModal from '@/components/ShareModal';
import { getReport, downloadReportPDF, deleteReport, updateReport, Report, LabResult } from '@/lib/api';
import { useAuth } from '@/lib/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faFilePdf,
  faShareNodes,
  faPenToSquare,
  faTrashCan,
  faArrowLeft,
  faSpinner,
  faFloppyDisk,
  faXmark,
  faClipboardList,
} from '@fortawesome/free-solid-svg-icons';

/* ── helpers ─────────────────────────────────────────────────────────────── */

/** Pull the first 2–3 sentences from the AI summary */
function shortSummary(text: string): string {
  if (!text) return '';
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
  // skip "Hello" opener sentences, take first real ones
  const meaningful = sentences.filter(
    (s) => !/^(hello|hi |sure|of course|i'?m here)/i.test(s.trim())
  );
  return (meaningful.slice(0, 3).join(' ') || text.slice(0, 280)).trim();
}

/** Parse bullet lines from tips text */
function parseTips(text: string): string[] {
  if (!text) return [];
  const lines = text.split('\n').map((l) => l.replace(/^[-•*]\s*/, '').trim()).filter(Boolean);
  return lines.slice(0, 5);
}

/** Colour helpers for status */
const STATUS_COLOR: Record<string, { bg: string; text: string; dot: string }> = {
  high:    { bg: '#fef2f2', text: '#dc2626', dot: '#ef4444' },
  low:     { bg: '#eff6ff', text: '#2563eb', dot: '#3b82f6' },
  normal:  { bg: '#f0fdf4', text: '#16a34a', dot: '#22c55e' },
  unknown: { bg: '#f8fafc', text: '#64748b', dot: '#94a3b8' },
};

export default function ReportDetails() {
  const router = useRouter();
  const { id } = router.query;
  const { user, isAuthenticated } = useAuth();

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editType, setEditType] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (id && typeof id === 'string') fetchReport(id);
  }, [id]);

  const fetchReport = async (reportId: string) => {
    try {
      setLoading(true);
      const data = await getReport(reportId);
      setReport(data);
      setError(null);
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 404) setError('Report not found.');
      else if (status === 403) setError('You do not have permission to view this report.');
      else setError('Failed to load report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!report) return;
    try {
      setDownloading(true);
      setDownloadError(null);
      await downloadReportPDF(report.id);
    } catch {
      setDownloadError('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!report) return;
    try {
      setDeleting(true);
      await deleteReport(report.id);
      router.push('/reports');
    } catch {
      setError('Failed to delete report. Please try again.');
      setDeleteModalOpen(false);
    } finally {
      setDeleting(false);
    }
  };

  const openEditModal = () => {
    if (!report) return;
    setEditTitle(report.title || '');
    setEditType(report.report_type || '');
    setEditNotes(report.notes || '');
    setEditModalOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!report) return;
    try {
      setSaving(true);
      const updated = await updateReport(report.id, {
        title: editTitle || undefined,
        report_type: editType || undefined,
        notes: editNotes || undefined,
      });
      setReport(updated);
      setEditModalOpen(false);
    } catch {
      /* keep modal open */
    } finally {
      setSaving(false);
    }
  };

  /* ── Loading ──────────────────────────────────────────────────────────────── */
  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div
              className="animate-spin rounded-full h-10 w-10 border-2 border-t-transparent mx-auto mb-4"
              style={{ borderColor: '#526D82', borderTopColor: 'transparent' }}
            />
            <p className="text-sm" style={{ color: '#9DB2BF' }}>Loading report…</p>
          </div>
        </div>
      </Layout>
    );
  }

  /* ── Error ────────────────────────────────────────────────────────────────── */
  if (error || !report) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
            <h2 className="text-xl font-bold text-red-900 mb-2">Error Loading Report</h2>
            <p className="text-red-700 mb-6">{error || 'Report not found.'}</p>
            <button
              onClick={() => router.push('/reports')}
              className="px-6 py-2.5 text-white rounded-xl font-semibold"
              style={{ backgroundColor: '#526D82' }}
            >
              Back to History
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  const isOwner = isAuthenticated && report;
  const displayTitle = report.title || report.report_type || 'Medical Report';

  /* ── Derived data for explanation section ─────────────────────────────────── */
  const abnormalResults: LabResult[] = report.lab_results.filter(
    (r) => r.status === 'high' || r.status === 'low'
  );
  const summaryText  = report.explanation ? shortSummary(report.explanation.summary) : '';
  const tipsLines    = report.explanation ? parseTips(report.explanation.tips) : [];

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-4 py-6">

        {/* Back */}
        <button
          onClick={() => router.push('/reports')}
          className="mb-6 inline-flex items-center gap-2 text-sm font-medium transition-colors"
          style={{ color: '#526D82' }}
        >
          <FontAwesomeIcon icon={faArrowLeft} className="w-3.5 h-3.5" />
          Back to History
        </button>

        {/* ── Header card ──────────────────────────────────────────────────── */}
        <div className="rounded-2xl border px-6 py-5 mb-6 flex items-start justify-between flex-wrap gap-4" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
          <div>
            <h1 className="text-2xl font-bold tracking-tight mb-1" style={{ color: '#27374D' }}>
              {displayTitle}
            </h1>
            <p className="text-sm" style={{ color: '#9DB2BF' }}>
              {new Date(report.created_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric',
              })}
            </p>
            {report.notes && (
              <p className="mt-1 text-sm italic" style={{ color: '#526D82' }}>"{report.notes}"</p>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge status={report.status as any} size="lg" />

            {/* PDF */}
            <button
              onClick={handleDownloadPDF}
              disabled={downloading || report.status !== 'done'}
              className="px-4 py-2 rounded-lg text-sm font-semibold border transition-all disabled:opacity-40 flex items-center gap-2"
              style={{ borderColor: '#9DB2BF', color: '#526D82', backgroundColor: 'transparent' }}
            >
              <FontAwesomeIcon
                icon={downloading ? faSpinner : faFilePdf}
                className={`w-3.5 h-3.5 ${downloading ? 'animate-spin' : ''}`}
              />
              PDF
            </button>

            {isOwner && report.status === 'done' && (
              <button
                onClick={() => setShareModalOpen(true)}
                className="px-4 py-2 rounded-lg text-sm font-semibold border transition-all flex items-center gap-2"
                style={{ borderColor: '#9DB2BF', color: '#526D82', backgroundColor: 'transparent' }}
              >
                <FontAwesomeIcon icon={faShareNodes} className="w-3.5 h-3.5" />
                Share
              </button>
            )}

            {isOwner && (
              <button
                onClick={openEditModal}
                className="px-4 py-2 rounded-lg text-sm font-semibold border transition-all flex items-center gap-2"
                style={{ borderColor: '#9DB2BF', color: '#526D82', backgroundColor: 'transparent' }}
              >
                <FontAwesomeIcon icon={faPenToSquare} className="w-3.5 h-3.5" />
                Edit
              </button>
            )}

            {isOwner && (
              <button
                onClick={() => setDeleteModalOpen(true)}
                className="px-4 py-2 rounded-lg text-sm font-semibold border transition-all flex items-center gap-2"
                style={{ borderColor: '#fecaca', color: '#dc2626', backgroundColor: '#ffffff' }}
              >
                <FontAwesomeIcon icon={faTrashCan} className="w-3.5 h-3.5" />
                Delete
              </button>
            )}
          </div>
        </div>

        {/* Download error */}
        {downloadError && (
          <div className="mb-5 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <p className="text-sm text-red-700 font-medium flex-1">{downloadError}</p>
            <button onClick={() => setDownloadError(null)} className="text-red-400 hover:text-red-600">
              <FontAwesomeIcon icon={faXmark} className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* ── Summary cards ─────────────────────────────────────────────────── */}
        {report.lab_results && report.lab_results.length > 0 && (
          <div className="mb-6">
            <SummaryCards results={report.lab_results} />
          </div>
        )}

        {/* ── Lab results table ──────────────────────────────────────────────── */}
        <div className="rounded-2xl border mb-6 overflow-hidden" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
          <div className="px-6 py-4 border-b" style={{ backgroundColor: '#DDE6ED', borderColor: '#c5d4df' }}>
            <h2 className="text-base font-semibold" style={{ color: '#27374D' }}>Lab Results</h2>
            {report.lab_results.length > 0 && (
              <p className="text-xs mt-0.5" style={{ color: '#526D82' }}>
                {report.lab_results.length} test{report.lab_results.length !== 1 ? 's' : ''} extracted
              </p>
            )}
          </div>
          <ResultsTable results={report.lab_results} />
        </div>

        {/* ── AI Explanation — clean, short, clear ────────────────────────────── */}
        {report.explanation && (
          <div className="rounded-2xl border mb-6 overflow-hidden" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>

            {/* Section header */}
            <div
              className="px-6 py-4 border-b flex items-center gap-3"
              style={{ backgroundColor: '#DDE6ED', borderColor: '#c5d4df' }}
            >
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: '#526D82' }}
              >
                <FontAwesomeIcon icon={faClipboardList} className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-bold" style={{ color: '#27374D' }}>What Your Results Mean</h2>
                <p className="text-xs" style={{ color: '#526D82' }}>AI-generated summary · Not medical advice</p>
              </div>
            </div>

            <div className="px-6 py-5 space-y-5">

              {/* Overview — short 2-3 sentences */}
              {summaryText && (
                <p className="text-sm leading-relaxed" style={{ color: '#333' }}>
                  {summaryText}
                </p>
              )}

              {/* Key findings — only abnormal results */}
              {abnormalResults.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide mb-2" style={{ color: '#526D82' }}>
                    Values outside normal range
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {abnormalResults.map((r) => {
                      const col = STATUS_COLOR[r.status] || STATUS_COLOR.unknown;
                      return (
                        <div
                          key={r.id.toString()}
                          className="flex items-center justify-between rounded-xl px-4 py-2.5"
                          style={{ backgroundColor: col.bg }}
                        >
                          <span className="text-sm font-medium" style={{ color: '#27374D' }}>
                            {r.canonical_name || r.test_name}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold" style={{ color: '#27374D' }}>
                              {r.value_text || (r.value_numeric !== null ? String(r.value_numeric) : '—')}
                              {r.unit ? ` ${r.unit}` : ''}
                            </span>
                            <span
                              className="text-xs font-bold px-2 py-0.5 rounded-full"
                              style={{ backgroundColor: col.bg, color: col.text, border: `1px solid ${col.dot}` }}
                            >
                              {r.status.charAt(0).toUpperCase() + r.status.slice(1)}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tips — compact bullet list */}
              {tipsLines.length > 0 && (
                <div
                  className="rounded-xl px-4 py-3"
                  style={{ backgroundColor: '#DDE6ED', border: '1px solid #c5d4df' }}
                >
                  <p className="text-xs font-bold uppercase tracking-wide mb-2" style={{ color: '#526D82' }}>
                    Wellness suggestions
                  </p>
                  <ul className="space-y-1.5">
                    {tipsLines.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm" style={{ color: '#27374D' }}>
                        <span className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: '#9DB2BF' }} />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          </div>
        )}

        {/* ── Bottom actions ─────────────────────────────────────────────────── */}
        <div className="flex flex-wrap gap-3 justify-center mt-2">
          <button
            onClick={() => router.push('/')}
            className="px-7 py-3 text-white rounded-xl font-semibold text-sm transition-all shadow-sm"
            style={{ backgroundColor: '#526D82' }}
          >
            Analyse Another Report
          </button>
          <button
            onClick={() => router.push('/reports')}
            className="px-7 py-3 rounded-xl font-semibold text-sm transition-all border-2"
            style={{ borderColor: '#9DB2BF', color: '#526D82', backgroundColor: '#DDE6ED' }}
          >
            View All Reports
          </button>
        </div>
      </div>

      {/* ── Modals ─────────────────────────────────────────────────────────────── */}

      <ShareModal
        reportId={report.id}
        isOpen={shareModalOpen}
        onClose={() => setShareModalOpen(false)}
      />

      {/* Delete modal */}
      {deleteModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold mb-2" style={{ color: '#27374D' }}>Delete Report</h3>
            <p className="text-sm mb-5" style={{ color: '#526D82' }}>
              Permanently delete <strong>"{displayTitle}"</strong>? All results, explanations, and share links will be removed.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteModalOpen(false)}
                disabled={deleting}
                className="flex-1 px-4 py-2.5 rounded-xl font-semibold text-sm disabled:opacity-50 flex items-center justify-center gap-2 border-2"
                style={{ borderColor: '#DDE6ED', color: '#526D82' }}
              >
                <FontAwesomeIcon icon={faXmark} className="w-3.5 h-3.5" />
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl font-semibold text-sm disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <FontAwesomeIcon icon={deleting ? faSpinner : faTrashCan} className={`w-3.5 h-3.5 ${deleting ? 'animate-spin' : ''}`} />
                {deleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit modal */}
      {editModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold mb-5" style={{ color: '#27374D' }}>Edit Report</h3>
            <div className="space-y-4 mb-5">
              <div>
                <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide" style={{ color: '#526D82' }}>Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none text-sm"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="e.g., Annual Check-up 2025"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide" style={{ color: '#526D82' }}>Report Type</label>
                <input
                  type="text"
                  value={editType}
                  onChange={(e) => setEditType(e.target.value)}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none text-sm"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="e.g., Complete Blood Count"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide" style={{ color: '#526D82' }}>Notes</label>
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none text-sm resize-none"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="Optional personal notes…"
                />
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setEditModalOpen(false)}
                disabled={saving}
                className="flex-1 px-4 py-2.5 border-2 rounded-xl font-semibold text-sm disabled:opacity-50"
                style={{ borderColor: '#DDE6ED', color: '#526D82' }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={saving}
                className="flex-1 px-4 py-2.5 text-white rounded-xl font-semibold text-sm disabled:opacity-50 flex items-center justify-center gap-2"
                style={{ backgroundColor: '#526D82' }}
              >
                <FontAwesomeIcon icon={saving ? faSpinner : faFloppyDisk} className={`w-3.5 h-3.5 ${saving ? 'animate-spin' : ''}`} />
                {saving ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
