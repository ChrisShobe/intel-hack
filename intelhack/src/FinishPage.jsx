import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';


function FinishPage() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // Get current section from query param, default to 0
  const params = new URLSearchParams(location.search);
  const section = parseInt(params.get("section") || "0", 10);

  // Helper to get total number of questions (async)
  const getTotalQuestions = async () => {
    const res = await fetch('/quizData.json');
    const data = await res.json();
    return data.flatMap(chunk => chunk.questions).length;
  };

  const handleGenerate = async () => {
    const totalQuestions = await getTotalQuestions();
    const totalSections = Math.ceil(totalQuestions / 10);
    const nextSection = (section + 1) % totalSections;
    navigate(`/questions?section=${nextSection}`);
  };

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
    <div className="p-4 min-h-screen bg-[#4F959D] text-white flex flex-col items-center justify-center">
      {/* Heading */}
      <h2 className="text-5xl font-bold text-center mb-6">You've completed 10 questions!</h2>
      <h2 className="text-4xl font-bold text-center mb-12">Would you like to generate more?</h2>

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

        {/* Return button */}
        <button
          type="button"
          className="px-11 py-3 bg-white text-[#4F959D] font-semibold rounded hover:bg-gray-100 transition"
          onClick={() => navigate('/upload')}

        >
          Return to File Upload
        </button>

        {/* Generate button */}
        <button
          type="button"
          className="px-8 py-3 bg-white text-[#4F959D] font-semibold rounded hover:bg-gray-100 transition"
          onClick={handleGenerate}
        >
          Generate New Questions
        </button>
      </form>

    </div>
  );
}

export default FinishPage;