import React, { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const demoPayload = {
  customer_id: '11111111-1111-1111-1111-111111111111',
  telemetry: {
    vehicle_id: 'VEH-001',
    speed_kph: 62,
    engine_temp_c: 108,
    vibration_rms: 0.82,
    oil_pressure_kpa: 155,
    battery_v: 11.5,
    odometer_km: 120000,
    ambient_temp_c: 28
  }
}

export default function App() {
  const [jsonText, setJsonText] = useState(JSON.stringify(demoPayload, null, 2))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const parsed = useMemo(() => {
    try {
      return JSON.parse(jsonText)
    } catch {
      return null
    }
  }, [jsonText])

  async function runOrchestrate() {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonText
      })
      if (!res.ok) {
        const msg = await res.text()
        throw new Error(msg || `HTTP ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-5xl p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Autonomous Predictive Maintenance</h1>
          <p className="mt-1 text-sm text-slate-600">Trigger orchestration and view risk, booking, and RCA.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium">Request Payload</h2>
              <button
                className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                onClick={runOrchestrate}
                disabled={loading || !parsed}
              >
                {loading ? 'Running…' : 'POST /orchestrate'}
              </button>
            </div>

            <textarea
              className="mt-3 h-96 w-full resize-none rounded-lg border border-slate-200 bg-slate-50 p-3 font-mono text-xs focus:outline-none"
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
            />

            <div className="mt-2 text-xs text-slate-600">
              API Base: <span className="font-mono">{API_BASE}</span>
            </div>

            {!parsed && <div className="mt-2 text-xs text-red-600">Invalid JSON</div>}
            {error && <div className="mt-2 text-xs text-red-600">{error}</div>}
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="text-sm font-medium">Result</h2>

            {!result && (
              <div className="mt-3 text-sm text-slate-600">
                Run orchestration to see risk score, booking details, and RCA summary.
              </div>
            )}

            {result && (
              <div className="mt-3 space-y-4">
                <div className="rounded-lg border border-slate-200 p-3">
                  <div className="text-xs text-slate-600">Risk</div>
                  <div className="mt-1 text-lg font-semibold">
                    {Math.round(result.prediction.risk_score * 100)}% ({result.prediction.risk_level})
                  </div>
                  <div className="text-sm text-slate-700">Component: {result.prediction.predicted_component}</div>
                </div>

                <div className="rounded-lg border border-slate-200 p-3">
                  <div className="text-xs text-slate-600">Booking</div>
                  <div className="mt-1 text-sm">
                    <div>Center: <span className="font-medium">{result.booking.center_id}</span></div>
                    <div>Starts: <span className="font-mono">{result.booking.starts_at}</span></div>
                    <div>Status: <span className="font-medium">{result.booking.status}</span></div>
                  </div>
                </div>

                <div className="rounded-lg border border-slate-200 p-3">
                  <div className="text-xs text-slate-600">RCA</div>
                  <div className="mt-1 text-sm text-slate-800">{result.rca.summary}</div>
                </div>

                <div className="rounded-lg border border-slate-200 p-3">
                  <div className="text-xs text-slate-600">Voice Script (stub)</div>
                  <div className="mt-1 whitespace-pre-wrap text-sm text-slate-800">{result.voice_script}</div>
                </div>

                <details className="rounded-lg border border-slate-200 p-3">
                  <summary className="cursor-pointer text-xs text-slate-600">Raw JSON</summary>
                  <pre className="mt-2 overflow-auto rounded bg-slate-50 p-2 text-xs">{JSON.stringify(result, null, 2)}</pre>
                </details>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
