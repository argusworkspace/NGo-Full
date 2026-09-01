export type QuestionType = "text" | "boolean" | "rating" | "single_choice" | "multiple_choice";

export interface Option {
  id: string;
  label: string;
}

export interface Question {
  id: string;
  question: string;
  type: QuestionType;
  required: boolean;
  options?: Option[];
}

export type ProjectStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  questions: Question[];
  status: ProjectStatus;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  responseCount: number;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  questions: Question[];
}

export interface Answer {
  questionId: string;
  answer: unknown;
}

export interface SubmitResponseRequest {
  answers: Answer[];
}

export interface SurveyResponse {
  id: string;
  projectId: string;
  userId: string;
  answers: Answer[];
  submittedAt: string;
}
