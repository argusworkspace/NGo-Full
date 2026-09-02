"use client";

import * as React from "react";
import { surveysApi } from "../api/surveys-api";
import type { DashboardData } from "../types";

const POLL_INTERVAL_MS = 15000;

export function useDashboard(projectId: string) {
  const [dashboard, setDashboard] = React.useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const refresh = React.useCallback(
    async (silent = false) => {
      if (!silent) setIsLoading(true);
      setError(null);
      try {
        const res = await surveysApi.getDashboard(projectId);
        setDashboard(res.data);
      } catch {
        setError("Could not load the impact dashboard.");
      } finally {
        if (!silent) setIsLoading(false);
      }
    },
    [projectId]
  );

  React.useEffect(() => {
    refresh();
    const interval = setInterval(() => refresh(true), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [refresh]);

  return { dashboard, isLoading, error, refresh };
}
