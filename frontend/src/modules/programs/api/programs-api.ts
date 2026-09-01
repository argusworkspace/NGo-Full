import { apiClient } from "@/shared/lib/api-client";
import type { Program, CreateProgramRequest } from "../types";
import type { PaginatedResponse } from "@/shared/types/api";

export const programsApi = {
  list: (page = 1, size = 10) =>
    apiClient.get<PaginatedResponse<Program>>("/programs", { params: { page, size } }),

  get: (id: string) => apiClient.get<Program>(`/programs/${id}`),

  create: (data: CreateProgramRequest) => apiClient.post<Program>("/programs", data),

  update: (id: string, data: Partial<CreateProgramRequest>) =>
    apiClient.patch<Program>(`/programs/${id}`, data),

  delete: (id: string) => apiClient.delete(`/programs/${id}`),
};
