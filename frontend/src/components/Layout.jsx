import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'

const Layout = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef(null)

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false)
      }
    }

    if (userMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [userMenuOpen])

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Resume Analysis', href: '/resume' },
    { name: 'AI Interview', href: '/interview' },
    { name: 'Career Insights', href: '/career' },
    { name: 'Job Matching', href: '/jobs' },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center" aria-label="Go to Homepage">
            <img 
              src="https://i.imgur.com/ljCbl1O.png" 
              alt="Logo" 
              className="h-12 sm:h-16" 
            />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`font-semibold transition-colors duration-300 relative group ${
                  location.pathname === item.href
                    ? 'text-[#d35500]'
                    : 'text-[#0A2A6B] hover:text-[#d35500]'
                }`}
              >
                {item.name}
                <span className={`absolute bottom-0 left-0 h-0.5 bg-[#d35500] transition-all duration-300 ${
                  location.pathname === item.href ? 'w-full' : 'w-0 group-hover:w-full'
                }`}></span>
              </Link>
            ))}
            
            {user ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 px-3 py-2 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  {user.photoURL ? (
                    <img
                      src={user.photoURL}
                      alt={user.displayName || user.email}
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-[#0A2A6B] flex items-center justify-center text-white font-bold">
                      {(user.displayName || user.email || 'U').charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="text-sm font-medium text-[#0A2A6B]">
                    {user.displayName || user.email?.split('@')[0]}
                  </span>
                  <i className="fa-solid fa-chevron-down text-xs text-gray-600"></i>
                </button>
                
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-semibold text-gray-900">{user.displayName || 'User'}</p>
                      <p className="text-xs text-gray-600 truncate">{user.email}</p>
                    </div>
                    <button
                      onClick={async () => {
                        await logout()
                        setUserMenuOpen(false)
                        navigate('/')
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors"
                    >
                      <i className="fa-solid fa-sign-out-alt mr-2"></i>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="px-4 py-2 text-[#0A2A6B] font-semibold border border-[#0A2A6B] rounded-xl hover:bg-[#0A2A6B] hover:text-white transition-all duration-300"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 bg-[#0A2A6B] text-white rounded-xl font-bold hover:bg-blue-800 transition duration-300 shadow-lg"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-[#0A2A6B] text-xl"
          >
            <i className="fa-solid fa-bars"></i>
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-3 py-2 text-base font-semibold rounded-md transition-colors ${
                    location.pathname === item.href
                      ? 'bg-[#0A2A6B] text-white'
                      : 'text-[#0A2A6B] hover:bg-gray-100'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              {user ? (
                <div className="border-t border-gray-200 pt-2 mt-2">
                  <div className="px-3 py-2 text-sm text-gray-600">
                    <p className="font-semibold">{user.displayName || 'User'}</p>
                    <p className="text-xs truncate">{user.email}</p>
                  </div>
                  <button
                    onClick={async () => {
                      await logout()
                      setMobileMenuOpen(false)
                      navigate('/')
                    }}
                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <i className="fa-solid fa-sign-out-alt mr-2"></i>
                    Sign Out
                  </button>
                </div>
              ) : (
                <div className="border-t border-gray-200 pt-2 mt-2 space-y-1">
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 text-base font-semibold text-[#0A2A6B] hover:bg-gray-100 rounded-md transition-colors"
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 text-base font-semibold bg-[#0A2A6B] text-white rounded-md hover:bg-blue-800 transition-colors"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="pt-20 min-h-screen">{children}</main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <p className="text-center text-sm text-gray-600">
            © 2025 UtopiaHire Career Services. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
