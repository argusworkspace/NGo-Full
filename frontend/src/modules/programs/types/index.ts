export interface Program {
  id: string;
  title: string;
  description: string;
  status: "active" | "completed" | "draft";
  start_date: string;
  end_date?: string;
  budget: number;
  created_at: string;
}

export interface CreateProgramRequest {
  title: string;
  description: string;
  start_date: string;
  end_date?: string;
  budget: number;
}
