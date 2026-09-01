"use client";

import { useAuthContext } from "../components/auth-provider";

// Thin convenience re-export so components can call useAuth() without
// importing from the provider path directly.
export const useAuth = useAuthContext;
