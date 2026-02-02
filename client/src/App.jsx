import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  // State
  const [mode, setMode] = useState('record') // 'record' or 'upload'
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [reports, setReports] = useState([]) // Array of { id, content, timestamp }
  const [error, setError] = useState('')
  const [copiedId, setCopiedId] = useState(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [expandedReportId, setExpandedReportId] = useState(null)
  
  // Settings
  const [pauseThreshold, setPauseThreshold] = useState(0.6)
  const [modelSize, setModelSize] = useState('small')
  
  // Refs
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)
  const fileInputRef = useRef(null)

  // Cleanup audio URL on unmount or change
  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl)
    }
  }, [audioUrl])

  // Start recording
  const startRecording = async () => {
    setError('')
    // Don't clear reports history, only current recording state
    setAudioBlob(null)
    setAudioUrl(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      })
      
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(track => track.stop())
        handleTranscribe(blob)
      }
      
      mediaRecorder.start()
      setIsRecording(true)
      setElapsedTime(0)
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1)
      }, 1000)
    } catch (err) {
      setError('Microphone access denied or not available.')
    }
  }

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }

  // Handle file upload
  const handleFileUpload = (e) => {
    setError('')
    // Don't clear reports history
    const file = e.target.files?.[0]
    if (file) {
      setAudioBlob(file)
      setAudioUrl(URL.createObjectURL(file))
      handleTranscribe(file) // Auto-transcribe immediately
    }
  }

  // Submit for transcription
  const handleTranscribe = async (arg) => {
    let blob = audioBlob
    if (arg instanceof Blob) {
      blob = arg
    }

    if (!blob) {
      setError('Please record or upload audio first.')
      return
    }
    
    setIsProcessing(true)
    setError('')
    
    try {
      const formData = new FormData()
      formData.append('file', blob, 'audio.webm')
      formData.append('source', mode)
      formData.append('pause_threshold', pauseThreshold.toString())
      formData.append('model_size', modelSize)
      
      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Transcription failed.')
      }
      
      const data = await response.json()
      const newReportId = Date.now()
      setReports(prev => [
        { 
          id: newReportId, 
          content: data.report, 
          timestamp: new Date().toLocaleString() 
        }, 
        ...prev
      ])
      setExpandedReportId(newReportId) // Auto-expand new report
    } catch (err) {
      setError(err.message || 'An error occurred during transcription.')
    } finally {
      setIsProcessing(false)
    }
  }

  // Copy report to clipboard
  const handleCopy = async (content, id) => {
    if (content) {
      await navigator.clipboard.writeText(content)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    }
  }

  // Delete report
  const handleDelete = (id) => {
    setReports(prev => prev.filter(report => report.id !== id))
  }

  // Reset
  const handleReset = () => {
    setAudioBlob(null)
    setAudioUrl(null)
    // Don't clear reports
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎤 Speaking Practice Aid</h1>
        <p className="subtitle">Local-only speech analysis with filler detection & pause timeline</p>
      </header>

      <main className="main-content">
        {/* Mode Selector */}
        <div className="mode-selector">
          <button 
            className={`mode-btn ${mode === 'record' ? 'active' : ''}`}
            onClick={() => { setMode('record'); handleReset(); }}
          >
            🎙️ Record
          </button>
          <button 
            className={`mode-btn ${mode === 'upload' ? 'active' : ''}`}
            onClick={() => { setMode('upload'); handleReset(); }}
          >
            📁 Upload
          </button>
        </div>

        {/* Settings Panel */}
        <div className="settings-panel">
          <div className="setting-item">
            <label htmlFor="pauseThreshold">Pause Threshold (s):</label>
            <input
              id="pauseThreshold"
              type="number"
              min="0.4"
              max="1.2"
              step="0.1"
              value={pauseThreshold}
              onChange={(e) => setPauseThreshold(parseFloat(e.target.value))}
            />
          </div>
          <div className="setting-item">
            <label htmlFor="modelSize">Whisper Model:</label>
            <select
              id="modelSize"
              value={modelSize}
              onChange={(e) => setModelSize(e.target.value)}
            >
              <option value="tiny">Tiny (fastest)</option>
              <option value="base">Base (recommended)</option>
              <option value="small">Small (more accurate)</option>
            </select>
          </div>
        </div>

        {/* Audio Input Area */}
        <div className="audio-input-area">
          {mode === 'record' ? (
            <div className="record-section">
              {!isRecording ? (
                <button className="action-btn record-btn" onClick={startRecording}>
                  🔴 Start Recording
                </button>
              ) : (
                <button className="action-btn stop-btn" onClick={stopRecording}>
                  ⏹️ Stop Recording
                </button>
              )}
              {isRecording && (
                <div className="recording-indicator">
                  <span className="recording-dot"></span>
                  Recording... {Math.floor(elapsedTime / 60)}:{(elapsedTime % 60).toString().padStart(2, '0')}
                </div>
              )}
            </div>
          ) : (
            <div className="upload-section">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="file-input"
              />
            </div>
          )}

          {/* Audio Preview */}
          {audioUrl && (
            <div className="audio-preview">
              <audio controls src={audioUrl} />
              <button className="reset-btn" onClick={handleReset}>Clear</button>
            </div>
          )}
        </div>



        {/* Error Display */}
        {error && <div className="error-message">{error}</div>}

        {/* Report Display */}
        {reports.length > 0 && (
          <div className="report-section">
            {reports.map((item, index) => {
              const isExpanded = expandedReportId === item.id || (expandedReportId === null && index === 0);
              
              return (
                <div 
                  key={item.id} 
                  className={`report-item ${isExpanded ? 'expanded' : ''}`}
                >
                  <div 
                    className="report-summary"
                    onClick={() => setExpandedReportId(isExpanded ? null : item.id)}
                  >
                    <span className="summary-title">📋 Report #{reports.length - index}</span>
                    <span className="summary-date">{item.timestamp}</span>
                  </div>
                  
                  {isExpanded && (
                    <div className="report-content-wrapper">
                      <div className="report-header">
                        <span className="timestamp">ID: {item.id}</span>
                        <div className="report-actions">
                          <button className="copy-btn" onClick={(e) => { e.stopPropagation(); handleCopy(item.content, item.id); }}>
                            {copiedId === item.id ? '✅ Copied!' : '📋 Copy'}
                          </button>
                          <button className="delete-btn" onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }} title="Delete Report">
                            🗑️
                          </button>
                        </div>
                      </div>
                      <textarea
                        className="report-textarea"
                        value={item.content}
                        readOnly
                        rows={15}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Local-only processing. No data sent to external servers.</p>
      </footer>
    </div>
  )
}

export default App
