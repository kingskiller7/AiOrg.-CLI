'use client';

import { useState } from 'react';

export default function Home() {
  const [task, setTask] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task) return;

    setIsLoading(true);
    setResult('');
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/execute-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setResult(JSON.stringify(data.result, null, 2) || 'No result returned.');

    } catch (err: any) {
      setError(err.message || 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-900 text-white">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl font-bold text-center mb-8">AI Organization</h1>
        
        <form onSubmit={handleSubmit} className="w-full">
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter your task for the organization..."
            className="w-full p-4 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow duration-300"
            rows={5}
            disabled={isLoading}
          />
          <button 
            type="submit"
            disabled={isLoading}
            className="w-full mt-4 px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors duration-300"
          >
            {isLoading ? 'Executing...' : 'Delegate Task'}
          </button>
        </form>

        {(result || error || isLoading) && (
          <div className="mt-8 w-full p-6 bg-gray-800 border border-gray-700 rounded-lg">
            <h2 className="text-2xl font-semibold mb-4">Result</h2>
            {isLoading && <p className="text-gray-400">The AI crew is working on your task. Please wait...</p>}
            {error && <pre className="text-red-400 whitespace-pre-wrap">{`Error: ${error}`}</pre>}
            {result && <pre className="text-gray-300 whitespace-pre-wrap">{result}</pre>}
          </div>
        )}
      </div>
    </main>
  );
}
