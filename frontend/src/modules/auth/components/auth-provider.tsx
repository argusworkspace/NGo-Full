"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { toast } from "sonner";
import { authApi } from "../api/auth-api";
import type { Role, User, LoginRequest, RegisterRequest } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

const ROLE_HOME: Record<Role, Route> = {
  ADMIN: "/admin",
  VOLUNTEER: "/volunteer",
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  // Hydrate user from stored token on mount
  React.useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setIsLoading(false);
      return;
    }
    authApi
      .me()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("access_token"))
      .finally(() => setIsLoading(false));
  }, []);

  const login = React.useCallback(
    async (data: LoginRequest) => {
      const res = await authApi.login(data);
      localStorage.setItem("access_token", res.data.access_token);
      const meRes = await authApi.me();
      setUser(meRes.data);
      toast.success("Logged in successfully");
      router.push(ROLE_HOME[meRes.data.role]);
    },
    [router]
  );

  const register = React.useCallback(
    async (data: RegisterRequest) => {
      await authApi.register(data);
      toast.success("Account created! Please log in.");
      router.push("/login");
    },
    [router]
  );

  const logout = React.useCallback(() => {
    authApi.logout().catch(() => {});
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within an AuthProvider");
  return ctx;
}
