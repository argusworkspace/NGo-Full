"use client";

import Link from "next/link";
import { Button } from "@/shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { useProjects } from "@/modules/surveys";

export default function AdminDashboardPage() {
  const { projects, isLoading, error } = useProjects();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Projects</h1>
        <Button asChild>
          <Link href="/admin/create">Create New Project</Link>
        </Button>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : error ? (
        <p className="text-destructive">{error}</p>
      ) : projects.length === 0 ? (
        <p className="text-muted-foreground">
          No projects yet. Create one to get started.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {projects.map((project) => (
            <Card key={project.id}>
              <CardHeader>
                <CardTitle>{project.name}</CardTitle>
                {project.description && (
                  <CardDescription>{project.description}</CardDescription>
                )}
              </CardHeader>
              <CardContent className="space-y-1 text-sm text-muted-foreground">
                <p>Status: {project.status}</p>
                <p>{project.questions.length} questions</p>
              </CardContent>
              <CardFooter>
                <span className="text-xs text-muted-foreground">
                  {project.responseCount} response{project.responseCount === 1 ? "" : "s"}
                </span>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
