import { useState } from 'react'
import { resumeAPI } from '../api/client'

const ResumeAnalysis = () => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [jobTitle, setJobTitle] = useState('')
  const [company, setCompany] = useState('')
  const [jobDescription, setJobDescription] = useState('')

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Please select a valid PDF file')
      setFile(null)
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a resume file')
      return
    }

    setLoading(true)
    setError('')
    setAnalysis(null)

    try {
      const response = await resumeAPI.analyze(file, {
        job_title: jobTitle || undefined,
        company: company || undefined,
        job_description: jobDescription || undefined,
      })
      setAnalysis(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze resume. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setAnalysis(null)
    setError('')
    setJobTitle('')
    setCompany('')
    setJobDescription('')
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-black text-[#0A2A6B] mb-2 uppercase">Resume Analysis</h1>
        <p className="text-xl text-gray-600">Upload your resume to get comprehensive ATS scoring and detailed feedback</p>
      </div>

      {!analysis ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {/* Job Information (Optional) */}
          <div className="mb-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Job Information (Optional)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Software Engineer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Tech Corp"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Paste the job description here for targeted analysis..."
              />
            </div>
          </div>

          {/* File Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload Resume (PDF)</label>
            <div
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors duration-200 ${
                dragActive ? 'border-[#0A2A6B] bg-blue-50' : 'border-gray-300 hover:border-gray-400 bg-gray-50'
              } ${file ? 'border-green-500 bg-green-50' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="file-input"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="file-input" className="cursor-pointer">
                {file ? (
                  <div className="flex flex-col items-center">
                    <span className="text-4xl mb-2">📄</span>
                    <span className="font-medium text-gray-900">{file.name}</span>
                    <span className="text-sm text-gray-500 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-lg font-semibold text-gray-700 mb-1">
                      <span className="text-[#0A2A6B] hover:text-blue-700">Click to choose</span> or drag and drop
                    </p>
                    <p className="text-sm text-gray-500">PDF format, max 16MB</p>
                  </div>
                )}
              </label>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || !file}
            className="w-full py-4 px-8 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              'Analyze Resume'
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* ATS Score */}
          <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8">
            <div className="text-center mb-6">
            <div className="text-6xl font-black text-[#0A2A6B] mb-2">{analysis.overall_score ?? analysis.ats_score ?? 'N/A'}</div>
            <div className="text-2xl font-semibold text-gray-900">ATS Score</div>
            <div className="text-gray-600 mt-2">Out of 100</div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-[#0A2A6B] h-4 rounded-full transition-all duration-500"
              style={{ width: `${analysis.overall_score ?? analysis.ats_score ?? 0}%` }}
            ></div>
          </div>
          </div>

          {/* Summary */}
          {analysis.feedback_summary && (
            <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8">
              <h2 className="text-2xl font-bold text-[#0A2A6B] mb-4">Summary</h2>
              <div className="text-gray-700 leading-relaxed space-y-2">
                {Array.isArray(analysis.feedback_summary) ? (
                  analysis.feedback_summary.map((line, idx) => (
                    <p key={idx}>{line}</p>
                  ))
                ) : (
                  <p className="whitespace-pre-wrap">{analysis.feedback_summary}</p>
                )}
              </div>
            </div>
          )}

          {/* Pros and Cons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {analysis.pros && analysis.pros.length > 0 && (
              <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8">
                <h2 className="text-2xl font-bold text-green-600 mb-4">✅ Strengths</h2>
                <ul className="space-y-2">
                  {analysis.pros.map((pro, idx) => (
                    <li key={idx} className="text-gray-700 flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.cons && analysis.cons.length > 0 && (
              <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8">
                <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ Areas for Improvement</h2>
                <ul className="space-y-2">
                  {analysis.cons.map((con, idx) => (
                    <li key={idx} className="text-gray-700 flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Suggestions */}
          {analysis.suggestions && analysis.suggestions.length > 0 && (
            <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8">
              <h2 className="text-2xl font-bold text-[#0A2A6B] mb-4">💡 Improvement Suggestions</h2>
              <ul className="space-y-3">
                {analysis.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="text-gray-700 flex items-start">
                    <span className="text-blue-500 mr-2 font-bold">{idx + 1}.</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={reset}
            className="w-full py-4 px-8 bg-gray-600 text-white font-bold rounded-xl hover:bg-gray-700 transition-all duration-300 shadow-lg"
          >
            Analyze Another Resume
          </button>
        </div>
      )}
    </div>
  )
}

export default ResumeAnalysis

