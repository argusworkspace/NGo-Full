import { RoleGuard } from "@/modules/auth/components/role-guard";
import { SessionBar } from "@/modules/auth/components/session-bar";
import { AdminNav } from "./admin-nav";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard allow={["ADMIN"]}>
      <div className="min-h-screen">
        <SessionBar />
        <main className="mx-auto max-w-5xl p-6">
          <AdminNav />
          {children}
        </main>
      </div>
    </RoleGuard>
  );
}
