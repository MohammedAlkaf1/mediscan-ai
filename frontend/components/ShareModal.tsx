import React, { useState, useEffect } from 'react';
import { createShareLink, listShareLinks, revokeShareLink, ShareLink } from '@/lib/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faShareNodes,
  faXmark,
  faPlus,
  faCopy,
  faCheck,
  faTrashCan,
  faSpinner,
  faLock,
} from '@fortawesome/free-solid-svg-icons';

interface ShareModalProps {
  reportId: string;
  isOpen: boolean;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ reportId, isOpen, onClose }) => {
  const [shares, setShares] = useState<ShareLink[]>([]);
  const [loadingShares, setLoadingShares] = useState(false);
  const [creating, setCreating] = useState(false);
  const [expiryDays, setExpiryDays] = useState(7);
  const [password, setPassword] = useState('');
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadShares();
      setError(null);
      setSuccessMessage(null);
    }
  }, [isOpen]);

  const loadShares = async () => {
    try {
      setLoadingShares(true);
      const data = await listShareLinks(reportId);
      setShares(data);
    } catch {
      setShares([]);
    } finally {
      setLoadingShares(false);
    }
  };

  const handleCreate = async () => {
    try {
      setCreating(true);
      setError(null);
      const link = await createShareLink(reportId, {
        expires_in_days: expiryDays,
        password: password.trim() || null,
      });
      setShares((prev) => [...prev, link]);
      setSuccessMessage('Share link created successfully!');
      setPassword('');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create share link.');
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (token: string) => {
    try {
      await revokeShareLink(reportId, token);
      setShares((prev) => prev.filter((s) => s.share_token !== token));
      setSuccessMessage('Share link revoked.');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch {
      setError('Failed to revoke share link.');
    }
  };

  const copyToClipboard = async (url: string, token: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedToken(token);
      setTimeout(() => setCopiedToken(null), 2000);
    } catch {
      const el = document.createElement('textarea');
      el.value = url;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopiedToken(token);
      setTimeout(() => setCopiedToken(null), 2000);
    }
  };

  const isExpired = (expiresAt: string | null) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b" style={{ borderColor: '#DDE6ED' }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#DDE6ED' }}>
              <FontAwesomeIcon icon={faShareNodes} className="w-5 h-5" style={{ color: '#526D82' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold" style={{ color: '#27374D' }}>Share Report</h2>
              <p className="text-sm" style={{ color: '#9DB2BF' }}>Create a secure shareable link</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-colors hover:bg-gray-100"
            style={{ color: '#9DB2BF' }}
            aria-label="Close"
          >
            <FontAwesomeIcon icon={faXmark} className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Feedback */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              <FontAwesomeIcon icon={faXmark} className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}
          {successMessage && (
            <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">
              <FontAwesomeIcon icon={faCheck} className="w-4 h-4 flex-shrink-0" />
              {successMessage}
            </div>
          )}

          {/* Create form */}
          <div className="rounded-xl p-5 space-y-4" style={{ backgroundColor: '#DDE6ED' }}>
            <h3 className="font-semibold text-sm" style={{ color: '#27374D' }}>Create New Share Link</h3>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#526D82' }}>
                Link expires in
              </label>
              <select
                value={expiryDays}
                onChange={(e) => setExpiryDays(Number(e.target.value))}
                className="w-full px-3 py-2.5 border rounded-lg bg-white text-sm focus:outline-none"
                style={{ borderColor: '#9DB2BF', color: '#27374D' }}
              >
                <option value={1}>1 day</option>
                <option value={3}>3 days</option>
                <option value={7}>7 days (recommended)</option>
                <option value={14}>14 days</option>
                <option value={30}>30 days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#526D82' }}>
                Password protection{' '}
                <span style={{ color: '#9DB2BF', fontWeight: 400 }}>(optional)</span>
              </label>
              <div className="relative">
                <FontAwesomeIcon
                  icon={faLock}
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5"
                  style={{ color: '#9DB2BF' }}
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Leave blank for no password"
                  className="w-full pl-9 pr-3 py-2.5 border rounded-lg text-sm focus:outline-none bg-white"
                  style={{ borderColor: '#9DB2BF', color: '#27374D' }}
                />
              </div>
            </div>

            <button
              onClick={handleCreate}
              disabled={creating}
              className="w-full py-2.5 text-white rounded-lg font-semibold text-sm disabled:opacity-60 transition-colors flex items-center justify-center gap-2"
              style={{ backgroundColor: '#526D82' }}
            >
              <FontAwesomeIcon icon={creating ? faSpinner : faPlus} className={`w-4 h-4 ${creating ? 'animate-spin' : ''}`} />
              {creating ? 'Creating…' : 'Generate Share Link'}
            </button>
          </div>

          {/* Active links */}
          <div>
            <h3 className="font-semibold text-sm mb-3" style={{ color: '#27374D' }}>
              Active Links
              {shares.length > 0 && (
                <span
                  className="ml-2 px-2 py-0.5 rounded-full text-xs"
                  style={{ backgroundColor: '#DDE6ED', color: '#526D82' }}
                >
                  {shares.length}
                </span>
              )}
            </h3>

            {loadingShares ? (
              <div className="text-center py-6">
                <FontAwesomeIcon
                  icon={faSpinner}
                  className="w-8 h-8 animate-spin"
                  style={{ color: '#526D82' }}
                />
              </div>
            ) : shares.length === 0 ? (
              <p className="text-sm text-center py-4" style={{ color: '#9DB2BF' }}>
                No active share links yet
              </p>
            ) : (
              <ul className="space-y-3">
                {shares.map((share) => {
                  const expired = isExpired(share.expires_at);
                  return (
                    <li
                      key={share.share_token}
                      className="border rounded-xl p-4"
                      style={
                        expired
                          ? { borderColor: '#DDE6ED', backgroundColor: '#f8fafc', opacity: 0.7 }
                          : { borderColor: '#9DB2BF', backgroundColor: '#DDE6ED' }
                      }
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1 flex-wrap">
                            {expired ? (
                              <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ backgroundColor: '#DDE6ED', color: '#9DB2BF' }}>
                                Expired
                              </span>
                            ) : (
                              <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">
                                Active
                              </span>
                            )}
                            {share.is_password_protected && (
                              <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full font-medium flex items-center gap-1">
                                <FontAwesomeIcon icon={faLock} className="w-2.5 h-2.5" />
                                Password
                              </span>
                            )}
                            <span className="text-xs" style={{ color: '#9DB2BF' }}>
                              {share.access_count} access{share.access_count !== 1 ? 'es' : ''}
                            </span>
                          </div>
                          <p className="text-xs truncate font-mono" style={{ color: '#526D82' }}>
                            {share.share_url}
                          </p>
                          {share.expires_at && (
                            <p className="text-xs mt-1" style={{ color: '#9DB2BF' }}>
                              Expires {new Date(share.expires_at).toLocaleDateString('en-US', {
                                month: 'short', day: 'numeric', year: 'numeric',
                              })}
                            </p>
                          )}
                        </div>

                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          {!expired && (
                            <button
                              onClick={() => copyToClipboard(share.share_url, share.share_token)}
                              className="p-1.5 rounded-lg transition-colors hover:bg-white"
                              style={{ color: '#526D82' }}
                              title="Copy link"
                            >
                              <FontAwesomeIcon
                                icon={copiedToken === share.share_token ? faCheck : faCopy}
                                className={`w-4 h-4 ${copiedToken === share.share_token ? 'text-green-600' : ''}`}
                              />
                            </button>
                          )}
                          <button
                            onClick={() => handleRevoke(share.share_token)}
                            className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Revoke link"
                          >
                            <FontAwesomeIcon icon={faTrashCan} className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Privacy note */}
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-800 leading-relaxed">
              ⚠️ <strong>Privacy Notice:</strong> Anyone with the link can view this report.
              Shared reports are read-only. Revoke a link at any time to stop access.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;
