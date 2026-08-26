import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { api } from '../services/api'
import toast from 'react-hot-toast'
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Loader2, Eye, ArrowRight } from 'lucide-react'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const f = acceptedFiles[0]
    setFile(f)
    setResult(null)

    // Get preview
    try {
      const formData = new FormData()
      formData.append('file', f)
      const data = await fetch('/api/uploads/preview', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: formData,
      }).then(r => r.json())
      setPreview(data)
    } catch (err) {
      toast.error('Failed to preview file')
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const data = await api.uploadFile('/api/uploads', file)
      setResult(data)
      toast.success(`Processed ${data.record_count} records — Score: ${data.quality_score}`)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Loan Data</h1>
        <p className="text-gray-500">Upload a CSV or Excel file for verification</p>
      </div>

      {/* Drop zone */}
      {!preview && (
        <div
          {...getRootProps()}
          className={`card border-2 border-dashed cursor-pointer transition-all ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center py-12">
            <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-primary-600" />
            </div>
            <p className="text-lg font-medium text-gray-700">
              {isDragActive ? 'Drop your file here' : 'Drag & drop your loan tape file'}
            </p>
            <p className="text-sm text-gray-500 mt-1">or click to browse — CSV and Excel files</p>
            <div className="flex gap-2 mt-4">
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
                <FileSpreadsheet className="w-3 h-3" /> .csv
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
                <FileSpreadsheet className="w-3 h-3" /> .xlsx
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Preview */}
      {preview && !result && (
        <div className="space-y-4">
          {/* File info */}
          <div className="card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Eye className="w-5 h-5 text-primary-600" />
                <div>
                  <h3 className="font-semibold">Preview: {file?.name}</h3>
                  <p className="text-sm text-gray-500">{preview.total_rows} rows, {preview.columns.length} columns detected</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => { setFile(null); setPreview(null) }} className="btn-secondary text-sm">
                  Choose Different File
                </button>
                <button onClick={handleUpload} disabled={uploading} className="btn-primary text-sm flex items-center gap-2">
                  {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                  {uploading ? 'Processing...' : 'Process & Validate'}
                </button>
              </div>
            </div>
          </div>

          {/* Column Mappings */}
          <div className="card">
            <h3 className="font-semibold mb-3">Detected Column Mappings</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase">
                    <th className="px-3 py-2">Original Column</th>
                    <th className="px-3 py-2">→</th>
                    <th className="px-3 py-2">Normalized Field</th>
                    <th className="px-3 py-2">Data Type</th>
                    <th className="px-3 py-2">Sample Values</th>
                    <th className="px-3 py-2">Nulls</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {preview.column_mappings.map((m, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-3 py-2 font-mono text-xs">{m.original}</td>
                      <td className="px-3 py-2 text-gray-400">→</td>
                      <td className="px-3 py-2">
                        <span className={`font-medium ${m.normalized === '(unmapped)' ? 'text-red-500' : 'text-green-700'}`}>
                          {m.normalized}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{m.data_type}</span>
                      </td>
                      <td className="px-3 py-2 text-xs text-gray-500 font-mono">
                        {m.sample_values.join(', ')}
                      </td>
                      <td className="px-3 py-2 text-xs">
                        {m.null_count > 0 ? (
                          <span className="text-yellow-600">{m.null_count} nulls</span>
                        ) : (
                          <span className="text-green-600">complete</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Preview Data */}
          <div className="card overflow-x-auto">
            <h3 className="font-semibold mb-3">First 5 Rows</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  {preview.columns.map(col => (
                    <th key={col} className="px-3 py-2 text-left text-xs font-medium text-gray-500 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {preview.preview_rows.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {preview.columns.map(col => (
                      <td key={col} className="px-3 py-2 text-xs whitespace-nowrap max-w-[150px] truncate">
                        {row[col] === '' || row[col] === null || row[col] === undefined ? (
                          <span className="text-gray-300">—</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="card border-green-200 bg-green-50">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-green-900">Upload Complete</h3>
              <p className="text-sm text-green-700 mt-1">
                Processed <strong>{result.record_count}</strong> records — Quality Score: <strong>{result.quality_score}</strong>/100
              </p>
              <div className="flex gap-3 mt-4">
                <button onClick={() => navigate(`/uploads/${result.id}`)} className="btn-primary text-sm">
                  View Details & Exceptions →
                </button>
                <button onClick={() => { setFile(null); setPreview(null); setResult(null) }} className="btn-secondary text-sm">
                  Upload Another File
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info cards */}
      {!preview && !result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <InfoCard icon={Eye} title="Preview First" desc="See column mappings and sample rows before processing" />
          <InfoCard icon={FileSpreadsheet} title="Smart Detection" desc="Auto-detects 50+ column name variants and data types" />
          <InfoCard icon={CheckCircle} title="Instant Validation" desc="Get quality score and exceptions in seconds" />
        </div>
      )}
    </div>
  )
}

function InfoCard({ icon: Icon, title, desc }) {
  return (
    <div className="card">
      <Icon className="w-8 h-8 text-primary-600 mb-3" />
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-500">{desc}</p>
    </div>
  )
}
