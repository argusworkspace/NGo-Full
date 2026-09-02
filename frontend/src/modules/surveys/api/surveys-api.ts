import { apiClient } from "@/shared/lib/api-client";
import type {
  CreateProjectRequest,
  DashboardData,
  Project,
  SubmitResponseRequest,
  SurveyResponse,
  UpdateProjectRequest,
} from "../types";

export const surveysApi = {
  listProjects: () => apiClient.get<Project[]>("/api/v1/projects"),

  getProject: (id: string) => apiClient.get<Project>(`/api/v1/projects/${id}`),

  createProject: (data: CreateProjectRequest) => apiClient.post<Project>("/api/v1/projects", data),

  updateProject: (id: string, data: UpdateProjectRequest) =>
    apiClient.put<Project>(`/api/v1/projects/${id}`, data),

  publishProject: (id: string) => apiClient.patch<Project>(`/api/v1/projects/${id}/publish`),

  submitResponse: (projectId: string, data: SubmitResponseRequest) =>
    apiClient.post<SurveyResponse>(`/api/v1/projects/${projectId}/responses`, data),

  getDashboard: (projectId: string) =>
    apiClient.get<DashboardData>(`/api/v1/projects/${projectId}/dashboard`),
};
