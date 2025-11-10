import React, { useState } from 'react';
// We're assuming React is available.
// We're also assuming Tailwind CSS is available in the environment
// this file is run in (e.g., via a CDN or a build step).

// ---
// 1. 📦 Sub-Components (to keep our App component clean)
// ---
// (These components are unchanged)

/**
 * A loading spinner component.
 */
const LoadingSpinner = () => (
  <div className="flex justify-center items-center p-8">
    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

/**
 * An error message component.
 */
const ErrorMessage = ({ message }) => (
  <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded-lg shadow-lg" role="alert">
    <strong className="font-bold">Error: </strong>
    <span className="block sm:inline whitespace-pre-wrap">{message}</span>
  </div>
);

/**
 * A single card to display a matched issue.
 */
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

// ---
// 2. 🚀 Main Application Component
// ---

/**
 * The main application component.
 */
export default function App() {
  // --- State Management ---
  // (Unchanged)
  const [profile, setProfile] = useState("I am a new Python developer. I have used pandas and scikit-learn.");
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // --- API Call Logic ---
  
  /**
   * Handles the form submission when the user clicks "Find Matches".
   */
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMatches([]);
    
    const API_URL = "http://127.0.0.1:8000/matches";

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_profile: profile 
        })
      });

      // ---
      // ⚠️ THIS IS THE SECTION THAT HANDLES BACKEND ERRORS
      // ---
      if (!response.ok) {
        // We got an error (4xx or 5xx). Let's parse the JSON body.
        const errorData = await response.json();
        
        // This is the most likely case: a FastAPI HTTPException
        if (errorData.detail) {
          // Check if 'detail' is a string or an object (like a validation error)
          if (typeof errorData.detail === 'string') {
            throw new Error(errorData.detail);
          } else {
            // It's a validation error (a list of objects)
            throw new Error(JSON.stringify(errorData.detail, null, 2));
          }
        }
        
        // A generic HTTP error
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // 5. Success! Save the data.
      const data = await response.json();
      setMatches(data.matches);
      
    } catch (err) {
      // ---
      // ⚠️ THIS IS THE UPDATED CATCH BLOCK (THE FIX)
      // ---
      console.error("Fetch error:", err);
      
      let errorMessage = "An unknown error occurred.";
      
      if (err instanceof Error) {
        // This is a standard Error object (e.g., from `throw new Error()`)
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        // This is a string being thrown (unlikely, but possible)
        errorMessage = err;
      } else {
        // Last resort, stringify the error
        try {
          errorMessage = JSON.stringify(err);
        } catch (e) {
          errorMessage = "Could not serialize the error object.";
        }
      }
      
      // Now, we set the error to a guaranteed string
      setError(errorMessage);
      
    } finally {
      // 7. Always stop loading
      setLoading(false);
    }
  };

  // --- Rendering (JSX) ---
  // (Unchanged)
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white mb-3">
            FirstPR.ai
          </h1>
          <p className="text-lg sm:text-xl text-gray-400">
            Tell us your skills. We'll find your first open-source contribution.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="mb-10">
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
    </div>
  );
}