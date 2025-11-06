 import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [uploads, setUploads] = useState([])

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    const uploadId = Date.now() + Math.random()
    const newUpload = { id: uploadId, fileName: file.name, status: 'uploading', downloadUrl: '' }
    setUploads(prev => [newUpload, ...prev])
    const formData = new FormData()
    formData.append('file', file)
    setFile(null) // Reset file input
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      const statusMap = {
        PENDING: 'Pending',
        STARTED: 'Processing',
        SUCCESS: 'Completed',
        FAILURE: 'Failed',
        RETRY: 'Retrying'
      }
      const friendlyStatus = statusMap[data.status] || data.status
      setUploads(prev => prev.map(upload =>
        upload.id === uploadId ? { ...upload, status: friendlyStatus, downloadUrl: data.download_url } : upload
      ))
    } catch (error) {
      console.error('Upload failed:', error)
      setUploads(prev => prev.map(upload =>
        upload.id === uploadId ? { ...upload, status: 'Failed' } : upload
      ))
    }
  }

  const handleCheck = async (upload) => {
    try {
      const response = await fetch(upload.downloadUrl, { method: 'HEAD' })
      if (response.ok) {
        setUploads(prev => prev.map(u =>
          u.id === upload.id ? { ...u, status: 'Completed' } : u
        ))
      }
    } catch (error) {
      console.error('Check failed:', error)
    }
  }

  return (
    <div className="App">
      <h1>CSV Uploader</h1>
      <input type="file" accept=".csv" onChange={handleFileChange} value={file ? undefined : ''} />
      <button onClick={handleUpload} disabled={!file}>
        Upload CSV
      </button>
      <table>
        <thead>
          <tr>
            <th>File Name</th>
            <th>Status</th>
            <th>Download</th>
          </tr>
        </thead>
        <tbody>
          {uploads.map(upload => (
            <tr key={upload.id}>
              <td>{upload.fileName}</td>
              <td>{upload.status}</td>
              <td>
                {upload.status === 'Completed' ? (
                  <a href={upload.downloadUrl} target="_blank" rel="noopener noreferrer">
                    📥
                  </a>
                ) : (
                  <button onClick={() => handleCheck(upload)}>🔄</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
