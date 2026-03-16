import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { isSignInWithEmailLink, signInWithEmailLink } from 'firebase/auth'
import { auth } from '../config/firebase'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showLinkSignIn, setShowLinkSignIn] = useState(false)
  const [linkEmail, setLinkEmail] = useState('')
  const [linkSent, setLinkSent] = useState(false)

  const { login, sendSignInLink, signInWithGoogle } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  // Check if user is signing in with email link
  useEffect(() => {
    if (isSignInWithEmailLink(auth, window.location.href)) {
      let email = window.localStorage.getItem('emailForSignIn')
      if (!email) {
        email = window.prompt('Please provide your email for confirmation')
      }
      if (email) {
        signInWithEmailLink(auth, email, window.location.href)
          .then(() => {
            window.localStorage.removeItem('emailForSignIn')
            navigate(from, { replace: true })
          })
          .catch((error) => {
            setError(error.message)
          })
      }
    }
  }, [navigate, from])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password)
    if (result.success) {
      navigate(from, { replace: true })
    } else {
      setError(result.error)
    }
    setLoading(false)
  }

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    const result = await signInWithGoogle()
    if (result.success) {
      navigate(from, { replace: true })
    } else {
      setError(result.error)
    }
    setLoading(false)
  }

  const handleSendLink = async (e) => {
    e.preventDefault()
    setError('')
    if (!linkEmail) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    const result = await sendSignInLink(linkEmail)
    if (result.success) {
      setLinkSent(true)
    } else {
      setError(result.error)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-4xl font-black text-[#0A2A6B] uppercase">
            Sign In
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/signup" className="font-semibold text-[#0A2A6B] hover:text-[#d35500]">
              create a new account
            </Link>
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {error}
          </div>
        )}

        {!showLinkSignIn ? (
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
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
                  className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0A2A6B] focus:border-transparent"
                  placeholder="Enter your email"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
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
                  className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0A2A6B] focus:border-transparent"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <Link
                  to="/forgot-password"
                  className="font-medium text-[#0A2A6B] hover:text-[#d35500]"
                >
                  Forgot your password?
                </Link>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-blue-800">
                <i className="fa-solid fa-link mr-2"></i>
                <strong>Forgot your password?</strong> Sign in with a link!{' '}
                <button
                  type="button"
                  onClick={() => setShowLinkSignIn(true)}
                  className="font-semibold underline hover:text-blue-900"
                >
                  Click here
                </button>
              </p>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-bold rounded-xl text-white bg-[#0A2A6B] hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0A2A6B] disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="space-y-3">
              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={loading}
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-300"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Sign in with Google
              </button>

              <button
                type="button"
                onClick={() => setShowLinkSignIn(true)}
                disabled={loading}
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-300"
              >
                <i className="fa-solid fa-envelope mr-2"></i>
                Sign in with email link (passwordless)
              </button>
            </div>
          </form>
        ) : (
          <div className="mt-8 space-y-6">
            {linkSent ? (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl">
                <p className="font-semibold mb-2">Check your email!</p>
                <p className="text-sm">
                  We've sent a sign-in link to <strong>{linkEmail}</strong>. Click the link in the email to sign in.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSendLink} className="space-y-4">
                <div>
                  <label htmlFor="link-email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email address
                  </label>
                  <input
                    id="link-email"
                    name="link-email"
                    type="email"
                    autoComplete="email"
                    required
                    value={linkEmail}
                    onChange={(e) => setLinkEmail(e.target.value)}
                    className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0A2A6B] focus:border-transparent"
                    placeholder="Enter your email"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent text-base font-bold rounded-xl text-white bg-[#0A2A6B] hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0A2A6B] disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
                >
                  {loading ? 'Sending...' : 'Send sign-in link'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowLinkSignIn(false)
                    setLinkEmail('')
                    setLinkSent(false)
                  }}
                  className="w-full text-sm text-gray-600 hover:text-[#0A2A6B]"
                >
                  Back to password sign in
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Login
