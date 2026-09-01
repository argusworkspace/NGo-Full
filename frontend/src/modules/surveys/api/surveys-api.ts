import { apiClient } from "@/shared/lib/api-client";
import type { CreateProjectRequest, Project, SubmitResponseRequest, SurveyResponse } from "../types";

export const surveysApi = {
  listProjects: () => apiClient.get<Project[]>("/api/v1/projects"),

  getProject: (id: string) => apiClient.get<Project>(`/api/v1/projects/${id}`),

  createProject: (data: CreateProjectRequest) => apiClient.post<Project>("/api/v1/projects", data),

  publishProject: (id: string) => apiClient.patch<Project>(`/api/v1/projects/${id}/publish`),

  submitResponse: (projectId: string, data: SubmitResponseRequest) =>
    apiClient.post<SurveyResponse>(`/api/v1/projects/${projectId}/responses`, data),
};
