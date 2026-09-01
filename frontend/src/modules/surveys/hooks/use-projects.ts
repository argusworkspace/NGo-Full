"use client";

import * as React from "react";
import { surveysApi } from "../api/surveys-api";
import type { Project } from "../types";

export function useProjects() {
  const [projects, setProjects] = React.useState<Project[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const refresh = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await surveysApi.listProjects();
      setProjects(res.data);
    } catch {
      setError("Could not load projects.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  return { projects, isLoading, error, refresh };
}
