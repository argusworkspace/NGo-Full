"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import { Textarea } from "@/shared/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { surveysApi } from "../api/surveys-api";
import type { Project } from "../types";

function getErrorMessage(err: unknown, fallback: string): string {
  const message = (err as { response?: { data?: { message?: string } } })?.response?.data
    ?.message;
  return typeof message === "string" ? message : fallback;
}

function isEmptyAnswer(value: unknown): boolean {
  return value === undefined || value === "" || (Array.isArray(value) && value.length === 0);
}

export function ProjectFillForm({ project }: { project: Project }) {
  const router = useRouter();
  const [answers, setAnswers] = React.useState<Record<string, unknown>>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const setAnswer = (questionId: string, value: unknown) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const toggleMultiple = (questionId: string, optionId: string) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[questionId]) ? (prev[questionId] as string[]) : [];
      const next = current.includes(optionId)
        ? current.filter((id) => id !== optionId)
        : [...current, optionId];
      return { ...prev, [questionId]: next };
    });
  };

  const handleSubmit = async () => {
    for (const q of project.questions) {
      if (q.required && isEmptyAnswer(answers[q.id])) {
        toast.error(`"${q.question}" is required`);
        return;
      }
    }

    setIsSubmitting(true);
    try {
      await surveysApi.submitResponse(project.id, {
        answers: Object.entries(answers)
          .filter(([, value]) => !isEmptyAnswer(value))
          .map(([questionId, answer]) => ({ questionId, answer })),
      });
      toast.success("Response submitted, thank you!");
      router.push("/volunteer");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not submit your response"));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
        {project.description && <CardDescription>{project.description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-6">
        {project.questions.map((q) => (
          <div key={q.id} className="space-y-2">
            <p className="text-sm font-medium">
              {q.question} {q.required && <span className="text-destructive">*</span>}
            </p>

            {q.type === "text" && (
              <Textarea
                value={(answers[q.id] as string) ?? ""}
                onChange={(e) => setAnswer(q.id, e.target.value)}
              />
            )}

            {q.type === "boolean" && (
              <div className="flex gap-2">
                {[
                  { label: "Yes", value: true },
                  { label: "No", value: false },
                ].map((opt) => (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => setAnswer(q.id, opt.value)}
                    className={cn(
                      "rounded-md border px-4 py-2 text-sm",
                      answers[q.id] === opt.value
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-input bg-background hover:bg-accent"
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            )}

            {q.type === "rating" && (
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setAnswer(q.id, n)}
                    className={cn(
                      "h-10 w-10 rounded-md border text-sm",
                      answers[q.id] === n
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-input bg-background hover:bg-accent"
                    )}
                  >
                    {n}
                  </button>
                ))}
              </div>
            )}

            {q.type === "single_choice" && (
              <div className="space-y-2">
                {q.options?.map((opt) => (
                  <label key={opt.id} className="flex items-center gap-2 text-sm">
                    <input
                      type="radio"
                      name={q.id}
                      checked={answers[q.id] === opt.id}
                      onChange={() => setAnswer(q.id, opt.id)}
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            )}

            {q.type === "multiple_choice" && (
              <div className="space-y-2">
                {q.options?.map((opt) => (
                  <label key={opt.id} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={
                        Array.isArray(answers[q.id]) &&
                        (answers[q.id] as string[]).includes(opt.id)
                      }
                      onChange={() => toggleMultiple(q.id, opt.id)}
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            )}
          </div>
        ))}
      </CardContent>
      <CardFooter>
        <Button type="button" onClick={handleSubmit} disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Submitting..." : "Submit"}
        </Button>
      </CardFooter>
    </Card>
  );
}
