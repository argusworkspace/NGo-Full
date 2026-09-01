import { apiClient } from "@/shared/lib/api-client";
import type { LoginRequest, RegisterRequest, AuthTokens, User } from "../types";

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<AuthTokens>("/api/v1/auth/login", data),

  register: (data: RegisterRequest) =>
    apiClient.post<User>("/api/v1/auth/register", data),

  me: () => apiClient.get<User>("/api/v1/auth/me"),

  logout: () => apiClient.post("/api/v1/auth/logout"),
};
