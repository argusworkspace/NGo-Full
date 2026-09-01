"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/shared/components/ui/button";
import { useAuthContext } from "./auth-provider";

export function SessionBar() {
  const { user, logout } = useAuthContext();
  const router = useRouter();

  if (!user) return null;

  return (
    <div className="flex items-center justify-between border-b px-6 py-4">
      <span className="text-sm text-muted-foreground">
        Signed in as{" "}
        <span className="font-medium text-foreground">{user.name}</span> (
        {user.role})
      </span>
      <Button
        variant="outline"
        size="sm"
        onClick={() => {
          logout();
          router.push("/login");
        }}
      >
        Log out
      </Button>
    </div>
  );
}
