"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { useAuthContext } from "./auth-provider";
import type { Role } from "../types";

interface RoleGuardProps {
  allow: Role[];
  children: React.ReactNode;
}

const ROLE_HOME: Record<Role, Route> = {
  ADMIN: "/admin",
  VOLUNTEER: "/volunteer",
};

export function RoleGuard({ allow, children }: RoleGuardProps) {
  const { user, isLoading } = useAuthContext();
  const router = useRouter();

  React.useEffect(() => {
    if (isLoading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    if (!allow.includes(user.role)) {
      router.replace(ROLE_HOME[user.role]);
    }
  }, [isLoading, user, allow, router]);

  if (isLoading || !user || !allow.includes(user.role)) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Loading...
      </div>
    );
  }

  return <>{children}</>;
}
