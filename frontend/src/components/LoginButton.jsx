const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function LoginButton() {
  return (
    <button
      className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition"
      onClick={() => (window.location.href = `${API}/auth/github/login`)}
    >
      Sign in with GitHub
    </button>
  );
}
