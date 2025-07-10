import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [userId, setUserId] = useState(() => {
    // Load from localStorage if available
    const storedId = localStorage.getItem("userId");
    return storedId ? parseInt(storedId) : -1;
  });

  const login = (id) => {
    setUserId(id);
    localStorage.setItem("userId", id);
  };

  const logout = () => {
    setUserId(-1);
    localStorage.removeItem("userId");
  };

  return (
    <AuthContext.Provider value={{ userId, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);