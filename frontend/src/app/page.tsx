'use client';

import { useState } from 'react';

export default function Home() {
  const [task, setTask] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const clearFile = () => {
    setFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task) return;

    setIsLoading(true);
    setResult('');
    setError('');
    setUploadProgress(0);

    let filePath: string | null = null;

    try {
      if (file) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'http://127.0.0.1:8000/api/upload', true);

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            setUploadProgress(percentComplete);
          }
        };

        const uploadPromise = new Promise<string>((resolve, reject) => {
          xhr.onload = () => {
            if (xhr.status === 200) {
              const response = JSON.parse(xhr.responseText);
              if (response.error) {
                reject(new Error(response.error));
              } else {
                resolve(response.file_path);
              }
            } else {
              reject(new Error(`File upload failed: ${xhr.statusText}`));
            }
          };
          xhr.onerror = () => {
            reject(new Error('File upload failed.'));
          };
        });

        xhr.send(formData);
        filePath = await uploadPromise;
      }

      const response = await fetch('http://127.0.0.1:8000/api/execute-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task, file_path: filePath }),
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
      setUploadProgress(0);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
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
          <div className="mt-4">
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-400 mb-2">
              Attach a file (optional)
            </label>
            <div className="flex items-center">
              <input 
                id="file-upload"
                type="file"
                onChange={handleFileChange}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                disabled={isLoading}
              />
              {file && (
                <button type="button" onClick={clearFile} className="ml-4 text-sm text-red-500 hover:text-red-700" disabled={isLoading}>Clear</button>
              )}
            </div>
            {file && (
              <div className="mt-2 text-sm text-gray-400">Selected file: {file.name}</div>
            )}
            {uploadProgress > 0 && (
              <div className="mt-2 w-full bg-gray-700 rounded-full h-2.5">
                <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${uploadProgress}%` }}></div>
              </div>
            )}
          </div>
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
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">Result</h2>
              {result && (
                <button onClick={copyToClipboard} className="text-sm text-blue-500 hover:text-blue-700">Copy</button>
              )}
            </div>
            {isLoading && <p className="text-gray-400">The AI crew is working on your task. Please wait...</p>}
            {error && <pre className="text-red-400 whitespace-pre-wrap">{`Error: ${error}`}</pre>}
            {result && <pre className="text-gray-300 whitespace-pre-wrap">{result}</pre>}
          </div>
        )}
      </div>
    </main>
  );
}
