import { useState, useEffect } from 'react'
import { jobAPI } from '../api/client'

const JobMatching = () => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [matches, setMatches] = useState(null)
  const [databaseInfo, setDatabaseInfo] = useState(null)

  useEffect(() => {
    loadDatabaseInfo()
  }, [])

  const loadDatabaseInfo = async () => {
    try {
      const response = await jobAPI.getDatabaseInfo()
      setDatabaseInfo(response.data)
    } catch (err) {
      console.error('Failed to load database info:', err)
    }
  }

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Please select a valid PDF file')
    }
  }

  const handleMatch = async () => {
    if (!file) {
      setError('Please select a CV file')
      return
    }

    setLoading(true)
    setError('')
    setMatches(null)

    try {
      const response = await jobAPI.matchCV(file)
      setMatches(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to match CV. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setMatches(null)
    setError('')
  }

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent Match'
    if (score >= 0.6) return 'Good Match'
    return 'Fair Match'
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-black text-[#0A2A6B] mb-2 uppercase">Job Matching</h1>
        <p className="text-xl text-gray-600">Find the best job matches for your CV using semantic search</p>
        {databaseInfo && (
          <p className="text-sm text-gray-500 mt-2">
            Database: {databaseInfo.total_jobs || 0} jobs available
          </p>
        )}
      </div>

      {!matches ? (
        <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Your CV</h2>
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center mb-4 hover:border-gray-400 bg-gray-50 transition-colors duration-200">
            <input
              type="file"
              id="file-input"
              accept=".pdf"
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
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
                  <p className="text-lg font-semibold text-gray-700">Click to upload your CV</p>
                  <p className="text-sm text-gray-500 mt-1">PDF format</p>
                </div>
              )}
            </label>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">{error}</div>
          )}

          <button
            onClick={handleMatch}
            disabled={loading || !file}
            className="w-full py-4 px-8 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Finding Matches...
              </>
            ) : (
              'Find Job Matches'
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Top {matches.matches?.length || 0} Job Matches
              </h2>
              <button
                onClick={reset}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Match Another CV
              </button>
            </div>
            <p className="text-sm text-gray-600">
              Searched {matches.total_jobs_searched || 0} jobs in the database
            </p>
          </div>

          {matches.matches && matches.matches.length > 0 ? (
            <div className="space-y-4">
              {matches.matches.map((match, idx) => (
                <div
                  key={idx}
                  className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-1">{match.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                        <span className="flex items-center gap-1">
                          <span>🏢</span> {match.company}
                        </span>
                        {match.location && (
                          <span className="flex items-center gap-1">
                            <span>📍</span> {match.location}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className={`px-4 py-2 rounded-lg font-semibold ${getScoreColor(match.similarity_score)}`}>
                      <div className="text-2xl">{(match.similarity_score * 100).toFixed(0)}%</div>
                      <div className="text-xs">{getScoreLabel(match.similarity_score)}</div>
                    </div>
                  </div>

                  {match.description && (
                    <p className="text-gray-700 mb-4 line-clamp-3">{match.description}</p>
                  )}

                  {match.job_url && match.job_url !== 'N/A' && (
                    <a
                      href={match.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-6 py-3 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 transition-all duration-300 shadow-lg"
                    >
                      View Job Details →
                    </a>
                  )}

                  {/* Similarity Score Bar */}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                      <span>Match Score</span>
                      <span>{(match.similarity_score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          match.similarity_score >= 0.8
                            ? 'bg-green-500'
                            : match.similarity_score >= 0.6
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${match.similarity_score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 text-center">
              <p className="text-gray-600">No matches found. Try uploading a different CV.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default JobMatching

