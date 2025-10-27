// src/pages/QuizPuzzles.jsx
import React, { useState } from 'react';

const QuizPuzzles = () => {
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const [moodSelection, setMoodSelection] = useState(null);

  const handleSubmitCaptcha = (e) => {
    e.preventDefault();
    // Simple placeholder logic for a human/bot check
    const correctSum = 15; 
    if (parseInt(captchaAnswer, 10) === correctSum) {
      alert('Success! You passed the attention check.');
    } else {
      alert('Incorrect. Please try again.');
    }
    setCaptchaAnswer('');
  };

  const handleMoodSelect = (mood) => {
    setMoodSelection(mood);
    alert(`Thank you for sharing. Mood selected: ${mood}. This information is being used for your mental well-being check.`);
  };

  return (
    <div className="max-w-4xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Cognitive and Well-being Puzzles</h2>
      <p className="text-md mb-6 text-gray-700">
        These interactive puzzles are designed not to test knowledge, but to check for cognitive state, mental focus, and well-being.
      </p>

      {/* Section 1: Attention Check (Human/Bot Puzzle) */}
      <section className="mb-6 border p-4 rounded">
        <h3 className="text-xl font-semibold mb-3">Attention Check: Prove You are Human</h3>
        <p className="mb-3">
          To ensure reliable well-being assessment, please solve the puzzle:
          <strong className="block text-lg mt-1">What is the sum of 7 and 8?</strong>
        </p>
        <form onSubmit={handleSubmitCaptcha} className="flex gap-2">
          <input
            type="number"
            value={captchaAnswer}
            onChange={(e) => setCaptchaAnswer(e.target.value)}
            className="p-2 border rounded w-32"
            placeholder="Enter sum"
            required
          />
          <button type="submit" className="btn btn-primary">Submit</button>
        </form>
      </section>

      {/* Section 2: Simple Mental State Assessment */}
      <section className="mb-6 border p-4 rounded bg-gray-100">
        <h3 className="text-xl font-semibold mb-3">Mental State Check: How are you feeling right now?</h3>
        <p className="mb-4 text-gray-700">Select the mood that best describes your current mental condition:</p>
        <div className="flex flex-wrap gap-4">
          {['Calm', 'Stressed', 'Anxious', 'Energetic', 'Fatigued', 'Neutral'].map((mood) => (
            <button
              key={mood}
              onClick={() => handleMoodSelect(mood)}
              className={`px-4 py-2 rounded shadow transition-colors ${
                moodSelection === mood
                  ? 'bg-blue-600 text-white font-bold'
                  : 'bg-white hover:bg-gray-200 text-gray-800'
              }`}
            >
              {mood}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
};

export default QuizPuzzles;