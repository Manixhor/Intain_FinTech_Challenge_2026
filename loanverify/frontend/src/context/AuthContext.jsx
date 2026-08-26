import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api.setToken(token)
      api.get('/api/auth/me')
        .then(data => setUser(data))
        .catch(() => { logout(); })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username, password) => {
    const data = await api.post('/api/auth/login', { username, password })
    localStorage.setItem('token', data.access_token)
    api.setToken(data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    return data
  }

  const register = async (username, email, password, role) => {
    const data = await api.post('/api/auth/register', { username, email, password, role })
    localStorage.setItem('token', data.access_token)
    api.setToken(data.access_token)
    setToken(data.access_token)
    setUser(data.user)
    return data
  }

  const logout = () => {
    localStorage.removeItem('token')
    api.setToken(null)
    setToken(null)
    setUser(null)
  }

  const hasRole = (...roles) => user && roles.includes(user.role)

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
