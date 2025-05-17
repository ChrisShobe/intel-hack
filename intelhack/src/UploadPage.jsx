import React, { useState } from 'react';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const response = await fetch('https://9v5mh8sg-3000.usw3.devtunnels.ms/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      setStatus(result.message || 'Upload complete!');
    } catch (err) {
      setStatus('Upload failed.');
      console.error(err);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Upload PDF File</h2>
      <form onSubmit={handleUpload}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button type="submit" className="ml-2 px-4 py-2 bg-blue-600 text-white rounded">Upload</button>
      </form>
      {status && <p className="mt-4">{status}</p>}
    </div>
  );
}

export default UploadPage;