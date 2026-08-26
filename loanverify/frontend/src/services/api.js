const BASE = ''

class APIClient {
  constructor() {
    this.token = null
  }

  setToken(token) {
    this.token = token
  }

  headers(extra = {}) {
    const h = { 'Content-Type': 'application/json', ...extra }
    if (this.token) h['Authorization'] = `Bearer ${this.token}`
    return h
  }

  async request(method, path, body = null, extraHeaders = {}) {
    const opts = { method, headers: this.headers(extraHeaders) }
    if (body && method !== 'GET') {
      opts.body = JSON.stringify(body)
    }
    const res = await fetch(`${BASE}${path}`, opts)
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Request failed')
    }
    return res.json()
  }

  get(path) { return this.request('GET', path) }
  post(path, body) { return this.request('POST', path, body) }
  put(path, body) { return this.request('PUT', path, body) }
  delete(path) { return this.request('DELETE', path) }

  async uploadFile(path, file) {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${this.token}` },
      body: form,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Upload failed')
    }
    return res.json()
  }
}

export const api = new APIClient()
