import { apiClient } from "@/shared/lib/api-client";
import type { Donor, CreateDonorRequest } from "../types";
import type { PaginatedResponse } from "@/shared/types/api";

export const donorsApi = {
  list: (page = 1, size = 10) =>
    apiClient.get<PaginatedResponse<Donor>>("/donors", { params: { page, size } }),

  get: (id: string) => apiClient.get<Donor>(`/donors/${id}`),

  create: (data: CreateDonorRequest) => apiClient.post<Donor>("/donors", data),

  update: (id: string, data: Partial<CreateDonorRequest>) =>
    apiClient.patch<Donor>(`/donors/${id}`, data),

  delete: (id: string) => apiClient.delete(`/donors/${id}`),
};
