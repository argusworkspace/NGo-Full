"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";

// Old deep-link shape (/admin/dashboard/<id>) — redirect into the tabbed
// dashboard hub which lets admins switch between events from one place.
export default function LegacyAdminEventDashboardRedirect() {
  const params = useParams<{ projectId: string }>();
  const router = useRouter();

  React.useEffect(() => {
    router.replace(`/admin/dashboard?project=${params.projectId}`);
  }, [params.projectId, router]);

  return <p className="text-muted-foreground">Redirecting...</p>;
}
