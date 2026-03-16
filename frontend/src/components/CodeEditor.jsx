import { useState, useEffect } from 'react'

const CodeEditor = ({ language = 'python', starterCode = '', onSubmit, onClose }) => {
  const [code, setCode] = useState(starterCode)

  useEffect(() => {
    if (starterCode) {
      setCode(starterCode)
    }
  }, [starterCode])

  const handleSubmit = () => {
    if (code.trim()) {
      onSubmit(code)
    }
  }

  const handleReset = () => {
    setCode(starterCode)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      const start = e.target.selectionStart
      const end = e.target.selectionEnd
      const newCode = code.substring(0, start) + '    ' + code.substring(end)
      setCode(newCode)
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4
      }, 0)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{'</>'}</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Code Editor</h3>
              <p className="text-sm text-gray-600">Language: {language}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Editor */}
        <div className="flex-1 p-4 overflow-auto">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Write your code here..."
            className="w-full h-full font-mono text-sm p-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ minHeight: '400px' }}
            spellCheck="false"
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <span>{code.length} characters</span>
            <span className="mx-2">•</span>
            <span>{code.split('\n').length} lines</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Reset
            </button>
            <button
              onClick={handleSubmit}
              disabled={!code.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Submit Solution
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CodeEditor

