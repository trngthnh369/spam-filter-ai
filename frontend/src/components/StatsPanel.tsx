import { useEffect, useState } from 'react'
import { Database, TrendingUp, Users, Activity } from 'lucide-react'

interface Stats {
  total_training_samples: number
  label_distribution: { ham: number; spam: number }
  class_weights: { ham: number; spam: number }
  model_name: string
  best_alpha: number
  faiss_index_size: number
}

export function StatsPanel() {
    const [stats, setStats] = useState<Stats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
  
    useEffect(() => {
      fetchStats()
    }, [])

    const fetchStats = async () => {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stats`)
          if (!response.ok) throw new Error('Failed to fetch stats')
          const data = await response.json()
          setStats(data)
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Unknown error')
        } finally {
          setLoading(false)
        }
    }

    if (loading) {
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        )
    }

    if (error || !stats) {
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-red-600">Failed to load statistics</p>
          </div>
        )
    }

    const totalSamples = stats.total_training_samples
    const hamPercent = ((stats.label_distribution.ham / totalSamples) * 100).toFixed(1)
    const spamPercent = ((stats.label_distribution.spam / totalSamples) * 100).toFixed(1)

    return (
        <div className="space-y-6">
          {/* Model Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <Database className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Model Info</h3>
            </div>
            
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-600">Model</p>
                <p className="font-medium text-gray-900 text-xs break-all">
                  {stats.model_name}
                </p>
              </div>
              
              <div>
                <p className="text-gray-600">Optimal Alpha</p>
                <p className="font-medium text-gray-900">{stats.best_alpha.toFixed(2)}</p>
              </div>
              
              <div>
                <p className="text-gray-600">Index Size</p>
                <p className="font-medium text-gray-900">
                  {stats.faiss_index_size.toLocaleString()} vectors
                </p>
              </div>
            </div>
          </div>
    
          {/* Training Data */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Training Data</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Total Samples</span>
                  <span className="text-sm font-bold text-gray-900">
                    {totalSamples.toLocaleString()}
                  </span>
                </div>
              </div>
    
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Ham</span>
                  <span className="text-sm font-medium text-green-600">
                    {stats.label_distribution.ham.toLocaleString()} ({hamPercent}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${hamPercent}%` }}
                  />
                </div>
              </div>
    
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Spam</span>
                  <span className="text-sm font-medium text-red-600">
                    {stats.label_distribution.spam.toLocaleString()} ({spamPercent}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-red-600 h-2 rounded-full"
                    style={{ width: `${spamPercent}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
    
          {/* Class Weights */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Class Weights</h3>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Ham</span>
                <span className="font-medium text-gray-900">
                {stats?.class_weights?.ham?.toFixed(3) ?? 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Spam</span>
                <span className="font-medium text-gray-900">
                {stats?.class_weights?.spam?.toFixed(3) ?? 'N/A'}
                </span>
              </div>
            </div>
            
            <p className="text-xs text-gray-500 mt-3">
              Higher weights for minority class to handle imbalance
            </p>
          </div>
    
          {/* Performance Badge */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-md p-6 text-white">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5" />
              <h3 className="text-lg font-semibold">Performance</h3>
            </div>
            <p className="text-3xl font-bold mb-1">95%+</p>
            <p className="text-sm opacity-90">Average Accuracy</p>
          </div>
        </div>
    )
}
