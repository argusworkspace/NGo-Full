"use client";

import * as React from "react";
import { surveysApi } from "../api/surveys-api";
import type { Project } from "../types";

export function useProject(id: string) {
  const [project, setProject] = React.useState<Project | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    surveysApi
      .getProject(id)
      .then((res) => {
        if (!cancelled) setProject(res.data);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load this survey form.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { project, isLoading, error };
}
