import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faUpload,
  faClockRotateLeft,
  faChartLine,
  faRightFromBracket,
  faUserPlus,
  faRightToBracket,
} from '@fortawesome/free-solid-svg-icons';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const navLinks = [
    { href: '/',          label: 'Upload',    icon: faUpload,           authRequired: false },
    { href: '/reports',   label: 'History',   icon: faClockRotateLeft,  authRequired: false },
    { href: '/analytics', label: 'Analytics', icon: faChartLine,        authRequired: true  },
  ];

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#27374D' }}>

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header
        className="sticky top-0 z-50 shadow-sm"
        style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #DDE6ED' }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">

            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 group">
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-105"
                style={{ backgroundColor: '#526D82' }}
              >
                {/* Medical cross — clean SVG */}
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <rect x="8.5" y="3"   width="3"  height="14" rx="1.2" fill="white" />
                  <rect x="3"   y="8.5" width="14" height="3"  rx="1.2" fill="white" />
                </svg>
              </div>
              <div className="leading-tight">
                <span className="text-lg font-bold tracking-tight" style={{ color: '#1a1a1a' }}>
                  Medi<span style={{ color: '#526D82' }}>Scan</span>
                  <span className="font-light text-sm ml-1" style={{ color: '#9DB2BF' }}>AI</span>
                </span>
                <p className="text-xs font-medium" style={{ color: '#9DB2BF' }}>
                  Lab Report Analysis
                </p>
              </div>
            </Link>

            {/* Nav links */}
            <nav className="flex items-center gap-1">
              {navLinks.map((link) => {
                if (link.authRequired && !isAuthenticated) return null;
                const active = router.pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-150 flex items-center gap-2"
                    style={
                      active
                        ? { color: '#526D82', backgroundColor: '#DDE6ED' }
                        : { color: '#555' }
                    }
                  >
                    <FontAwesomeIcon icon={link.icon} className="w-3.5 h-3.5" />
                    <span className="hidden sm:block">{link.label}</span>
                  </Link>
                );
              })}

              {!loading && (
                <div className="ml-2 flex items-center gap-1.5">
                  {isAuthenticated ? (
                    <>
                      <span className="hidden md:block text-xs max-w-[120px] truncate px-2" style={{ color: '#9DB2BF' }}>
                        {user?.email}
                      </span>
                      <button
                        onClick={handleLogout}
                        className="px-3.5 py-2 text-sm font-medium rounded-lg transition-all flex items-center gap-2"
                        style={{ color: '#c0392b', backgroundColor: '#fdf0ee' }}
                      >
                        <FontAwesomeIcon icon={faRightFromBracket} className="w-3.5 h-3.5" />
                        <span className="hidden sm:block">Logout</span>
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/auth/login"
                        className="px-3.5 py-2 text-sm font-medium rounded-lg transition-all flex items-center gap-2"
                        style={{ color: '#526D82' }}
                      >
                        <FontAwesomeIcon icon={faRightToBracket} className="w-3.5 h-3.5" />
                        <span className="hidden sm:block">Login</span>
                      </Link>
                      <Link
                        href="/auth/register"
                        className="px-4 py-2 text-sm font-semibold text-white rounded-lg transition-all shadow-sm flex items-center gap-2"
                        style={{ backgroundColor: '#526D82' }}
                      >
                        <FontAwesomeIcon icon={faUserPlus} className="w-3.5 h-3.5" />
                        <span className="hidden sm:block">Sign Up</span>
                      </Link>
                    </>
                  )}
                </div>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* ── Main ───────────────────────────────────────────────────────────── */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer style={{ backgroundColor: '#ffffff', borderTop: '1px solid #DDE6ED' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
            <span className="text-sm font-semibold" style={{ color: '#526D82' }}>MediScan AI</span>
            <span className="text-xs" style={{ color: '#9DB2BF' }}>Educational use only</span>
            <span className="text-xs" style={{ color: '#9DB2BF' }}>© {new Date().getFullYear()} MediScan AI</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
