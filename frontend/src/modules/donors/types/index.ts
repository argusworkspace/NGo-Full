export interface Donor {
  id: string;
  name: string;
  email: string;
  phone?: string;
  total_donated: number;
  created_at: string;
}

export interface CreateDonorRequest {
  name: string;
  email: string;
  phone?: string;
}
