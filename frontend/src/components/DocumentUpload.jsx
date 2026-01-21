import { useState } from 'react';
import { Upload, File, CheckCircle, XCircle } from 'lucide-react';
import { documentsAPI } from '../services/api';

export default function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      const supported = ['txt', 'pdf', 'docx', 'md'];
      
      if (supported.includes(ext)) {
        setFile(selectedFile);
        setMessage(null);
      } else {
        setMessage({ type: 'error', text: `Unsupported file type. Use: ${supported.join(', ')}` });
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setMessage(null);

    try {
      const result = await documentsAPI.upload(file);
      setMessage({
        type: 'success',
        text: `Uploaded ${result.filename} - ${result.chunks} chunks indexed`,
      });
      setFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Upload failed',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2> Upload Documents</h2>
      
      <div className="upload-area">
        <input
          type="file"
          id="file-input"
          onChange={handleFileChange}
          accept=".txt,.pdf,.docx,.md"
          disabled={uploading}
        />
        <label htmlFor="file-input" className="file-label">
          <Upload size={24} />
          <span>{file ? file.name : 'Choose file (TXT, PDF, DOCX, MD)'}</span>
        </label>
      </div>

      {file && (
        <div className="file-info">
          <File size={20} />
          <span>{file.name} ({(file.size / 1024).toFixed(2)} KB)</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="btn btn-primary"
      >
        {uploading ? 'Uploading...' : 'Upload & Index'}
      </button>

      {message && (
        <div className={`message ${message.type}`}>
          {message.type === 'success' ? (
            <CheckCircle size={20} />
          ) : (
            <XCircle size={20} />
          )}
          <span>{message.text}</span>
        </div>
      )}
    </div>
  );
}
