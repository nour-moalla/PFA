import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const HomePage = () => {
  const { user } = useAuth()

  const features = [
    {
      icon: '📄',
      title: 'Resume AI Analysis',
      description: 'Get comprehensive ATS scoring and detailed feedback on your resume. Our AI analyzes your resume against industry standards and provides actionable improvement suggestions.',
      benefits: [
        'ATS compatibility scoring (0-100)',
        'Detailed feedback with pros and cons',
        'Skill extraction and matching',
        'Industry-specific optimization tips',
        'Job-targeted analysis support'
      ],
      href: '/resume',
      buttonText: 'Analyze Resume',
      color: 'blue',
    },
    {
      icon: '🤖',
      title: 'AI Interview Coach',
      description: 'Practice with realistic AI-powered interviews tailored to your role. Receive instant feedback on your technical knowledge, communication skills, and problem-solving abilities.',
      benefits: [
        'Role-specific interview questions',
        'Real-time scoring and feedback',
        'Code editor for technical challenges',
        'Communication style analysis',
        'Interview history tracking'
      ],
      href: '/interview',
      buttonText: 'Start Interview',
      color: 'green',
    },
    {
      icon: '📊',
      title: 'Career Insights & Roadmap',
      description: 'Discover market trends, identify skill gaps, and get personalized learning roadmaps. Understand what skills are in demand and how to bridge your career gaps.',
      benefits: [
        'Market skill analysis',
        'Personalized learning roadmaps',
        'Skill gap identification',
        'Career progression recommendations',
        'PDF roadmap downloads'
      ],
      href: '/career',
      buttonText: 'Get Insights',
      color: 'purple',
    },
    {
      icon: '🎯',
      title: 'Smart Job Matching',
      description: 'Find the perfect job matches using semantic search technology. Our AI analyzes your CV and matches it with relevant job postings based on skills, experience, and requirements.',
      benefits: [
        'Semantic job matching',
        'Similarity scoring',
        'Top job recommendations',
        'Detailed job insights',
        'Direct application links'
      ],
      href: '/jobs',
      buttonText: 'Find Jobs',
      color: 'orange',
    },
  ]

  const stats = [
    { number: '95%', label: 'ATS Score Improvement', icon: '📈' },
    { number: '10K+', label: 'Interviews Conducted', icon: '💼' },
    { number: '50K+', label: 'Jobs Matched', icon: '🎯' },
    { number: '24/7', label: 'AI Support Available', icon: '🤖' },
  ]

  const howItWorks = [
    {
      step: '01',
      title: 'Sign Up & Upload',
      description: 'Create your account and upload your resume. Our system securely stores your information.',
      icon: '📤',
    },
    {
      step: '02',
      title: 'AI Analysis',
      description: 'Our advanced AI analyzes your resume, skills, and experience to provide comprehensive insights.',
      icon: '🔍',
    },
    {
      step: '03',
      title: 'Get Recommendations',
      description: 'Receive personalized recommendations, roadmaps, and job matches tailored to your profile.',
      icon: '💡',
    },
    {
      step: '04',
      title: 'Take Action',
      description: 'Practice interviews, improve your resume, and apply to matched jobs to advance your career.',
      icon: '🚀',
    },
  ]

  return (
    <div className="bg-white min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col justify-center items-center pt-20 pb-20 overflow-hidden">
        {/* Animated Background Blobs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse delay-75"></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse delay-150"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10">
          <div className="text-center space-y-8">
            <div className="inline-block">
              <span className="text-lg sm:text-xl md:text-2xl font-bold text-[#0A2A6B] uppercase tracking-wide px-4 py-2 bg-blue-50 rounded-full border border-blue-200">
                AI-Powered Career Platform
              </span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-black text-[#0A2A6B] leading-tight px-4">
              Transform Your{' '}
              <span className="text-orange-500 bg-clip-text">Career</span>{' '}
              with AI
            </h1>
            
            <p className="text-lg sm:text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto px-4 leading-relaxed">
              Get hired faster with AI-powered resume optimization, interview practice, career insights, and smart job matching.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-6 justify-center items-center px-4">
              {user ? (
                <Link
                  to="/resume"
                  className="px-8 py-4 bg-[#0A2A6B] text-white font-bold rounded-2xl hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3 shadow-lg group text-base sm:text-lg"
                >
                  <span>Get Started</span>
                  <i className="fa-solid fa-arrow-right group-hover:translate-x-1 transition-transform duration-300"></i>
                </Link>
              ) : (
                <>
                  <Link
                    to="/signup"
                    className="px-8 py-4 bg-[#0A2A6B] text-white font-bold rounded-2xl hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3 shadow-lg group text-base sm:text-lg"
                  >
                    <span>Get Started Free</span>
                    <i className="fa-solid fa-arrow-right group-hover:translate-x-1 transition-transform duration-300"></i>
                  </Link>
                  <Link
                    to="/login"
                    className="px-8 py-4 border-2 border-[#0A2A6B] text-[#0A2A6B] font-bold rounded-2xl hover:bg-[#0A2A6B] hover:text-white transition-all duration-300 text-base sm:text-lg"
                  >
                    Sign In
                  </Link>
                </>
              )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 pt-12 mt-12 border-t border-gray-200/50 max-w-6xl mx-auto px-4">
              {stats.map((stat, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-2xl sm:text-3xl md:text-4xl mb-2">{stat.icon}</div>
                  <div className="text-2xl sm:text-3xl md:text-4xl font-black text-[#0A2A6B] mb-1">
                    {stat.number}
                  </div>
                  <div className="text-xs sm:text-sm text-gray-600 font-medium">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 sm:py-20 md:py-24 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 md:mb-20">
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black text-[#0A2A6B] mb-4 sm:mb-6 uppercase">
              Our Features
            </h2>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Everything you need to advance your career, powered by AI
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 md:gap-10 lg:gap-12">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="bg-white rounded-3xl p-6 sm:p-8 md:p-10 lg:p-12 hover:shadow-2xl transition-all duration-300 border-2 border-gray-100 group"
              >
                <div className="flex items-start gap-4 sm:gap-6 mb-6">
                  <div className="text-4xl sm:text-5xl md:text-6xl flex-shrink-0">
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#0A2A6B] mb-3 sm:mb-4">
                      {feature.title}
                    </h3>
                    <p className="text-base sm:text-lg text-gray-600 leading-relaxed mb-6">
                      {feature.description}
                    </p>
                  </div>
                </div>

                <div className="mb-6 sm:mb-8">
                  <h4 className="text-sm sm:text-base font-semibold text-gray-900 mb-3 sm:mb-4 uppercase tracking-wide">
                    Key Benefits:
                  </h4>
                  <ul className="space-y-2 sm:space-y-3">
                    {feature.benefits.map((benefit, benefitIdx) => (
                      <li key={benefitIdx} className="flex items-start gap-3">
                        <i className="fa-solid fa-check-circle text-green-500 mt-1 flex-shrink-0"></i>
                        <span className="text-sm sm:text-base text-gray-700">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Link
                  to={feature.href}
                  className={`inline-flex items-center justify-center w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 rounded-xl font-bold text-base sm:text-lg text-white bg-[#0A2A6B] hover:bg-blue-800 transition-all duration-300 shadow-lg group-hover:shadow-xl group-hover:scale-105`}
                >
                  {feature.buttonText}
                  <i className="fa-solid fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 sm:py-20 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 md:mb-20">
            <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black text-[#0A2A6B] mb-4 sm:mb-6 uppercase">
              How It Works
            </h2>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Get started in minutes and transform your career
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
            {howItWorks.map((step, idx) => (
              <div
                key={idx}
                className="relative bg-gradient-to-br from-gray-50 to-white rounded-3xl p-6 sm:p-8 border-2 border-gray-100 hover:border-[#0A2A6B] transition-all duration-300 hover:shadow-xl group"
              >
                <div className="absolute -top-4 -left-4 w-12 h-12 sm:w-16 sm:h-16 bg-[#0A2A6B] text-white rounded-full flex items-center justify-center font-black text-lg sm:text-xl md:text-2xl shadow-lg">
                  {step.step}
                </div>
                <div className="text-4xl sm:text-5xl md:text-6xl mb-4 sm:mb-6 text-center">
                  {step.icon}
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-[#0A2A6B] mb-3 sm:mb-4 text-center">
                  {step.title}
                </h3>
                <p className="text-sm sm:text-base text-gray-600 leading-relaxed text-center">
                  {step.description}
                </p>
                {idx < howItWorks.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 text-2xl text-gray-300">
                    <i className="fa-solid fa-arrow-right"></i>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 sm:py-20 md:py-24 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            <div className="bg-white rounded-3xl p-6 sm:p-8 text-center border-2 border-gray-100 hover:border-blue-200 transition-all duration-300 hover:shadow-xl">
              <div className="text-4xl sm:text-5xl mb-4">🔒</div>
              <h3 className="text-xl sm:text-2xl font-black text-[#0A2A6B] mb-3">
                End-to-End Encryption
              </h3>
              <p className="text-sm sm:text-base text-gray-600">
                Your interviews and data are fully secured with industry-standard encryption
              </p>
            </div>
            <div className="bg-white rounded-3xl p-6 sm:p-8 text-center border-2 border-gray-100 hover:border-orange-200 transition-all duration-300 hover:shadow-xl">
              <div className="text-4xl sm:text-5xl mb-4">👤</div>
              <h3 className="text-xl sm:text-2xl font-black text-orange-500 mb-3">
                You Own Your Data
              </h3>
              <p className="text-sm sm:text-base text-gray-600">
                Download or delete your data anytime. Complete control over your information
              </p>
            </div>
            <div className="bg-white rounded-3xl p-6 sm:p-8 text-center border-2 border-gray-100 hover:border-blue-200 transition-all duration-300 hover:shadow-xl">
              <div className="text-4xl sm:text-5xl mb-4">🛡️</div>
              <h3 className="text-xl sm:text-2xl font-black text-blue-600 mb-3">
                24/7 AI Monitoring
              </h3>
              <p className="text-sm sm:text-base text-gray-600">
                Constant security surveillance and AI-powered protection for your account
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20 md:py-24 bg-gradient-to-r from-[#0A2A6B] to-blue-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-4 sm:mb-6">
            Ready to Transform Your Career?
          </h2>
          <p className="text-lg sm:text-xl md:text-2xl text-blue-100 mb-8 sm:mb-10 leading-relaxed">
            Join thousands of professionals who have accelerated their career growth with AI-powered tools
          </p>
          {user ? (
            <Link
              to="/resume"
              className="inline-flex items-center px-8 py-4 bg-white text-[#0A2A6B] font-bold rounded-2xl hover:bg-gray-100 hover:scale-105 transition-all duration-300 shadow-xl text-base sm:text-lg"
            >
              Get Started Now
              <i className="fa-solid fa-arrow-right ml-2"></i>
            </Link>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/signup"
                className="inline-flex items-center px-8 py-4 bg-white text-[#0A2A6B] font-bold rounded-2xl hover:bg-gray-100 hover:scale-105 transition-all duration-300 shadow-xl text-base sm:text-lg"
              >
                Start Free Trial
                <i className="fa-solid fa-arrow-right ml-2"></i>
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center px-8 py-4 border-2 border-white text-white font-bold rounded-2xl hover:bg-white hover:text-[#0A2A6B] transition-all duration-300 text-base sm:text-lg"
              >
                Sign In
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default HomePage
