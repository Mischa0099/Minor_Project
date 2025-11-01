// src/pages/Profile.jsx
import React, { useState, useEffect } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Profile = () => {
  const [profile, setProfile] = useState({
    name: '',
    age: '',
    gender: '',
    weight: '',
    health_conditions: '',
    birthmarks: '',
    family_medication_history: '',
    previous_medication_history: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  
  // NEW STATE: Control when to show the puzzles
  const [showPuzzles, setShowPuzzles] = useState(false);
  
  // PUZZLE STATES
  const [captchaAnswer, setCaptchaAnswer] = useState('');
  const [moodSelection, setMoodSelection] = useState(null);

  const navigate = useNavigate();
  const { logout } = useContext(AuthContext);

  // Generate age options (e.g., 18 to 99)
  const ageOptions = Array.from({ length: 82 }, (_, i) => i + 4);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/api/user/profile');
        setProfile(response.data || {});
      } catch (error) {
        setMessage(error.friendlyMessage || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setShowPuzzles(false);
    try {
      await api.put('/api/user/profile', profile);
      setMessage('Profile updated successfully! Please complete the quick check below.');
      setShowPuzzles(true);
    } catch (error) {
      setMessage(error.friendlyMessage || 'Failed to update profile');
      setShowPuzzles(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // PUZZLE LOGIC
  const handleSubmitCaptcha = (e) => {
    e.preventDefault();
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

  // Puzzle Content JSX
  const PuzzleSection = () => (
    <div className="mt-8 pt-6 border-t border-gray-200">
        <h2 className="text-2xl font-bold mb-4 text-blue-600">Cognitive Check</h2>
        <p className="text-md mb-6 text-gray-700">
            These checks help us ensure the reliability of your health assessment.
        </p>

        {/* Section 1: Attention Check (Human/Bot Puzzle) */}
        <section className="mb-6 border border-gray-200 p-4 rounded-lg shadow-sm">
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
                className="p-2 border rounded w-32 focus:ring-blue-600"
                placeholder="Enter sum"
                required
            />
            <button type="submit" className="btn btn-primary">Submit</button>
            </form>
        </section>

        {/* Section 2: Simple Mental State Assessment */}
        <section className="mb-6 border border-gray-200 p-4 rounded-lg shadow-sm bg-gray-50">
            <h3 className="text-xl font-semibold mb-3">Mental State Check: How are you feeling right now?</h3>
            <p className="mb-4 text-gray-700">Select the mood that best describes your current mental condition:</p>
            <div className="flex flex-wrap gap-4">
            {['Calm', 'Stressed', 'Anxious', 'Energetic', 'Fatigued', 'Neutral'].map((mood) => (
                <button
                key={mood}
                onClick={() => handleMoodSelect(mood)}
                className={`px-4 py-2 rounded-full shadow transition-colors border ${
                    moodSelection === mood
                    ? 'bg-blue-600 text-white font-bold border-blue-600 shadow-md'
                    : 'bg-white hover:bg-blue-50 text-gray-800 border-gray-300'
                }`}
                >
                {mood}
                </button>
            ))}
            </div>
        </section>
    </div>
  );


  return (
    <div className="max-w-xl mx-auto bg-white p-8 rounded-lg shadow-xl animate-subtle-pop">
      <h2 className="text-3xl font-bold mb-6 text-center text-blue-600">Your Health Profile</h2>
      {loading ? <p className="text-center text-lg">Loading...</p> : (
        <form onSubmit={handleSubmit}>
          
          {/* Name Field */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Name</label>
            <input
              type="text"
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
            />
          </div>

          {/* Age Dropdown */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Age</label>
            <select
              name="age"
              value={profile.age}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150 bg-white"
              required
            >
              <option value="">Select Age</option>
              {ageOptions.map(age => (
                <option key={age} value={age}>{age}</option>
              ))}
            </select>
          </div>

          {/* Gender Dropdown */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Gender</label>
            <select
              name="gender"
              value={profile.gender}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150 bg-white"
              required
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Non-Binary">Non-Binary</option>
              <option value="Prefer Not to Say">Prefer Not to Say</option>
            </select>
          </div>

          {/* Weight Field */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Weight (kg)</label>
            <input
              type="number"
              name="weight"
              value={profile.weight}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
              placeholder="Enter your weight in kilograms"
              min="1"
              step="0.1"
            />
          </div>

          {/* Health Conditions */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Health Conditions</label>
            <textarea
              name="health_conditions"
              value={profile.health_conditions}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
              rows="3"
            />
          </div>

          {/* Birthmarks */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Birthmarks</label>
            <textarea
              name="birthmarks"
              value={profile.birthmarks}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
              rows="3"
            />
          </div>
          
          {/* Family Medication History */}
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Family Medication History</label>
            <textarea
              name="family_medication_history"
              value={profile.family_medication_history}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
              rows="3"
              placeholder="e.g., Medications taken by family members..."
            />
          </div>

          {/* Previous Medication History */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">Previous Medication History</label>
            <textarea
              name="previous_medication_history"
              value={profile.previous_medication_history}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150"
              rows="3"
              placeholder="e.g., Medications you have taken in the past year..."
            />
          </div>

          {/* AI Response Style */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">AI Response Style</label>
            <select 
              name="response_style" 
              value={profile.response_style || 'concise'} 
              onChange={handleChange} 
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-600 transition duration-150 bg-white"
            >
              <option value="concise">Concise</option>
              <option value="detailed">Detailed</option>
            </select>
          </div>

          <button type="submit" className="w-full btn btn-primary py-3 text-lg hover:shadow-md transition duration-200">
            Update Profile
          </button>
        </form>
      )}

      {message && <p className={`mt-4 text-center p-2 rounded ${
        message.includes('successfully') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}>{message}</p>}

      {/* Logout button */}
      <div className="mt-4">
        <button onClick={handleLogout} className="w-full btn btn-secondary py-3 text-lg hover:shadow-md transition duration-200">
          Logout
        </button>
      </div>
      
      {/* CONDITIONAL DISPLAY: Show puzzles */}
      {!loading && showPuzzles && <PuzzleSection />}

    </div>
  );
};

export default Profile;