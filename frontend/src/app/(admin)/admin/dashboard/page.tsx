"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useProjects, useProject, ImpactDashboard } from "@/modules/surveys";
import type { Project } from "@/modules/surveys";

export default function AdminDashboardHubPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { projects, isLoading: projectsLoading, error: projectsError } = useProjects();

  const selectedId = searchParams.get("project") ?? "";

  // Default to the first project once the list loads, if none is selected yet.
  React.useEffect(() => {
    if (!selectedId && projects.length > 0) {
      router.replace(`/admin/dashboard?project=${projects[0].id}`);
    }
  }, [selectedId, projects, router]);

  const { project, isLoading: projectLoading, error: projectError } = useProject(selectedId);
  const [override, setOverride] = React.useState<Project | null>(null);
  const current = override?.id === selectedId ? override : project;

  const handleSwitch = (id: string) => {
    setOverride(null);
    router.replace(`/admin/dashboard?project=${id}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Impact Dashboard</h1>

        {!projectsLoading && projects.length > 0 && (
          <label className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Event:</span>
            <select
              value={selectedId}
              onChange={(e) => handleSwitch(e.target.value)}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {projectsLoading ? (
        <p className="text-muted-foreground">Loading projects...</p>
      ) : projectsError ? (
        <p className="text-destructive">{projectsError}</p>
      ) : projects.length === 0 ? (
        <p className="text-muted-foreground">
          No projects yet. Create one from the Projects tab to see its impact here.
        </p>
      ) : projectLoading && !current ? (
        <p className="text-muted-foreground">Loading impact data...</p>
      ) : projectError ? (
        <p className="text-destructive">{projectError}</p>
      ) : current ? (
        <ImpactDashboard project={current} onProjectUpdated={setOverride} />
      ) : null}
    </div>
  );
}
