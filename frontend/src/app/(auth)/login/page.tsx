import { LoginForm } from "@/modules/auth/components/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <LoginForm />
    </div>
  );
}
