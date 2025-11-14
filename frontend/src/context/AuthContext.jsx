import { createContext, useContext, useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const AuthCtx = createContext({ user: null, refresh: () => {} });

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  
  const refresh = () => {
    fetch(`${API}/auth/me`, { credentials: "include" })
      .then(r => (r.ok ? r.json() : null))
      .then(setUser)
      .catch(() => setUser(null));
  };
  
  useEffect(refresh, []);
  
  return (
    <AuthCtx.Provider value={{ user, refresh }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
