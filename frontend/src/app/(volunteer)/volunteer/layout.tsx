import { RoleGuard } from "@/modules/auth/components/role-guard";
import { SessionBar } from "@/modules/auth/components/session-bar";

export default function VolunteerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard allow={["VOLUNTEER"]}>
      <div className="min-h-screen">
        <SessionBar />
        <main className="mx-auto max-w-4xl p-6">{children}</main>
      </div>
    </RoleGuard>
  );
}
