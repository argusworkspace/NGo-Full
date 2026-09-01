"use client";

import { useParams } from "next/navigation";
import { useProject, ProjectFillForm } from "@/modules/surveys";

export default function VolunteerProjectPage() {
  const params = useParams<{ projectId: string }>();
  const { project, isLoading, error } = useProject(params.projectId);

  if (isLoading) return <p className="text-muted-foreground">Loading...</p>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (!project) return <p className="text-muted-foreground">Survey form not found.</p>;

  return <ProjectFillForm project={project} />;
}
