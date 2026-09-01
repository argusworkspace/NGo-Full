import { apiClient } from "@/shared/lib/api-client";
import type { Volunteer, CreateVolunteerRequest } from "../types";
import type { PaginatedResponse } from "@/shared/types/api";

export const volunteersApi = {
  list: (page = 1, size = 10) =>
    apiClient.get<PaginatedResponse<Volunteer>>("/volunteers", { params: { page, size } }),

  get: (id: string) => apiClient.get<Volunteer>(`/volunteers/${id}`),

  create: (data: CreateVolunteerRequest) => apiClient.post<Volunteer>("/volunteers", data),

  update: (id: string, data: Partial<CreateVolunteerRequest>) =>
    apiClient.patch<Volunteer>(`/volunteers/${id}`, data),

  delete: (id: string) => apiClient.delete(`/volunteers/${id}`),
};
