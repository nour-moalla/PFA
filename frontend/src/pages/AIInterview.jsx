import { useState, useEffect, useRef } from 'react'
import { interviewAPI, resumeAPI } from '../api/client'
import CodeEditor from '../components/CodeEditor'

const AIInterview = () => {
  const [sessionId, setSessionId] = useState(null)
  const [cvSummary, setCvSummary] = useState('')
  const [role, setRole] = useState('Software Engineer')
  const [messages, setMessages] = useState([])
  const [isFinished, setIsFinished] = useState(false)
  const [scores, setScores] = useState(null)
  const [inputText, setInputText] = useState('')
  const [showCodeEditor, setShowCodeEditor] = useState(false)
  const [codeQuestion, setCodeQuestion] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef(null)

  const roles = [
    'Software Engineer',
    'Data Scientist',
    'Product Manager',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'DevOps Engineer',
    'UI/UX Designer',
    'Business Analyst',
    'Project Manager',
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Please select a valid PDF file')
    }
  }

  const startInterview = async () => {
    if (!file) {
      setError('Please upload your CV first')
      return
    }

    setLoading(true)
    setError('')

    try {
      // First, upload and parse the CV
      const uploadResponse = await resumeAPI.upload(file)
      const cvText = uploadResponse.data.extracted_text || uploadResponse.data.summary

      // Start interview session
      const response = await interviewAPI.start({
        cv_text: cvText,
        role: role,
      })

      setSessionId(response.data.session_id)
      setCvSummary(response.data.cv_summary || cvText.substring(0, 500))
      setMessages([
        {
          sender: 'ai',
          text: response.data.first_question,
          timestamp: new Date(),
        },
      ])
      setIsFinished(false)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start interview. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSendAnswer = async (answer, isCode = false) => {
    if (!sessionId) return

    const userMessage = {
      sender: 'user',
      text: isCode ? '[Code Submitted]' : answer,
      timestamp: new Date(),
      fullCode: isCode ? answer : null,
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await interviewAPI.answer({
        session_id: sessionId,
        answer: answer,
        is_code: isCode,
      })

      const aiMessage = {
        sender: 'ai',
        text: response.data.response,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])

      if (response.data.is_finished) {
        setIsFinished(true)
        // Fetch final scores
        try {
          const scoresResponse = await interviewAPI.getScores(sessionId)
          setScores(scoresResponse.data)
        } catch (err) {
          console.error('Failed to fetch scores:', err)
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message. Please try again.')
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputText.trim() && !isFinished) {
      handleSendAnswer(inputText.trim())
      setInputText('')
    }
  }

  const handleCodeSubmit = (code) => {
    setShowCodeEditor(false)
    setCodeQuestion(null)
    handleSendAnswer(code, true)
  }

  const parseCodeQuestion = (text) => {
    const codeMatch = text.match(/\[CODE_QUESTION\]([\s\S]*?)(?:\[LANGUAGE\]\s*(\w+)\s*\[\/LANGUAGE\])?([\s\S]*?)(?:\[STARTER_CODE\]([\s\S]*?)\[\/STARTER_CODE\])?/i)
    if (codeMatch) {
      return {
        question: codeMatch[1]?.trim() || '',
        language: codeMatch[2]?.trim() || 'python',
        starterCode: codeMatch[4]?.trim() || '# Write your code here\n',
      }
    }
    return null
  }

  const formatMessage = (text) => {
    return text
      .replace(/\[CODE_QUESTION\][\s\S]*?\[\/STARTER_CODE\]/gi, '')
      .replace(/\[SCORES\].*?\[\/SCORES\]/g, '')
      .trim()
  }

  const reset = () => {
    setSessionId(null)
    setCvSummary('')
    setMessages([])
    setIsFinished(false)
    setScores(null)
    setFile(null)
    setError('')
  }

  if (sessionId) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
        <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100">
          {/* Header */}
          <div className="border-b border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Interview for: {role}</h2>
                <p className="text-sm text-gray-600 mt-1">AI-Powered Interview Session</p>
              </div>
              <button
                onClick={reset}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                End Interview
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto">
            {messages.map((message, index) => {
              const codeQ = parseCodeQuestion(message.text)
              return (
                <div
                  key={index}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-xl p-4 ${
                      message.sender === 'user'
                        ? 'bg-[#0A2A6B] text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{formatMessage(message.text)}</div>
                    {codeQ && (
                      <button
                        onClick={() => {
                          setCodeQuestion(codeQ)
                          setShowCodeEditor(true)
                        }}
                        className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Open Code Editor
                      </button>
                    )}
                    {message.fullCode && (
                      <div className="mt-2 p-2 bg-gray-800 rounded text-xs font-mono text-gray-300 overflow-x-auto">
                        {message.fullCode.substring(0, 200)}
                        {message.fullCode.length > 200 ? '...' : ''}
                      </div>
                    )}
                    <div className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              )
            })}

            {isFinished && (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Interview Completed!</h3>
                <p className="text-gray-600 mb-4">Thank you for participating in this AI interview session.</p>
                {scores && (
                  <div className="bg-gray-50 rounded-lg p-4 mt-4">
                    <h4 className="font-semibold mb-2">Final Scores</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>Technical: {scores.final_scores?.technical || 'N/A'}/10</div>
                      <div>Communication: {scores.final_scores?.communication || 'N/A'}/10</div>
                      <div>Problem Solving: {scores.final_scores?.problem_solving || 'N/A'}/10</div>
                      <div>Relevance: {scores.final_scores?.relevance || 'N/A'}/10</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          {!isFinished && (
            <form onSubmit={handleSubmit} className="border-t border-gray-200 p-6">
              <div className="flex gap-4">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Type your answer here..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                />
                <button
                  type="submit"
                  disabled={!inputText.trim()}
                  className="px-8 py-4 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
                >
                  Send
                </button>
              </div>
            </form>
          )}
        </div>

        {showCodeEditor && codeQuestion && (
          <CodeEditor
            language={codeQuestion.language}
            starterCode={codeQuestion.starterCode}
            onSubmit={handleCodeSubmit}
            onClose={() => {
              setShowCodeEditor(false)
              setCodeQuestion(null)
            }}
          />
        )}
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-black text-[#0A2A6B] mb-2 uppercase">AI Interview Practice</h1>
        <p className="text-xl text-gray-600">Upload your CV and practice with AI-powered interview questions</p>
      </div>

      <div className="bg-white rounded-3xl shadow-lg border-2 border-gray-100 p-8 hover:shadow-2xl transition-all duration-300">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Position</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Upload CV (PDF)</label>
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center hover:border-gray-400 bg-gray-50 transition-colors duration-200">
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
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">{error}</div>
        )}

        <button
          onClick={startInterview}
          disabled={loading || !file}
          className="w-full py-4 px-8 bg-[#0A2A6B] text-white font-bold rounded-xl hover:bg-blue-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 shadow-lg flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Starting Interview...
            </>
          ) : (
            'Start Interview'
          )}
        </button>
      </div>
    </div>
  )
}

export default AIInterview

