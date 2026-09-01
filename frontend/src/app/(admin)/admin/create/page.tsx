"use client";

import { CreateProjectForm } from "@/modules/surveys";

export default function CreateProjectPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Create New Project</h1>
      <CreateProjectForm />
    </div>
  );
}
