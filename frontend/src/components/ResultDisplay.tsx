import { Shield, AlertTriangle, Clock, TrendingUp } from 'lucide-react'

interface ResultDisplayProps {
  result: {
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
}

export function ResultDisplay({ result }: ResultDisplayProps) {
    const isSpam = result.is_spam
    const confidencePercent = (result.confidence * 100).toFixed(1)
  
    const getSubcategoryLabel = (subcategory?: string) => {
      const labels: Record<string, string> = {
        'spam_quangcao': 'Advertising Spam',
        'spam_hethong': 'System/Security Spam',
        'spam_khac': 'Other Spam'
      }
      return subcategory ? labels[subcategory] || subcategory : 'N/A'
    }

    const getColorClasses = (isSpam: boolean) => {
        if (isSpam) {
          return {
            bg: 'bg-red-50',
            border: 'border-red-200',
            text: 'text-red-800',
            icon: 'text-red-600',
            badge: 'bg-red-100 text-red-800'
          }
        }
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-800',
          icon: 'text-green-600',
          badge: 'bg-green-100 text-green-800'
        }
    }

    const colors = getColorClasses(isSpam)

  return (
    <div className="space-y-6">
      {/* Main Result Card */}
      <div className={`${colors.bg} ${colors.border} border rounded-lg p-6`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {isSpam ? (
              <AlertTriangle className={`w-8 h-8 ${colors.icon}`} />
            ) : (
              <Shield className={`w-8 h-8 ${colors.icon}`} />
            )}
            <div>
              <h3 className={`text-2xl font-bold ${colors.text}`}>
                {isSpam ? 'SPAM DETECTED' : 'LEGITIMATE MESSAGE'}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Confidence: {confidencePercent}%
              </p>
            </div>
          </div>
          
          <span className={`px-3 py-1 ${colors.badge} rounded-full text-sm font-medium`}>
            {result.prediction.toUpperCase()}
          </span>
        </div>

        {/* Subcategory */}
        {isSpam && result.subcategory && (
          <div className="mt-4 pt-4 border-t border-red-200">
            <p className="text-sm text-gray-700">
              <span className="font-medium">Category:</span> {getSubcategoryLabel(result.subcategory)}
            </p>
          </div>
        )}
      </div>

      {/* Vote Scores */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Vote Scores</h4>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Ham (Legitimate)</span>
              <span className="text-sm text-gray-600">{result.vote_scores.ham.toFixed(3)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all"
                style={{
                  width: `${(result.vote_scores.ham / (result.vote_scores.ham + result.vote_scores.spam)) * 100}%`
                }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Spam</span>
              <span className="text-sm text-gray-600">{result.vote_scores.spam.toFixed(3)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-600 h-2 rounded-full transition-all"
                style={{
                  width: `${(result.vote_scores.spam / (result.vote_scores.ham + result.vote_scores.spam)) * 100}%`
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Token Saliency */}
      {result.tokens && result.tokens.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Token Importance</h4>
          <div className="flex flex-wrap gap-2">
            {result.tokens.map((token, idx) => {
              const opacity = Math.max(0.1, token.saliency)
              const bgColor = `rgba(239, 68, 68, ${opacity})`
              return (
                <span
                  key={idx}
                  className="px-2 py-1 rounded text-sm font-mono border border-gray-200"
                  style={{ backgroundColor: bgColor }}
                  title={`Saliency: ${token.saliency.toFixed(3)}`}
                >
                  {token.token}
                </span>
              )
            })}
          </div>
          <p className="text-xs text-gray-500 mt-3">
            Darker background indicates higher impact on spam prediction
          </p>
        </div>
      )}

      {/* Neighbors */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Top Similar Messages</h4>
        <div className="space-y-3">
          {result.neighbors.slice(0, 5).map((neighbor, idx) => (
            <div key={idx} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  neighbor.label === 'spam' 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {neighbor.label.toUpperCase()}
                </span>
                <div className="flex items-center gap-3 text-xs text-gray-600">
                  <span>Similarity: {(neighbor.similarity * 100).toFixed(1)}%</span>
                  <span>Weight: {neighbor.weight.toFixed(3)}</span>
                </div>
              </div>
              <p className="text-sm text-gray-700">{neighbor.message}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Analysis Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Saliency Weight</p>
            <p className="font-medium text-gray-900">{result.saliency_weight.toFixed(3)}</p>
          </div>
          <div>
            <p className="text-gray-600">Alpha Parameter</p>
            <p className="font-medium text-gray-900">{result.alpha.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-600">Processing Time</p>
            <p className="font-medium text-gray-900 flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {result.processing_time_ms.toFixed(2)}ms
            </p>
          </div>
          <div>
            <p className="text-gray-600">Neighbors Used</p>
            <p className="font-medium text-gray-900">{result.neighbors.length}</p>
          </div>
        </div>
      </div>
    </div>
  )
}