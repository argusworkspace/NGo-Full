"use client";

import * as React from "react";
import { Pencil, Check, X } from "lucide-react";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { surveysApi } from "../api/surveys-api";
import type { Project } from "../types";
import { toast } from "sonner";

export function EventTitleEditor({
  project,
  onUpdated,
}: {
  project: Project;
  onUpdated: (project: Project) => void;
}) {
  const [editing, setEditing] = React.useState(false);
  const [name, setName] = React.useState(project.name);
  const [saving, setSaving] = React.useState(false);

  React.useEffect(() => {
    setName(project.name);
  }, [project.name]);

  const save = async () => {
    const trimmed = name.trim();
    if (!trimmed || trimmed === project.name) {
      setEditing(false);
      setName(project.name);
      return;
    }
    setSaving(true);
    try {
      const res = await surveysApi.updateProject(project.id, {
        name: trimmed,
        description: project.description ?? undefined,
        questions: project.questions,
      });
      onUpdated(res.data);
      toast.success("Event name updated");
      setEditing(false);
    } catch {
      toast.error("Could not update the event name");
    } finally {
      setSaving(false);
    }
  };

  if (!editing) {
    return (
      <button
        type="button"
        onClick={() => setEditing(true)}
        className="group flex items-center gap-2 text-left"
        title="Click to rename this event"
      >
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <Pencil className="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
      </button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        autoFocus
        value={name}
        disabled={saving}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") save();
          if (e.key === "Escape") {
            setEditing(false);
            setName(project.name);
          }
        }}
        className="max-w-sm text-lg font-semibold"
      />
      <Button size="icon" variant="ghost" onClick={save} disabled={saving}>
        <Check className="h-4 w-4" />
      </Button>
      <Button
        size="icon"
        variant="ghost"
        onClick={() => {
          setEditing(false);
          setName(project.name);
        }}
        disabled={saving}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
