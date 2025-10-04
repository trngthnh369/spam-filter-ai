// frontend/src/pages/index.tsx
import { useState } from 'react'
import { ClassifierForm } from '@/components/ClassifierForm'
import { ResultDisplay } from '@/components/ResultDisplay'
import { StatsPanel } from '@/components/StatsPanel'
import { BarChart3, Shield, Zap } from 'lucide-react'

interface ClassificationResult {
  prediction: 'ham' | 'spam'
  is_spam: boolean
  confidence: number
  vote_scores: { ham: number; spam: number }
  subcategory?: string
  saliency_weight: number
  alpha: number
  neighbors: Array<{
    label: string
    similarity: number
    weight: number
    message: string
  }>
  tokens?: Array<{ token: string; saliency: number }>
  processing_time_ms: number
}

export default function Home() {
  const [result, setResult] = useState<ClassificationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleClassify = async (message: string, k: number, explain: boolean) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, k, explain })
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }
      
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Classification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Spam Filter AI</h1>
              <p className="text-sm text-gray-600">AI-powered spam detection with explainability</p>
            </div>
          </div>
        </div>
      </header>

      {/* Features Banner */}
      <div className="bg-blue-600 text-white py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              <span>Multilingual Support</span>
            </div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              <span>95%+ Accuracy</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span>Explainable AI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Input Form */}
          <div className="lg:col-span-2">
            <ClassifierForm onClassify={handleClassify} loading={loading} />
            
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}
            
            {result && (
              <div className="mt-6">
                <ResultDisplay result={result} />
              </div>
            )}
          </div>

          {/* Right Column - Stats */}
          <div className="lg:col-span-1">
            <StatsPanel />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Spam Filter AI v1.0 - Powered by multilingual-e5-base & FAISS
          </p>
        </div>
      </footer>
    </div>
  )
}