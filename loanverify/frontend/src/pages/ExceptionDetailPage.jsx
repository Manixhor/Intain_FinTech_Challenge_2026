import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Brain, ArrowLeft, CheckCircle, XCircle, Loader2, Send, MessageCircle } from 'lucide-react'

export default function ExceptionDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [exception, setException] = useState(null)
  const [loading, setLoading] = useState(true)
  const [explaining, setExplaining] = useState(false)

  useEffect(() => {
    api.get(`/api/exceptions/${id}`)
      .then(setException)
      .catch(err => toast.error(err.message))
      .finally(() => setLoading(false))
  }, [id])

  const getExplanation = async () => {
    setExplaining(true)
    try {
      const data = await api.post(`/api/exceptions/${id}/explain`)
      setException(prev => ({ ...prev, ai_explanation: data.explanation, status: 'explained' }))
      toast.success('Explanation generated')
    } catch (err) { toast.error(err.message) }
    finally { setExplaining(false) }
  }

  const resolve = async (action) => {
    try {
      await api.post(`/api/exceptions/${id}/resolve`, { resolution_note: `Resolved by ${user.username}`, action })
      setException(prev => ({ ...prev, status: action }))
      toast.success(`Exception ${action}`)
    } catch (err) { toast.error(err.message) }
  }

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 text-primary-500 animate-spin" /></div>
  if (!exception) return <div className="text-center py-12 text-gray-500">Not found</div>

  const sevColor = { critical: 'badge-critical', warning: 'badge-warning', info: 'badge-info' }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Exception Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <span className={sevColor[exception.severity]}>{exception.severity}</span>
              <span className="text-xs text-gray-500">Row {exception.row_index}</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">{exception.rule_name}</h2>
            <p className="text-gray-600 mt-2">{exception.message}</p>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="p-3 bg-red-50 rounded-lg">
                <p className="text-xs font-medium text-red-700 mb-1">Actual Value</p>
                <p className="text-sm font-mono text-red-900">{exception.actual_value || 'NULL'}</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-xs font-medium text-green-700 mb-1">Expected</p>
                <p className="text-sm font-mono text-green-900">{exception.expected_value || 'Any value'}</p>
              </div>
            </div>
          </div>

          {/* AI Explanation */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2"><Brain className="w-5 h-5 text-purple-600" /> AI Explanation</h3>
              {!exception.ai_explanation && (
                <button onClick={getExplanation} disabled={explaining} className="btn-primary text-sm flex items-center gap-2">
                  {explaining ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                  {explaining ? 'Generating...' : 'Get AI Explanation'}
                </button>
              )}
            </div>
            {exception.ai_explanation ? (
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                <p className="text-sm text-purple-900 leading-relaxed">{exception.ai_explanation}</p>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">Click "Get AI Explanation" to analyze this exception</p>
            )}
          </div>

          {/* Actions */}
          {exception.status !== 'resolved' && exception.status !== 'dismissed' && ['reviewer', 'admin'].includes(user?.role) && (
            <div className="card">
              <h3 className="font-semibold mb-4">Actions</h3>
              <div className="flex gap-3">
                <button onClick={() => resolve('resolved')} className="btn-primary flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Mark Resolved
                </button>
                <button onClick={() => resolve('dismissed')} className="btn-danger flex items-center gap-2">
                  <XCircle className="w-4 h-4" /> Dismiss
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: AI Chat Panel */}
        <div className="lg:col-span-1">
          <ChatPanel exception={exception} />
        </div>
      </div>
    </div>
  )
}

function ChatPanel({ exception }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hi! I'm LoanVerify AI. I can help you understand this data quality issue.\n\nTry asking me:\n• Is this a false positive?\n• What's the impact if I don't fix this?\n• How should I correct it?\n• Explain this exception`,
    },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || sending) return

    const userMsg = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setSending(true)

    try {
      const data = await api.post('/api/chat', {
        messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })),
        record_id: exception.record_id,
      })
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
    } finally {
      setSending(false)
    }
  }

  const quickQuestions = [
    'Is this a false positive?',
    'What is the impact?',
    'How do I fix this?',
    'Explain this exception',
  ]

  return (
    <div className="card h-[600px] flex flex-col">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
        <MessageCircle className="w-5 h-5 text-primary-600" />
        <h3 className="font-semibold">AI Copilot Chat</h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] px-3 py-2 rounded-lg text-sm ${
              msg.role === 'user'
                ? 'bg-primary-600 text-white rounded-br-none'
                : 'bg-gray-100 text-gray-900 rounded-bl-none'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-3 py-2 rounded-lg rounded-bl-none">
              <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick questions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {quickQuestions.map((q, i) => (
            <button key={i} onClick={() => setInput(q)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-700 transition-colors">
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        <input
          className="input flex-1 text-sm"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder="Ask about this exception..."
          disabled={sending}
        />
        <button onClick={sendMessage} disabled={!input.trim() || sending} className="btn-primary px-3">
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
