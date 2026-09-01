"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { surveysApi } from "../api/surveys-api";
import { QuestionBuilder } from "./question-builder";
import type { Question } from "../types";

function getErrorMessage(err: unknown, fallback: string): string {
  const message = (err as { response?: { data?: { message?: string } } })?.response?.data
    ?.message;
  return typeof message === "string" ? message : fallback;
}

export function CreateProjectForm() {
  const router = useRouter();
  const [step, setStep] = React.useState<1 | 2>(1);
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [questions, setQuestions] = React.useState<Question[]>([]);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const goToStep2 = () => {
    if (!name.trim()) {
      toast.error("Project name is required");
      return;
    }
    setStep(2);
  };

  const handleCreate = async () => {
    if (!name.trim()) {
      toast.error("Survey title is required");
      return;
    }
    if (questions.length === 0) {
      toast.error("Add at least one question");
      return;
    }
    for (const q of questions) {
      if (!q.question.trim()) {
        toast.error("Every question needs text");
        return;
      }
      if (q.type === "single_choice" || q.type === "multiple_choice") {
        const labels = (q.options ?? []).map((o) => o.label.trim()).filter(Boolean);
        if (labels.length === 0) {
          toast.error(`"${q.question}" needs at least one option`);
          return;
        }
      }
    }

    setIsSubmitting(true);
    try {
      const created = await surveysApi.createProject({
        name,
        description: description || undefined,
        questions: questions.map((q) => ({
          ...q,
          options: q.options?.filter((o) => o.label.trim()),
        })),
      });
      await surveysApi.publishProject(created.data.id);
      toast.success("Survey form created and published");
      router.push("/admin");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not create the survey form"));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (step === 1) {
    return (
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Create new project</CardTitle>
          <CardDescription>Start with a name and description.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="project-name">Project name</Label>
            <Input id="project-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="project-description">Project description</Label>
            <Textarea
              id="project-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <Button type="button" onClick={goToStep2}>
            Create Survey Form
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Build the survey form</CardTitle>
        <CardDescription>Add a title and as many questions as you need.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="survey-title">Title</Label>
          <Input id="survey-title" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <QuestionBuilder questions={questions} onChange={setQuestions} />
        <div className="flex gap-2">
          <Button type="button" variant="outline" onClick={() => setStep(1)}>
            Back
          </Button>
          <Button type="button" onClick={handleCreate} disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create Survey Form"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
