import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState('')
  const [uploading, setUploading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setDownloadUrl(data.download_url)
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="App">
      <h1>CSV Uploader</h1>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload CSV'}
      </button>
      {downloadUrl && (
        <p>
          <a href={downloadUrl} target="_blank" rel="noopener noreferrer">
            Download Processed CSV
          </a>
        </p>
      )}
    </div>
  )
}

export default App
