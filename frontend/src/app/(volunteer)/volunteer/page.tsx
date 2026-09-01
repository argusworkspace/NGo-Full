"use client";

import Link from "next/link";
import { Button } from "@/shared/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { useProjects } from "@/modules/surveys";

export default function VolunteerDashboardPage() {
  const { projects, isLoading, error } = useProjects();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Volunteer Dashboard</h1>
        <p className="text-muted-foreground">
          Select a project to fill out its survey form.
        </p>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : error ? (
        <p className="text-destructive">{error}</p>
      ) : projects.length === 0 ? (
        <p className="text-muted-foreground">No survey forms are available yet.</p>
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
              <CardFooter className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  {project.responseCount} response{project.responseCount === 1 ? "" : "s"}
                </span>
                <Button asChild size="sm">
                  <Link href={`/volunteer/${project.id}`}>Fill Form</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
