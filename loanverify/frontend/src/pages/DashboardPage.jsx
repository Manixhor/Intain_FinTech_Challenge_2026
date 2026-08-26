import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Upload, AlertTriangle, CheckCircle, TrendingUp, FileText, Clock } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/audit/dashboard')
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSkeleton />
  if (!stats) return <div className="text-center py-12 text-gray-500">No data yet. Upload a loan tape to get started!</div>

  const scoreColor = stats.avg_quality_score >= 80 ? 'text-green-600' : stats.avg_quality_score >= 50 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Overview of your loan data verification pipeline</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={FileText} label="Total Uploads" value={stats.total_uploads} color="primary" />
        <StatCard icon={Upload} label="Total Records" value={stats.total_records.toLocaleString()} color="blue" />
        <StatCard icon={AlertTriangle} label="Exceptions" value={stats.total_exceptions} color="red" />
        <StatCard icon={CheckCircle} label="Resolved" value={stats.resolved_exceptions} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quality Score */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Data Quality Score</h3>
          <div className="flex items-center justify-center">
            <div className="relative">
              <svg className="w-32 h-32" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                <circle cx="50" cy="50" r="45" fill="none" stroke={stats.avg_quality_score >= 80 ? '#22c55e' : stats.avg_quality_score >= 50 ? '#eab308' : '#ef4444'} strokeWidth="8" strokeDasharray={`${(stats.avg_quality_score / 100) * 283} 283`} strokeLinecap="round" transform="rotate(-90 50 50)" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-3xl font-bold ${scoreColor}`}>{stats.avg_quality_score}</span>
              </div>
            </div>
          </div>
          <p className="text-center text-sm text-gray-500 mt-3">Average across all uploads</p>
        </div>

        {/* Exception Breakdown */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Exception Breakdown</h3>
          <div className="space-y-4">
            <ExceptionBar label="Critical" count={stats.exception_breakdown.critical} total={stats.total_exceptions} color="bg-red-500" />
            <ExceptionBar label="Warning" count={stats.exception_breakdown.warning} total={stats.total_exceptions} color="bg-yellow-500" />
            <ExceptionBar label="Info" count={stats.exception_breakdown.info} total={stats.total_exceptions} color="bg-blue-500" />
          </div>
        </div>

        {/* Recent Uploads */}
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Recent Uploads</h3>
          <div className="space-y-3">
            {stats.recent_uploads.length === 0 && (
              <p className="text-gray-400 text-sm">No uploads yet</p>
            )}
            {stats.recent_uploads.map(upload => (
              <Link key={upload.id} to={`/uploads/${upload.id}`} className="block p-3 rounded-lg border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{upload.original_filename}</p>
                    <p className="text-xs text-gray-500">{upload.record_count} records</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-bold ${upload.quality_score >= 80 ? 'text-green-600' : upload.quality_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {upload.quality_score}
                    </span>
                    <StatusBadge status={upload.status} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Resolution progress */}
      {stats.total_exceptions > 0 && (
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">Resolution Progress</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 rounded-full transition-all" style={{ width: `${(stats.resolved_exceptions / stats.total_exceptions) * 100}%` }} />
            </div>
            <span className="text-sm font-medium text-gray-600">{stats.resolved_exceptions}/{stats.total_exceptions} resolved</span>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color }) {
  const bg = { primary: 'bg-primary-50 text-primary-600', blue: 'bg-blue-50 text-blue-600', red: 'bg-red-50 text-red-600', green: 'bg-green-50 text-green-600' }
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${bg[color]}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function ExceptionBar({ label, count, total, color }) {
  const pct = total > 0 ? (count / total) * 100 : 0
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{count}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const colors = {
    completed: 'bg-green-100 text-green-700',
    processing: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700',
  }
  return <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[status] || 'bg-gray-100 text-gray-700'}`}>{status}</span>
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />
      <div className="grid grid-cols-4 gap-6">
        {[1,2,3,4].map(i => <div key={i} className="h-24 bg-gray-200 rounded-xl" />)}
      </div>
      <div className="grid grid-cols-3 gap-6">
        {[1,2,3].map(i => <div key={i} className="h-64 bg-gray-200 rounded-xl" />)}
      </div>
    </div>
  )
}
