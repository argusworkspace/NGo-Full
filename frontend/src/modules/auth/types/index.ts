export type Role = "ADMIN" | "VOLUNTEER";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  created_at: string;
}
