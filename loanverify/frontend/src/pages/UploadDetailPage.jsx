import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import {
  AlertTriangle, CheckCircle, Shield, Hash, Link2, ExternalLink,
  ChevronDown, ChevronRight, Loader2, Brain, Download, FileText,
  CheckSquare, Square, Trash2, XCircle, Filter
} from 'lucide-react'

export default function UploadDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [records, setRecords] = useState([])
  const [exceptions, setExceptions] = useState([])
  const [activeTab, setActiveTab] = useState('exceptions')
  const [chainVerification, setChainVerification] = useState(null)
  const [selectedExceptions, setSelectedExceptions] = useState(new Set())
  const [severityFilter, setSeverityFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    try {
      const [s, r, e] = await Promise.all([
        api.get(`/api/uploads/${id}`),
        api.get(`/api/uploads/${id}/records`),
        api.get(`/api/uploads/${id}/exceptions`),
      ])
      setSummary(s); setRecords(r); setExceptions(e)
    } catch (err) { toast.error(err.message) }
    finally { setLoading(false) }
  }

  const verifyChain = async () => {
    try {
      const data = await api.get(`/api/audit/chain-verify/${id}`)
      setChainVerification(data)
      toast.success(data.chain_valid ? 'Chain verified ✓' : `Chain broken at ${data.broken_links.length} records`)
    } catch (err) { toast.error(err.message) }
  }

  const explainException = async (excId) => {
    try {
      const data = await api.post(`/api/exceptions/${excId}/explain`)
      setExceptions(prev => prev.map(e => e.id === excId ? { ...e, ai_explanation: data.explanation, status: 'explained' } : e))
      toast.success('AI explanation generated')
    } catch (err) { toast.error(err.message) }
  }

  const resolveException = async (excId, action) => {
    try {
      await api.post(`/api/exceptions/${excId}/resolve`, {
        resolution_note: `Resolved by ${user.username}`,
        action,
      })
      setExceptions(prev => prev.map(e => e.id === excId ? { ...e, status: action, resolved_at: new Date().toISOString() } : e))
      const s = await api.get(`/api/uploads/${id}`)
      setSummary(s)
      toast.success(`Exception ${action}`)
    } catch (err) { toast.error(err.message) }
  }

  // ── Bulk Operations ──────────────────────────────
  const toggleSelect = (excId) => {
    setSelectedExceptions(prev => {
      const next = new Set(prev)
      next.has(excId) ? next.delete(excId) : next.add(excId)
      return next
    })
  }

  const toggleSelectAll = () => {
    const filtered = getFilteredExceptions()
    if (selectedExceptions.size === filtered.length) {
      setSelectedExceptions(new Set())
    } else {
      setSelectedExceptions(new Set(filtered.map(e => e.id)))
    }
  }

  const bulkResolve = async (action) => {
    if (selectedExceptions.size === 0) return
    try {
      await api.post('/api/exceptions/bulk-resolve', {
        exception_ids: Array.from(selectedExceptions),
        action,
        resolution_note: `Bulk ${action} by ${user.username}`,
      })
      toast.success(`${selectedExceptions.size} exceptions ${action}`)
      setSelectedExceptions(new Set())
      loadData()
    } catch (err) { toast.error(err.message) }
  }

  const bulkExplain = async () => {
    if (selectedExceptions.size === 0) return
    try {
      toast.loading('Generating explanations...')
      await api.post('/api/exceptions/bulk-explain', {
        exception_ids: Array.from(selectedExceptions),
      })
      toast.dismiss()
      toast.success(`${selectedExceptions.size} explanations generated`)
      setSelectedExceptions(new Set())
      loadData()
    } catch (err) { toast.dismiss(); toast.error(err.message) }
  }

  // ── Export Functions ──────────────────────────────
  const downloadFile = async (endpoint, filename) => {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/exports/${id}/${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Download failed')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = filename; a.click()
      URL.revokeObjectURL(url)
      toast.success(`Downloaded ${filename}`)
    } catch (err) { toast.error(err.message) }
  }

  const getFilteredExceptions = () => {
    return exceptions.filter(e => {
      if (severityFilter !== 'all' && e.severity !== severityFilter) return false
      if (statusFilter !== 'all' && e.status !== statusFilter) return false
      return true
    })
  }

  if (loading) return <LoadingSkeleton />
  if (!summary) return <div className="text-center py-12 text-gray-500">Upload not found</div>

  const filteredExceptions = getFilteredExceptions()
  const tabs = [
    { id: 'exceptions', label: 'Exceptions', count: summary.total_exceptions },
    { id: 'records', label: 'Loan Records', count: summary.total_records },
    { id: 'audit', label: 'Audit & Hash Chain', count: null },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{summary.upload.original_filename}</h1>
          <p className="text-gray-500">{summary.total_records} records · Uploaded {new Date(summary.upload.created_at).toLocaleDateString()}</p>
        </div>
        <div className="flex items-center gap-3">
          <QualityBadge score={summary.quality_score} />
          <StatusBadge status={summary.upload.status} />
        </div>
      </div>

      {/* Export Buttons */}
      <div className="card">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold flex items-center gap-2"><Download className="w-5 h-5 text-primary-600" /> Export Data</h3>
          <div className="flex gap-2">
            <button onClick={() => downloadFile('verified-csv', `verified_${summary.upload.original_filename}`)}
              className="btn-primary text-sm flex items-center gap-2">
              <CheckCircle className="w-4 h-4" /> Verified CSV
            </button>
            <button onClick={() => downloadFile('full-csv', `full_${summary.upload.original_filename}`)}
              className="btn-secondary text-sm flex items-center gap-2">
              <FileText className="w-4 h-4" /> Full CSV
            </button>
            {['reviewer', 'admin'].includes(user?.role) && (
              <>
                <button onClick={() => downloadFile('audit-report', `audit_report.json`)}
                  className="btn-secondary text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Audit Report
                </button>
                <button onClick={() => downloadFile('hash-manifest', `hash_manifest.json`)}
                  className="btn-secondary text-sm flex items-center gap-2">
                  <Hash className="w-4 h-4" /> Hash Manifest
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStat label="Critical" value={summary.critical_count} color="text-red-600" />
        <MiniStat label="Warnings" value={summary.warning_count} color="text-yellow-600" />
        <MiniStat label="Info" value={summary.info_count} color="text-blue-600" />
        <MiniStat label="Resolved" value={summary.resolved_count} color="text-green-600" />
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-0">
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}>
              {tab.label}{tab.count !== null && <span className="ml-2 text-xs bg-gray-100 px-2 py-0.5 rounded-full">{tab.count}</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'exceptions' && (
        <ExceptionsList
          exceptions={filteredExceptions}
          allExceptions={exceptions}
          selectedExceptions={selectedExceptions}
          onToggleSelect={toggleSelect}
          onToggleSelectAll={toggleSelectAll}
          onExplain={explainException}
          onResolve={resolveException}
          onBulkResolve={bulkResolve}
          onBulkExplain={bulkExplain}
          severityFilter={severityFilter}
          statusFilter={statusFilter}
          onSeverityFilter={setSeverityFilter}
          onStatusFilter={setStatusFilter}
          userRole={user?.role}
        />
      )}

      {activeTab === 'records' && (
        <RecordsTable records={records} />
      )}

      {activeTab === 'audit' && (
        <AuditTab uploadId={id} verifyChain={verifyChain} chainVerification={chainVerification} />
      )}
    </div>
  )
}

function ExceptionsList({
  exceptions, allExceptions, selectedExceptions,
  onToggleSelect, onToggleSelectAll, onExplain, onResolve,
  onBulkResolve, onBulkExplain,
  severityFilter, statusFilter, onSeverityFilter, onStatusFilter,
  userRole
}) {
  return (
    <div className="space-y-4">
      {/* Filters & Bulk Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          {['all', 'critical', 'warning', 'info'].map(f => (
            <button key={f} onClick={() => onSeverityFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                severityFilter === f ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}>{f}</button>
          ))}
          <span className="text-gray-300">|</span>
          {['all', 'pending', 'explained', 'resolved', 'dismissed'].map(f => (
            <button key={f} onClick={() => onStatusFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                statusFilter === f ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}>{f}</button>
          ))}
        </div>

        {/* Bulk actions */}
        {selectedExceptions.size > 0 && ['reviewer', 'admin'].includes(userRole) && (
          <div className="flex items-center gap-2 bg-primary-50 px-3 py-2 rounded-lg">
            <span className="text-sm font-medium text-primary-700">{selectedExceptions.size} selected</span>
            <button onClick={onBulkExplain} className="btn-secondary text-xs flex items-center gap-1">
              <Brain className="w-3 h-3" /> Explain All
            </button>
            <button onClick={() => onBulkResolve('resolved')} className="btn-primary text-xs flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> Resolve All
            </button>
            <button onClick={() => onBulkResolve('dismissed')} className="btn-secondary text-xs flex items-center gap-1 text-red-600">
              <XCircle className="w-3 h-3" /> Dismiss All
            </button>
          </div>
        )}
      </div>

      {/* Select all */}
      <div className="flex items-center gap-2">
        <button onClick={onToggleSelectAll} className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900">
          {selectedExceptions.size === exceptions.length && exceptions.length > 0 ? (
            <CheckSquare className="w-4 h-4 text-primary-600" />
          ) : (
            <Square className="w-4 h-4" />
          )}
          Select all ({exceptions.length})
        </button>
      </div>

      {/* Exception cards */}
      <div className="space-y-3">
        {exceptions.length === 0 && <p className="text-gray-400 text-sm py-8 text-center">No exceptions matching filters</p>}
        {exceptions.map(exc => (
          <ExceptionCard
            key={exc.id}
            exc={exc}
            selected={selectedExceptions.has(exc.id)}
            onToggleSelect={onToggleSelect}
            onExplain={onExplain}
            onResolve={onResolve}
            userRole={userRole}
          />
        ))}
      </div>
    </div>
  )
}

function ExceptionCard({ exc, selected, onToggleSelect, onExplain, onResolve, userRole }) {
  const [expanded, setExpanded] = useState(false)
  const sevColors = { critical: 'badge-critical', warning: 'badge-warning', info: 'badge-info' }
  const statusColors = { pending: 'bg-gray-100 text-gray-700', explained: 'bg-purple-100 text-purple-700', resolved: 'badge-resolved', dismissed: 'bg-gray-100 text-gray-500 line-through' }

  return (
    <div className={`card hover:shadow-md transition-shadow ${selected ? 'ring-2 ring-primary-500 bg-primary-50' : ''}`}>
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button onClick={() => onToggleSelect(exc.id)} className="mt-1 flex-shrink-0">
          {selected ? <CheckSquare className="w-5 h-5 text-primary-600" /> : <Square className="w-5 h-5 text-gray-300 hover:text-gray-500" />}
        </button>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={sevColors[exc.severity]}>{exc.severity}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[exc.status] || ''}`}>{exc.status}</span>
            <span className="text-xs text-gray-400">Row {exc.row_index}</span>
          </div>
          <h4 className="font-medium text-gray-900">{exc.field_name} — {exc.rule_name}</h4>
          <p className="text-sm text-gray-600 mt-1">{exc.message}</p>
          {exc.actual_value && exc.expected_value && (
            <p className="text-xs text-gray-400 mt-1">
              Got: <code className="bg-red-50 text-red-700 px-1 rounded">{exc.actual_value}</code> ·
              Expected: <code className="bg-green-50 text-green-700 px-1 rounded">{exc.expected_value}</code>
            </p>
          )}
        </div>

        <div className="flex gap-2 flex-shrink-0">
          {!exc.ai_explanation && exc.status !== 'resolved' && exc.status !== 'dismissed' && (
            <button onClick={() => onExplain(exc.id)} className="btn-secondary text-xs flex items-center gap-1">
              <Brain className="w-3 h-3" /> Explain
            </button>
          )}
          {exc.status !== 'resolved' && exc.status !== 'dismissed' && ['reviewer', 'admin'].includes(userRole) && (
            <>
              <button onClick={() => onResolve(exc.id, 'resolved')} className="btn-primary text-xs">Resolve</button>
              <button onClick={() => onResolve(exc.id, 'dismissed')} className="btn-secondary text-xs">Dismiss</button>
            </>
          )}
        </div>
      </div>

      {exc.ai_explanation && (
        <div className="mt-3 p-3 bg-purple-50 rounded-lg border border-purple-100">
          <div className="flex items-center gap-2 mb-1">
            <Brain className="w-4 h-4 text-purple-600" />
            <span className="text-xs font-medium text-purple-700">AI Explanation</span>
          </div>
          <p className="text-sm text-purple-900">{exc.ai_explanation}</p>
        </div>
      )}
    </div>
  )
}

function RecordsTable({ records }) {
  const [page, setPage] = useState(0)
  const perPage = 15
  const pageRecords = records.slice(page * perPage, (page + 1) * perPage)
  const totalPages = Math.ceil(records.length / perPage)

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <th className="px-4 py-3">Row</th>
            <th className="px-4 py-3">Loan ID</th>
            <th className="px-4 py-3">Borrower</th>
            <th className="px-4 py-3">Amount</th>
            <th className="px-4 py-3">Rate</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Credit Score</th>
            <th className="px-4 py-3">Hash</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {pageRecords.map(rec => (
            <tr key={rec.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-gray-500">{rec.row_index}</td>
              <td className="px-4 py-3 font-medium">{rec.loan_id || '—'}</td>
              <td className="px-4 py-3">{rec.borrower_name || <span className="text-red-400">Missing</span>}</td>
              <td className="px-4 py-3">{rec.loan_amount != null ? `$${rec.loan_amount.toLocaleString()}` : '—'}</td>
              <td className="px-4 py-3">{rec.interest_rate != null ? `${rec.interest_rate}%` : '—'}</td>
              <td className="px-4 py-3">{rec.status || '—'}</td>
              <td className="px-4 py-3">{rec.credit_score || '—'}</td>
              <td className="px-4 py-3 font-mono text-xs text-gray-400">{rec.record_hash ? `${rec.record_hash.slice(0, 12)}…` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
          <span className="text-sm text-gray-500">Showing {page * perPage + 1}–{Math.min((page + 1) * perPage, records.length)} of {records.length}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary text-xs disabled:opacity-40">Prev</button>
            <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="btn-secondary text-xs disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}

function AuditTab({ uploadId, verifyChain, chainVerification }) {
  const [logs, setLogs] = useState([])

  useEffect(() => {
    api.get(`/api/audit/logs?upload_id=${uploadId}`).then(setLogs).catch(console.error)
  }, [uploadId])

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Link2 className="w-6 h-6 text-primary-600" />
            <div>
              <h3 className="font-semibold text-gray-900">Hash Chain Verification</h3>
              <p className="text-sm text-gray-500">Each record's hash depends on the previous record's hash</p>
            </div>
          </div>
          <button onClick={verifyChain} className="btn-primary text-sm flex items-center gap-2">
            <Shield className="w-4 h-4" /> Verify Chain
          </button>
        </div>

        {chainVerification && (
          <div className={`p-4 rounded-lg ${chainVerification.chain_valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center gap-2 mb-2">
              {chainVerification.chain_valid ? <CheckCircle className="w-5 h-5 text-green-600" /> : <AlertTriangle className="w-5 h-5 text-red-600" />}
              <span className={`font-medium ${chainVerification.chain_valid ? 'text-green-800' : 'text-red-800'}`}>
                {chainVerification.chain_valid ? 'Chain Integrity Verified ✓' : `Chain Broken — ${chainVerification.broken_links.length} broken links`}
              </span>
            </div>
            <p className="text-sm text-gray-600">{chainVerification.total_records} records checked</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Audit Log</h3>
        <div className="space-y-3">
          {logs.length === 0 && <p className="text-gray-400 text-sm">No audit entries yet</p>}
          {logs.map(log => (
            <div key={log.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-gray-900">{log.action.replace(/_/g, ' ')}</p>
                <p className="text-xs text-gray-500">{new Date(log.created_at).toLocaleString()} · User: {log.user_id?.slice(0, 8) || 'system'}</p>
                {log.details && Object.keys(log.details).length > 0 && (
                  <pre className="text-xs text-gray-600 mt-1 bg-white p-2 rounded border border-gray-200 overflow-x-auto">{JSON.stringify(log.details, null, 2)}</pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function QualityBadge({ score }) {
  const color = score >= 80 ? 'bg-green-100 text-green-800' : score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
  return <span className={`px-3 py-1.5 rounded-full text-sm font-bold ${color}`}>Score: {score}</span>
}

function StatusBadge({ status }) {
  const colors = { completed: 'bg-green-100 text-green-700', processing: 'bg-blue-100 text-blue-700', failed: 'bg-red-100 text-red-700' }
  return <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${colors[status] || 'bg-gray-100 text-gray-700'}`}>{status}</span>
}

function MiniStat({ label, value, color }) {
  return (
    <div className="card text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-64 bg-gray-200 rounded" />
      <div className="grid grid-cols-4 gap-4">{[1,2,3,4].map(i => <div key={i} className="h-20 bg-gray-200 rounded-xl" />)}</div>
      <div className="h-64 bg-gray-200 rounded-xl" />
    </div>
  )
}
