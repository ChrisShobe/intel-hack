import React, { useEffect, useState } from 'react';

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
      const response = await fetch('/api/upload', { method: 'POST', body: formData })

      if (!response.ok) {
        const errorResult = await response.json();
        setStatus(errorResult.message || 'Upload failed (server error).');
        return;
      }

      const result = await response.json();
      setStatus(result.message || 'Upload complete!');
    } catch (err) {
      setStatus('Upload failed (network error).');
      console.error(err);
    }
  };

  useEffect(() => {
    const apiURL = '/api';

    fetch(apiURL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Server is running:', data);
      })
      .catch((error) => {
        console.error('Error fetching the server status:', error);
    });
  }
  , []);

  return (
    <div className="p-4 min-h-screen bg-[#4F959D] text-white flex flex-col items-center justify-center">
      {/* Heading */}
      <h2 className="text-5xl font-bold text-center mb-12">Upload PDF File</h2>

      {/* Form */}
      <form onSubmit={handleUpload} className="flex flex-col items-center space-y-6">
        {/* Hidden file input */}
        <input
          type="file"
          accept="application/pdf"
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Clickable icon triggers file input */}
        <label htmlFor="file-upload" className="cursor-pointer">
          <img
            src="uploadicon.png"
            alt="Upload Icon"
            className="w-20 h-20 hover:opacity-80 transition"
          />
        </label>

        {/* Optional: show selected file name */}
        {file && <p className="text-xl">{file.name}</p>}

        {/* Submit button */}
        <button
          type="submit"
          className="px-8 py-3 bg-white text-[#4F959D] font-semibold rounded hover:bg-gray-100 transition"
        >
          Upload
        </button>
      </form>

      {/* Status Message */}
      {status && <p className="mt-6 text-center text-lg text-[red]">{status}</p>}
    </div>
  );
}

export default UploadPage;