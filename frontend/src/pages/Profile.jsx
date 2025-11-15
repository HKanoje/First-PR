import { useAuth } from "../context/AuthContext.jsx";
import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Profile() {
  const { user, refresh } = useAuth();
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setBio(user.bio || "");
    }
  }, [user]);

  if (!user) {
    return <div className="p-4 text-center text-gray-500">Please sign in first.</div>;
  }

  const save = async () => {
    await fetch(`${API}/auth/me`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name, bio }),
    });
    refresh();
  };

  const logout = async () => {
    await fetch(`${API}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    window.location.href = "/";
  };

  return (
    <div className="max-w-lg mx-auto p-4 space-y-4">
      <div className="text-center">
        <img
          src={user.avatar_url}
          alt={user.username}
          className="w-20 h-20 rounded-full mx-auto mb-3"
        />
        <div className="text-xl font-semibold">@{user.username}</div>
        <div className="text-sm text-gray-500">{user.email}</div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">Name</label>
        <input
          className="border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Your full name"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">Bio</label>
        <textarea
          className="border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="4"
          value={bio}
          onChange={e => setBio(e.target.value)}
          placeholder="Tell us about yourself..."
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={save}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded transition"
        >
          Save Changes
        </button>
        <button
          onClick={logout}
          className="flex-1 bg-gray-700 hover:bg-gray-800 text-white px-3 py-2 rounded transition"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
