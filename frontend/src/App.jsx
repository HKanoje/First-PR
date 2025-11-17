import React, { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import LoginButton from './components/LoginButton';
import Profile from './pages/Profile';

// Sub-components from original App.jsx
const LoadingSpinner = () => (
  <div className="flex justify-center items-center p-8">
    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

const ErrorMessage = ({ message }) => (
  <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded-lg shadow-lg" role="alert">
    <strong className="font-bold">Error: </strong>
    <span className="block sm:inline whitespace-pre-wrap">{message}</span>
  </div>
);

const MatchCard = ({ match }) => {
  const formattedScore = (match.score * 100).toFixed(1);

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden transform transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl">
      <div className="p-5">
        <div className="flex justify-between items-start mb-2">
          <span className="text-sm font-semibold text-blue-400 uppercase tracking-wider">
            {match.repo_name}
          </span>
          <span className={`text-lg font-bold ${formattedScore > 50 ? 'text-green-400' : 'text-yellow-400'}`}>
            {formattedScore}%
            <span className="text-xs text-gray-400"> Match</span>
          </span>
        </div>
        
        <h3 className="text-lg font-bold text-white mb-3">
          {match.title}
        </h3>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {match.labels.map((label, index) => (
            <span 
              key={index} 
              className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs font-medium rounded-full"
            >
              {label}
            </span>
          ))}
        </div>
      </div>
      
      <div className="bg-gray-700/50 px-5 py-3">
        <a 
          href={match.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-400 font-semibold hover:text-blue-300 transition-colors duration-200"
        >
          View Issue on GitHub &rarr;
        </a>
      </div>
    </div>
  );
};

// Home page component
function Home() {
  const [profile, setProfile] = useState("I am a new Python developer. I have used pandas and scikit-learn.");
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMatches([]);

    try {
      const response = await fetch(`${API_URL}/matches`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_profile: profile 
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            throw new Error(errorData.detail);
          } else {
            throw new Error(JSON.stringify(errorData.detail, null, 2));
          }
        }
        
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setMatches(data.matches);
      
    } catch (err) {
      console.error("Fetch error:", err);
      
      let errorMessage = "An unknown error occurred.";
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else {
        try {
          errorMessage = JSON.stringify(err);
        } catch (e) {
          errorMessage = "Could not serialize the error object.";
        }
      }
      
      setError(errorMessage);
      
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white mb-3">
          FirstPR.ai
        </h1>
        <p className="text-lg sm:text-xl text-gray-400">
          Tell us your skills. We'll find your first open-source contribution.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-gray-800/50 p-6 rounded-lg">
        <label htmlFor="profile-input" className="block text-sm font-medium text-gray-300 mb-2">
          Describe your skills (e.g., "I know React and Node.js", "I'm good at writing documentation"):
        </label>
        <textarea
          id="profile-input"
          value={profile}
          onChange={(e) => setProfile(e.target.value)}
          className="w-full h-32 p-4 bg-gray-800 border-2 border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-inner"
          placeholder="I am a new Python developer. I have used pandas..."
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 px-6 py-3 bg-blue-600 text-white text-lg font-bold rounded-lg shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-all duration-200 disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {loading ? "Scanning for matches..." : "Find My First PR"}
        </button>
      </form>

      <section>
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} />}
        {matches.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {matches.map((match) => (
              <MatchCard key={match.url} match={match} />
            ))}
          </div>
        )}
        {!loading && !error && matches.length === 0 && profile === "" && (
          <div className="text-center text-gray-500">
            <p>Enter your skills above to get started!</p>
          </div>
        )}
      </section>
    </div>
  );
}

// Main App component with routing
export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <header className="max-w-4xl mx-auto p-4 flex justify-between items-center border-b border-gray-700">
        <Link to="/" className="text-2xl font-bold hover:text-blue-400 transition">
          First-PR
        </Link>
        <nav className="flex gap-4 items-center">
          {user ? (
            <>
              <img src={user.avatar_url} alt={user.username} className="w-8 h-8 rounded-full" />
              <Link to="/profile" className="hover:text-blue-400 transition underline">
                Profile
              </Link>
            </>
          ) : (
            <LoginButton />
          )}
        </nav>
      </header>

      <main className="max-w-4xl mx-auto p-4 sm:p-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  );
}