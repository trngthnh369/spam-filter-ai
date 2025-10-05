import { useState } from 'react'
import { Send, Loader2, AlertCircle } from 'lucide-react'

interface ClassifierFormProps {
    onClassify: (message: string, k: number, explain: boolean) => void
    loading: boolean
}

export function ClassifierForm({ onClassify, loading }: ClassifierFormProps) {
    const [message, setMessage] = useState('')
    const [k, setK] = useState(5)
    const [explain, setExplain] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        
        if (!message.trim()) {
          setError('Please enter a message')
          return
        }
        
        if (message.length > 10000) {
          setError('Message too long (max 10000 characters)')
          return
        }
        
        setError('')
        onClassify(message.trim(), k, explain)
    }

    const exampleMessages = [
    "Hello, how are you doing today?",
    "Congratulations! You've won $1000! Click here now!",
    "Meeting rescheduled to 3pm tomorrow",
    "URGENT: Your account will be suspended. Verify immediately!",
    ]

    return (
    <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Classify Message</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
        {/* Message Input */}
        <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
            Message Text
            </label>
            <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your message here..."
            className="w-full h-32 px-4 py-3 border text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={loading}
            />
            <div className="flex justify-between items-center mt-1">
            <span className="text-xs text-gray-500">
                {message.length} / 10000 characters
            </span>
            {error && (
                <span className="text-xs text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {error}
                </span>
            )}
            </div>
        </div>

        {/* Example Messages */}
        <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Quick Examples:</p>
            <div className="grid grid-cols-2 text-gray-900 gap-2">
            {exampleMessages.map((example, idx) => (
                <button
                key={idx}
                type="button"
                onClick={() => setMessage(example)}
                disabled={loading}
                className="text-left px-3 py-2 text-xs bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors disabled:opacity-50"
                >
                {example.substring(0, 50)}...
                </button>
            ))}
            </div>
        </div>

        {/* Settings */}
        <div className="grid grid-cols-2 gap-4">
            <div>
            <label htmlFor="k" className="block text-sm font-medium text-gray-700 mb-2">
                K Neighbors
            </label>
            <input
                type="number"
                id="k"
                value={k}
                onChange={(e) => setK(parseInt(e.target.value))}
                min={1}
                max={20}
                className="w-full px-3 py-2 border text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">Number of nearest neighbors (1-20)</p>
            </div>

            <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
                <input
                type="checkbox"
                checked={explain}
                onChange={(e) => setExplain(e.target.checked)}
                disabled={loading}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                Enable Explainability
                </span>
            </label>
            </div>
        </div>

        {/* Submit Button */}
        <button
            type="submit"
            disabled={loading || !message.trim()}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
            {loading ? (
            <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
            </>
            ) : (
            <>
                <Send className="w-5 h-5" />
                Classify Message
            </>
            )}
        </button>
        </form>
    </div>
    )
}    