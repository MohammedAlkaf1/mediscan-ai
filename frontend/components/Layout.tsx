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
  faMicroscope,
  faHeartPulse,
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
                className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200 group-hover:scale-105 group-hover:shadow-lg relative overflow-hidden"
                style={{ background: 'linear-gradient(135deg, #2d6a9f 0%, #526D82 60%, #1a4a6b 100%)' }}
              >
                {/* Subtle pulse ring */}
                <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ boxShadow: '0 0 0 3px rgba(82,109,130,0.3)' }} />
                <FontAwesomeIcon icon={faMicroscope} className="w-5 h-5 text-white relative z-10" />
              </div>
              <div className="leading-tight">
                <div className="flex items-baseline gap-1">
                  <span className="text-lg font-extrabold tracking-tight" style={{ color: '#1a1a1a' }}>
                    Medi<span style={{ color: '#2d6a9f' }}>Scan</span>
                  </span>
                  <span
                    className="text-xs font-bold px-1.5 py-0.5 rounded-md"
                    style={{ backgroundColor: '#DDE6ED', color: '#526D82' }}
                  >
                    AI
                  </span>
                </div>
                <p className="text-xs font-medium flex items-center gap-1" style={{ color: '#9DB2BF' }}>
                  <FontAwesomeIcon icon={faHeartPulse} className="w-2.5 h-2.5" style={{ color: '#e05c5c' }} />
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
