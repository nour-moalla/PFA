import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const { resetPassword } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')

    if (!email) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    const result = await resetPassword(email)
    if (result.success) {
      setMessage('Check your email for password reset instructions')
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
            Reset Password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/login" className="font-semibold text-[#0A2A6B] hover:text-[#d35500]">
              sign in with email link
            </Link>
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {error}
          </div>
        )}

        {message && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl">
            {message}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
            <p className="mt-2 text-sm text-gray-600">
              We'll send you a link to reset your password
            </p>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-bold rounded-xl text-white bg-[#0A2A6B] hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0A2A6B] disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </div>

          <div className="text-center">
            <Link
              to="/login"
              className="text-sm font-medium text-[#0A2A6B] hover:text-[#d35500]"
            >
              Back to Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ForgotPassword

