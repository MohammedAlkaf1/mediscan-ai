import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Layout from '@/components/Layout';
import { useAuth } from '@/lib/AuthContext';

export default function Login() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold" style={{ color: '#DDE6ED' }}>
              Sign in to your account
            </h2>
            <p className="mt-2 text-center text-sm" style={{ color: '#9DB2BF' }}>
              Or{' '}
              <Link href="/auth/register" className="font-medium hover:underline" style={{ color: '#526D82' }}>
                create a new account
              </Link>
            </p>
          </div>

          <form className="mt-8 space-y-6 p-8 rounded-xl shadow-lg border" style={{ backgroundColor: '#DDE6ED', borderColor: '#9DB2BF' }} onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium" style={{ color: '#526D82' }}>
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border rounded-lg focus:outline-none text-sm"
                  style={{ borderColor: '#DDE6ED', color: '#27374D' }}
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium" style={{ color: '#526D82' }}>
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border rounded-lg focus:outline-none text-sm"
                  style={{ borderColor: '#DDE6ED', color: '#27374D' }}
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-semibold rounded-lg text-white transition-all disabled:opacity-50"
                style={{ backgroundColor: '#526D82' }}
              >
                {loading ? 'Signing in…' : 'Sign in'}
              </button>
            </div>

            <div className="text-center">
              <Link href="/" className="text-sm hover:underline" style={{ color: '#9DB2BF' }}>
                Continue without login
              </Link>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}
