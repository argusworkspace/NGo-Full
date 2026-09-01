"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { useAuthContext } from "./auth-provider";
import type { Role } from "../types";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

type FormData = z.infer<typeof schema>;

const ROLE_CARDS: { role: Role; title: string; description: string }[] = [
  { role: "ADMIN", title: "Admin", description: "Manage projects and survey forms." },
  { role: "VOLUNTEER", title: "Volunteer", description: "Fill out survey forms." },
];

// Which card is selected only decides which form/copy is shown below (and
// whether the "create account" link appears, since there's no admin
// sign-up path) — the account's actual role always comes from the backend,
// and login succeeds purely based on the submitted credentials.
export function LoginForm() {
  const { login } = useAuthContext();
  const [selectedRole, setSelectedRole] = React.useState<Role | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      await login(data);
    } catch {
      toast.error("Invalid credentials");
    }
  };

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="grid grid-cols-2 gap-4">
        {ROLE_CARDS.map(({ role, title, description }) => (
          <button
            key={role}
            type="button"
            onClick={() => setSelectedRole(role)}
            className={cn(
              "rounded-lg border p-4 text-left transition-colors",
              selectedRole === role
                ? "border-primary bg-primary/5 ring-2 ring-primary"
                : "border-input bg-background hover:bg-accent"
            )}
          >
            <p className="font-semibold">{title}</p>
            <p className="text-xs text-muted-foreground">{description}</p>
          </button>
        ))}
      </div>

      {selectedRole && (
        <Card>
          <CardHeader>
            <CardTitle>Sign in as {selectedRole === "ADMIN" ? "Admin" : "Volunteer"}</CardTitle>
            <CardDescription>Enter your credentials to access the platform.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" {...register("email")} />
                {errors.email && <p className="text-destructive text-xs">{errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" {...register("password")} />
                {errors.password && <p className="text-destructive text-xs">{errors.password.message}</p>}
              </div>
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Signing in..." : "Sign in"}
              </Button>
              {selectedRole === "VOLUNTEER" && (
                <p className="text-center text-sm text-muted-foreground">
                  No account?{" "}
                  <Link href="/register" className="underline">Register</Link>
                </p>
              )}
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
