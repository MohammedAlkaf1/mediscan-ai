import axios, { AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ── Types ────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LabResult {
  id: string;
  test_name: string;
  canonical_name: string;
  value_numeric: number | null;
  value_text: string;
  unit: string | null;
  ref_low: number | null;
  ref_high: number | null;
  ref_text: string | null;
  status: 'normal' | 'high' | 'low' | 'unknown';
}

export interface Explanation {
  summary: string;
  tips: string;
  disclaimer: string;
}

export interface Report {
  id: string;
  status: 'queued' | 'processing' | 'done' | 'failed';
  report_type: string | null;
  title: string | null;
  notes: string | null;
  created_at: string;
  processed_at: string | null;
  lab_results: LabResult[];
  explanation: Explanation | null;
}

export interface ReportListItem {
  id: string;
  status: string;
  report_type: string | null;
  title: string | null;
  notes: string | null;
  created_at: string;
  result_count: number;
}

export interface ReportStatus {
  id: string;
  status: string;
  error_message: string | null;
}

export interface ShareLink {
  id: string;
  share_token: string;
  share_url: string;
  expires_at: string | null;
  max_access: number | null;
  access_count: number;
  is_password_protected: boolean;
  is_active: boolean;
}

export interface ShareLinkCreate {
  expires_in_days: number;
  max_access?: number | null;
  password?: string | null;
}

export interface TrendDataPoint {
  date: string | null;
  value: number | string;
  unit: string | null;
  status: string;
  ref_range: string | null;
  report_id: string;
}

export interface TrendResult {
  test_name: string;
  canonical_name: string;
  data_points: TrendDataPoint[];
  trend: 'increasing' | 'decreasing' | 'stable' | 'insufficient_data';
}

export interface TrendOverview {
  test_name: string;
  count: number;
}

export interface DashboardStats {
  total_reports: number;
  done_reports: number;
  result_counts: {
    normal: number;
    high: number;
    low: number;
    unknown: number;
  };
}

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Token helpers ─────────────────────────────────────────────────────────────

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    if (typeof window !== 'undefined') localStorage.setItem('authToken', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    if (typeof window !== 'undefined') localStorage.removeItem('authToken');
  }
};

// Restore token on module load (client-side only)
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('authToken');
  if (token) setAuthToken(token);
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const register = async (data: RegisterData): Promise<User> => {
  const res = await api.post<User>('/api/auth/register', data);
  return res.data;
};

export const login = async (credentials: LoginCredentials): Promise<AuthToken> => {
  const res = await api.post<AuthToken>('/api/auth/login', credentials);
  return res.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const res = await api.get<User>('/api/auth/me');
  return res.data;
};

export const logout = () => setAuthToken(null);

// ── Reports ───────────────────────────────────────────────────────────────────

export const uploadReport = async (file: File, saveReport = false): Promise<ReportStatus> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('save_report', saveReport.toString());
  const res = await api.post<ReportStatus>('/api/reports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const getReportStatus = async (reportId: string): Promise<ReportStatus> => {
  const res = await api.get<ReportStatus>(`/api/reports/${reportId}/status`);
  return res.data;
};

export const getReport = async (reportId: string): Promise<Report> => {
  const res = await api.get<Report>(`/api/reports/${reportId}`);
  return res.data;
};

export const listReports = async (limit = 50, offset = 0): Promise<ReportListItem[]> => {
  const res = await api.get<ReportListItem[]>('/api/reports', { params: { limit, offset } });
  return res.data;
};

export const createDemoReport = async (): Promise<Report> => {
  const res = await api.post<Report>('/api/reports/demo');
  return res.data;
};

export const updateReport = async (
  reportId: string,
  data: { report_type?: string; title?: string; notes?: string }
): Promise<Report> => {
  const res = await api.put<Report>(`/api/reports/${reportId}`, data);
  return res.data;
};

export const deleteReport = async (reportId: string): Promise<void> => {
  await api.delete(`/api/reports/${reportId}`);
};

export const downloadReportPDF = async (reportId: string): Promise<void> => {
  const res = await api.get(`/api/reports/${reportId}/pdf`, { responseType: 'blob' });
  const blob = new Blob([res.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `mediscan_report_${reportId.slice(0, 8)}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// ── Sharing ───────────────────────────────────────────────────────────────────

export const createShareLink = async (
  reportId: string,
  data: ShareLinkCreate
): Promise<ShareLink> => {
  const res = await api.post<ShareLink>(`/api/reports/${reportId}/share`, data);
  return res.data;
};

export const listShareLinks = async (reportId: string): Promise<ShareLink[]> => {
  const res = await api.get<ShareLink[]>(`/api/reports/${reportId}/shares`);
  return res.data;
};

export const revokeShareLink = async (reportId: string, shareToken: string): Promise<void> => {
  await api.delete(`/api/reports/${reportId}/share/${shareToken}`);
};

export const getSharedReport = async (
  shareToken: string,
  password?: string
): Promise<Report> => {
  const params = password ? { password } : {};
  const res = await api.get<Report>(`/api/shared/${shareToken}`, { params });
  return res.data;
};

// ── Trends ────────────────────────────────────────────────────────────────────

export const getAllTrends = async (): Promise<TrendOverview[]> => {
  const res = await api.get<TrendOverview[]>('/api/trends');
  return res.data;
};

export const getTrend = async (testName: string): Promise<TrendResult> => {
  const res = await api.get<TrendResult>(`/api/trends/${encodeURIComponent(testName)}`);
  return res.data;
};

// ── Dashboard stats ───────────────────────────────────────────────────────────

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const res = await api.get<DashboardStats>('/api/stats');
  return res.data;
};

// ── Health check ──────────────────────────────────────────────────────────────

export const healthCheck = async (): Promise<{ status: string }> => {
  const res = await api.get('/health');
  return res.data;
};

export default api;
