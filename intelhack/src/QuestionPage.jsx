import React, { useEffect, useState } from "react";

function QuestionPage() {
  const [quizData, setQuizData] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");

  // Load JSON on mount
  useEffect(() => {
    fetch("/quiz_data.json")
      .then((res) => res.json())
      .then((data) => {
        // Flatten questions from all chunks into a single array
        const allQuestions = data.flatMap(chunk => chunk.questions);
        setQuizData(allQuestions);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();

    const correctAnswer = quizData[currentIndex].answer.trim().toLowerCase();
    const userAnswer = answer.trim().toLowerCase();

    if (userAnswer === correctAnswer) {
      setFeedback("✅ Correct!");
    } else {
      setFeedback(`❌ Incorrect. Correct answer: ${quizData[currentIndex].answer}`);
    }
  };

  /*
  if (quizData.length === 0) {
    return <div className="p-4 text-white">Loading questions...</div>;
  }
  */

  return (
    <div className="p-4 min-h-screen bg-[#4F959D] text-white flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-6 text-center">Question {currentIndex + 1}</h2>
      <p className="text-xl mb-4 text-center">{quizData[currentIndex].question}</p>

      <form onSubmit={handleSubmit} className="w-full max-w-lg">
        <textarea
          id="answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your response here..."
          className="p-4 rounded text-black min-h-[150px] resize-y border border-gray-400 focus:outline focus:ring-2 focus:ring-[#E2E5AE] w-full"
        />
        <button
          type="submit"
          className="mt-4 px-6 py-2 bg-white text-[#4F959D] font-semibold rounded hover:bg-gray-100"
        >
          Submit
        </button>
      </form>

      {feedback && <p className="mt-6 text-xl text-center">{feedback}</p>}
    </div>
  );
}

export default QuestionPage;