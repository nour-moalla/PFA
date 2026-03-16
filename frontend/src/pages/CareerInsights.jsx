import { useState, useEffect } from 'react'
import { careerAPI } from '../api/client'

const CareerInsights = () => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [skills, setSkills] = useState([])
  const [marketInsights, setMarketInsights] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [roadmap, setRoadmap] = useState(null)

  useEffect(() => {
    loadMarketInsights()
  }, [])

  const loadMarketInsights = async () => {
    try {
      const response = await careerAPI.getMarketInsights()
      setMarketInsights(response.data)
    } catch (err) {
      console.error('Failed to load market insights:', err)
    }
  }

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && (selectedFile.type === 'application/pdf' || selectedFile.type === 'text/plain')) {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Please select a valid PDF or TXT file')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await careerAPI.uploadCV(file)
      if (response.data.success) {
        setSkills(response.data.skills || [])
      } else {
        setError(response.data.error || 'Failed to extract skills')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload CV. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (skills.length === 0) {
      setError('Please upload your CV first to extract skills')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await careerAPI.analyze({ skills })
      setAnalysis(response.data)
      setRoadmap(response.data.roadmap)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze skills. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    if (!analysis?.pdf_url) return

    try {
      const filename = analysis.pdf_url.split('/').pop()
      const response = await careerAPI.downloadPDF(filename)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('Failed to download PDF')
    }
  }

  const reset = () => {
    setFile(null)
    setSkills([])
    setAnalysis(null)
    setRoadmap(null)
    setError('')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-black text-[#0A2A6B] mb-2 uppercase">Career Insights</h1>
        <p className="text-xl text-gray-600">Discover market trends, identify skill gaps, and get personalized learning roadmaps</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Market Insights */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-6 sticky top-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>📊</span> Market Insights
            </h2>
            {marketInsights && marketInsights.top_10_skills && marketInsights.top_10_skills.length > 0 ? (
              <div className="space-y-2">
                {marketInsights.top_10_skills.map((skill, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500 hover:bg-blue-100 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded">
                        #{idx + 1}
                      </span>
                      <span className="font-semibold text-gray-900 text-sm">{skill.category}</span>
                    </div>
                    <div className="text-xs text-gray-600">{skill.count} job postings</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Market insights loading...</p>
            )}
          </div>
        </div>

        {/* Right Panel - CV Upload & Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {!skills.length && !analysis && (
            <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Your CV</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center mb-4 hover:border-gray-400 bg-gray-50 transition-colors duration-200">
                <input
                  type="file"
                  id="file-input"
                  accept=".pdf,.txt"
                  onChange={(e) => handleFileSelect(e.target.files?.[0])}
                  className="hidden"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  {file ? (
                    <div className="flex flex-col items-center">
                      <span className="text-4xl mb-2">📄</span>
                      <span className="font-medium text-gray-900">{file.name}</span>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-lg font-semibold text-gray-700">Click to upload your CV</p>
                      <p className="text-sm text-gray-500 mt-1">PDF or TXT format</p>
                    </div>
                  )}
                </label>
              </div>
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">{error}</div>
              )}
              <button
                onClick={handleUpload}
                disabled={loading || !file}
                className="w-full py-4 px-8 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
              >
                {loading ? 'Processing...' : 'Extract Skills'}
              </button>
            </div>
          )}

          {skills.length > 0 && !analysis && (
            <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Extracted Skills</h2>
              <div className="flex flex-wrap gap-2 mb-6">
                {skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full py-4 px-8 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
              >
                {loading ? 'Analyzing...' : 'Analyze Skills & Generate Career Insights'}
              </button>
            </div>
          )}

          {analysis && (
            <div className="space-y-6">
              {/* Gap Analysis */}
              {analysis.missing_categories && analysis.missing_categories.length > 0 && (
                <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Skill Gap Analysis</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h3 className="font-semibold text-green-600 mb-2">✅ Your Skills</h3>
                      <div className="space-y-1">
                        {analysis.user_categories?.map((cat, idx) => (
                          <div key={idx} className="text-sm text-gray-700">• {cat}</div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-red-600 mb-2">⚠️ Missing Skills</h3>
                      <div className="space-y-1">
                        {analysis.missing_categories.map((cat, idx) => (
                          <div key={idx} className="text-sm text-gray-700">• {cat}</div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Roadmap */}
              {roadmap && (
                <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Career Roadmap</h2>
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-700 leading-relaxed bg-gray-50 p-6 rounded-lg">
                      {roadmap}
                    </div>
                  </div>
                  <div className="mt-6 flex gap-4">
                    {analysis.pdf_url && (
                      <button
                        onClick={downloadPDF}
                        className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                      >
                        Download PDF
                      </button>
                    )}
                    <button
                      onClick={reset}
                      className="px-4 py-2 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 transition-colors"
                    >
                      Start Over
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CareerInsights

