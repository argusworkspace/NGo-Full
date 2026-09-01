export interface Volunteer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  skills: string[];
  status: "active" | "inactive";
  created_at: string;
}

export interface CreateVolunteerRequest {
  name: string;
  email: string;
  phone?: string;
  skills?: string[];
}
