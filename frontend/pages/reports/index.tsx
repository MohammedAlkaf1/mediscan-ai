import React, { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import StatusBadge from '@/components/StatusBadge';
import { listReports, deleteReport, updateReport, ReportListItem } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faEye, faPenToSquare, faTrashCan, faPlus, faMagnifyingGlass,
  faSpinner, faFloppyDisk, faXmark, faFileLines, faCircleExclamation,
} from '@fortawesome/free-solid-svg-icons';

type SortKey = 'newest' | 'oldest' | 'name';
type StatusFilter = 'all' | 'done' | 'processing' | 'failed' | 'queued';

export default function ReportHistory() {
  const router = useRouter();
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search / filter / sort
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [sortKey, setSortKey] = useState<SortKey>('newest');

  // Modals
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ReportListItem | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editType, setEditType] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await listReports(100, 0);
      setReports(data);
      setError(null);
    } catch {
      setError('Failed to load reports. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Filtered + sorted reports
  const filteredReports = useMemo(() => {
    let list = [...reports];

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (r) =>
          (r.title || '').toLowerCase().includes(q) ||
          (r.report_type || '').toLowerCase().includes(q) ||
          (r.notes || '').toLowerCase().includes(q)
      );
    }

    if (statusFilter !== 'all') {
      list = list.filter((r) => r.status === statusFilter);
    }

    if (sortKey === 'newest') {
      list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } else if (sortKey === 'oldest') {
      list.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    } else if (sortKey === 'name') {
      list.sort((a, b) =>
        (a.title || a.report_type || '').localeCompare(b.title || b.report_type || '')
      );
    }

    return list;
  }, [reports, search, statusFilter, sortKey]);

  const handleDeleteClick = (r: ReportListItem) => {
    setSelectedReport(r);
    setDeleteModalOpen(true);
  };

  const handleEditClick = (r: ReportListItem) => {
    setSelectedReport(r);
    setEditTitle(r.title || '');
    setEditType(r.report_type || '');
    setEditNotes(r.notes || '');
    setEditModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!selectedReport) return;
    try {
      setActionLoading(true);
      await deleteReport(selectedReport.id);
      setReports((prev) => prev.filter((r) => r.id !== selectedReport.id));
      setDeleteModalOpen(false);
      setSelectedReport(null);
    } catch {
      setError('Failed to delete report. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  const confirmEdit = async () => {
    if (!selectedReport) return;
    try {
      setActionLoading(true);
      await updateReport(selectedReport.id, {
        title: editTitle || undefined,
        report_type: editType || undefined,
        notes: editNotes || undefined,
      });
      setReports((prev) =>
        prev.map((r) =>
          r.id === selectedReport.id
            ? { ...r, title: editTitle, report_type: editType, notes: editNotes }
            : r
        )
      );
      setEditModalOpen(false);
      setSelectedReport(null);
    } catch {
      setError('Failed to update report. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  // Status counts for filter badges
  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = { all: reports.length };
    reports.forEach((r) => {
      counts[r.status] = (counts[r.status] || 0) + 1;
    });
    return counts;
  }, [reports]);

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div
              className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4"
              style={{ borderColor: '#526D82' }}
            />
            <p style={{ color: '#9DB2BF' }}>Loading reports…</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-1" style={{ color: '#DDE6ED' }}>Report History</h1>
            <p style={{ color: '#9DB2BF' }}>
              {reports.length} report{reports.length !== 1 ? 's' : ''} total
            </p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="px-5 py-2.5 text-white rounded-xl font-semibold shadow-md transition-all flex items-center gap-2"
            style={{ backgroundColor: '#526D82' }}
          >
            <FontAwesomeIcon icon={faPlus} className="w-4 h-4" />
            Upload New Report
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <FontAwesomeIcon icon={faCircleExclamation} className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-800 font-medium">{error}</p>
            <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">
              <FontAwesomeIcon icon={faXmark} className="w-4 h-4" />
            </button>
          </div>
        )}

        {reports.length === 0 ? (
          /* Empty state */
          <div className="rounded-2xl shadow-lg p-12 text-center border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
            <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6" style={{ backgroundColor: '#9DB2BF' }}>
              <FontAwesomeIcon icon={faFileLines} className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold mb-2" style={{ color: '#27374D' }}>No Reports Yet</h3>
            <p className="mb-8 max-w-sm mx-auto" style={{ color: '#526D82' }}>
              Upload your first medical lab report to get started with AI-powered analysis.
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-8 py-3 text-white rounded-xl font-semibold shadow-md transition-all"
              style={{ backgroundColor: '#526D82' }}
            >
              Upload Your First Report
            </button>
          </div>
        ) : (
          <>
            {/* Search + filter + sort bar */}
            <div className="mb-6 space-y-4">
              {/* Search */}
              <div className="relative">
                <FontAwesomeIcon
                  icon={faMagnifyingGlass}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4"
                  style={{ color: '#9DB2BF' }}
                />
                <input
                  type="text"
                  placeholder="Search by title, type, or notes…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border rounded-xl bg-white text-sm shadow-sm focus:outline-none transition-colors"
                  style={{ borderColor: '#DDE6ED' }}
                />
                {search && (
                  <button
                    onClick={() => setSearch('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                    style={{ color: '#9DB2BF' }}
                  >
                    <FontAwesomeIcon icon={faXmark} className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Filter + sort row */}
              <div className="flex items-center gap-3 flex-wrap">
                {/* Status filter chips */}
                <div className="flex items-center gap-2 flex-wrap">
                  {(['all', 'done', 'processing', 'failed'] as StatusFilter[]).map((s) => (
                    <button
                      key={s}
                      onClick={() => setStatusFilter(s)}
                      className="px-3 py-1.5 rounded-full text-xs font-semibold capitalize transition-all border"
                      style={
                        statusFilter === s
                          ? { backgroundColor: '#526D82', color: '#ffffff', borderColor: '#526D82' }
                          : { backgroundColor: '#ffffff', color: '#526D82', borderColor: '#9DB2BF' }
                      }
                    >
                      {s} {statusCounts[s] ? `(${statusCounts[s]})` : ''}
                    </button>
                  ))}
                </div>

                {/* Sort */}
                <div className="ml-auto flex items-center gap-2">
                  <span className="text-xs font-medium" style={{ color: '#9DB2BF' }}>Sort:</span>
                  <select
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value as SortKey)}
                    className="text-sm border rounded-lg px-3 py-1.5 bg-white focus:outline-none transition-colors"
                    style={{ borderColor: '#DDE6ED', color: '#526D82' }}
                  >
                    <option value="newest">Newest first</option>
                    <option value="oldest">Oldest first</option>
                    <option value="name">By name</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Results count */}
            {search || statusFilter !== 'all' ? (
              <p className="text-sm mb-4" style={{ color: '#9DB2BF' }}>
                Showing {filteredReports.length} of {reports.length} reports
              </p>
            ) : null}

            {/* Reports table */}
            {filteredReports.length === 0 ? (
              <div className="rounded-2xl shadow-lg p-12 text-center border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                <FontAwesomeIcon icon={faFileLines} className="h-12 w-12 mx-auto mb-4" style={{ color: '#9DB2BF' }} />
                <h3 className="text-lg font-semibold mb-1" style={{ color: '#27374D' }}>No results match your search</h3>
                <p className="text-sm" style={{ color: '#9DB2BF' }}>Try adjusting the search or filters</p>
                <button
                  onClick={() => { setSearch(''); setStatusFilter('all'); }}
                  className="mt-4 text-sm font-medium hover:underline"
                  style={{ color: '#526D82' }}
                >
                  Clear all filters
                </button>
              </div>
            ) : (
              <div className="rounded-2xl shadow-lg overflow-hidden border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                <table className="min-w-full divide-y" style={{ borderColor: '#9DB2BF' }}>
                  <thead style={{ backgroundColor: '#9DB2BF' }}>
                    <tr>
                      <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>
                        Report
                      </th>
                      <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider hidden sm:table-cell" style={{ color: '#526D82' }}>
                        Date
                      </th>
                      <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider hidden md:table-cell" style={{ color: '#526D82' }}>
                        Tests
                      </th>
                      <th className="px-6 py-3.5 text-left text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>
                        Status
                      </th>
                      <th className="px-6 py-3.5 text-right text-xs font-semibold uppercase tracking-wider" style={{ color: '#526D82' }}>
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }}>
                    {filteredReports.map((report) => (
                      <tr
                        key={report.id}
                        className="transition-colors cursor-pointer group hover:bg-blue-50/20"
                        style={{ borderColor: '#DDE6ED' }}
                      >
                        <td
                          className="px-6 py-4"
                          onClick={() => router.push(`/reports/${report.id}`)}
                        >
                          <div className="font-semibold transition-colors group-hover:text-opacity-80" style={{ color: '#27374D' }}>
                            {report.title || report.report_type || 'Medical Report'}
                          </div>
                          {report.notes && (
                            <div className="text-xs italic mt-0.5 truncate max-w-xs" style={{ color: '#9DB2BF' }}>
                              {report.notes}
                            </div>
                          )}
                          {!report.title && report.report_type && (
                            <div className="text-xs mt-0.5" style={{ color: '#9DB2BF' }}>{report.report_type}</div>
                          )}
                        </td>
                        <td
                          className="px-6 py-4 hidden sm:table-cell"
                          onClick={() => router.push(`/reports/${report.id}`)}
                        >
                          <div className="text-sm" style={{ color: '#27374D' }}>
                            {new Date(report.created_at).toLocaleDateString('en-US', {
                              month: 'short', day: 'numeric', year: 'numeric',
                            })}
                          </div>
                          <div className="text-xs" style={{ color: '#9DB2BF' }}>
                            {new Date(report.created_at).toLocaleTimeString('en-US', {
                              hour: '2-digit', minute: '2-digit',
                            })}
                          </div>
                        </td>
                        <td
                          className="px-6 py-4 hidden md:table-cell"
                          onClick={() => router.push(`/reports/${report.id}`)}
                        >
                          <span className="text-sm" style={{ color: '#526D82' }}>
                            {report.result_count} test{report.result_count !== 1 ? 's' : ''}
                          </span>
                        </td>
                        <td
                          className="px-6 py-4"
                          onClick={() => router.push(`/reports/${report.id}`)}
                        >
                          <StatusBadge status={report.status as any} size="sm" />
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={(e) => { e.stopPropagation(); router.push(`/reports/${report.id}`); }}
                              className="p-2 rounded-lg transition-colors"
                              style={{ color: '#526D82' }}
                              title="View report"
                            >
                              <FontAwesomeIcon icon={faEye} className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleEditClick(report); }}
                              className="p-2 rounded-lg transition-colors"
                              style={{ color: '#526D82' }}
                              title="Edit report"
                            >
                              <FontAwesomeIcon icon={faPenToSquare} className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleDeleteClick(report); }}
                              className="p-2 rounded-lg transition-colors text-red-500 hover:bg-red-50"
                              title="Delete report"
                            >
                              <FontAwesomeIcon icon={faTrashCan} className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>

      {/* Delete confirmation modal */}
      {deleteModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold" style={{ color: '#27374D' }}>Delete Report</h3>
                <p className="text-sm" style={{ color: '#9DB2BF' }}>This action cannot be undone</p>
              </div>
            </div>
            <p className="mb-6" style={{ color: '#526D82' }}>
              Permanently delete <strong>"{selectedReport?.title || selectedReport?.report_type || 'this report'}"</strong>?
              All associated data will be removed.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => { setDeleteModalOpen(false); setSelectedReport(null); }}
                disabled={actionLoading}
                className="flex-1 px-4 py-2.5 border-2 rounded-xl font-semibold disabled:opacity-50 transition-colors"
                style={{ borderColor: '#DDE6ED', color: '#526D82' }}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={actionLoading}
                className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl font-semibold disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {actionLoading ? (
                  <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Deleting…</>
                ) : 'Delete Report'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit modal */}
      {editModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#DDE6ED' }}>
                <FontAwesomeIcon icon={faPenToSquare} className="w-6 h-6" style={{ color: '#526D82' }} />
              </div>
              <div>
                <h3 className="text-xl font-bold" style={{ color: '#27374D' }}>Edit Report</h3>
                <p className="text-sm" style={{ color: '#9DB2BF' }}>Update report information</p>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#526D82' }}>Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none transition-colors text-sm"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="e.g., Annual Check-up 2024"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#526D82' }}>Report Type</label>
                <input
                  type="text"
                  value={editType}
                  onChange={(e) => setEditType(e.target.value)}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none transition-colors text-sm"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="e.g., Complete Blood Count (CBC)"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#526D82' }}>Notes</label>
                <textarea
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2.5 border-2 rounded-xl focus:outline-none transition-colors text-sm resize-none"
                  style={{ borderColor: '#DDE6ED' }}
                  placeholder="Optional personal notes…"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => { setEditModalOpen(false); setSelectedReport(null); }}
                disabled={actionLoading}
                className="flex-1 px-4 py-2.5 border-2 rounded-xl font-semibold disabled:opacity-50 transition-colors"
                style={{ borderColor: '#DDE6ED', color: '#526D82' }}
              >
                Cancel
              </button>
              <button
                onClick={confirmEdit}
                disabled={actionLoading}
                className="flex-1 px-4 py-2.5 text-white rounded-xl font-semibold disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
                style={{ backgroundColor: '#526D82' }}
              >
                {actionLoading ? (
                  <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Saving…</>
                ) : (
                  <><FontAwesomeIcon icon={faFloppyDisk} className="w-4 h-4" /> Save Changes</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
