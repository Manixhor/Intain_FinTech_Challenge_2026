import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { FileCheck, Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('analyst')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isRegister) {
        await register(username, email, password, role)
      } else {
        await login(username, password)
      }
      toast.success(isRegister ? 'Account created!' : 'Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (u) => { setUsername(u); setPassword('demo123'); setIsRegister(false) }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-indigo-50">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FileCheck className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">LoanVerify</h1>
          <p className="text-gray-500 mt-1">AI-Powered Loan Data Verification</p>
        </div>

        {/* Form */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">{isRegister ? 'Create Account' : 'Sign In'}</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input className="input" value={username} onChange={e => setUsername(e.target.value)} required />
            </div>

            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <input className="input pr-10" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required />
                <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" onClick={() => setShowPw(!showPw)}>
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select className="input" value={role} onChange={e => setRole(e.target.value)}>
                  <option value="analyst">Analyst — Upload & view data</option>
                  <option value="reviewer">Reviewer — Resolve exceptions</option>
                  <option value="admin">Admin — Full access</option>
                </select>
              </div>
            )}

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button onClick={() => setIsRegister(!isRegister)} className="text-sm text-primary-600 hover:text-primary-700">
              {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
            </button>
          </div>
        </div>

        {/* Demo accounts */}
        <div className="mt-6 card bg-gray-50 border-dashed">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Demo Accounts (password: demo123)</p>
          <div className="flex gap-2">
            {['analyst', 'reviewer', 'admin'].map(u => (
              <button key={u} onClick={() => fillDemo(u)}
                className="flex-1 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:border-primary-300 hover:bg-primary-50 transition-colors capitalize">
                {u}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
