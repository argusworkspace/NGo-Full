"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import type { Question, QuestionType } from "../types";

const TYPE_LABELS: Record<QuestionType, string> = {
  boolean: "Yes / No",
  rating: "Rating (1-5)",
  multiple_choice: "Multiple choice",
  single_choice: "Choose one option",
  text: "Text (writing)",
};

const CHOICE_TYPES: QuestionType[] = ["single_choice", "multiple_choice"];

interface QuestionBuilderProps {
  questions: Question[];
  onChange: (questions: Question[]) => void;
}

export function QuestionBuilder({ questions, onChange }: QuestionBuilderProps) {
  const addQuestion = () => {
    onChange([
      ...questions,
      { id: crypto.randomUUID(), question: "", type: "text", required: false },
    ]);
  };

  const updateQuestion = (index: number, patch: Partial<Question>) => {
    const next = [...questions];
    const updated = { ...next[index], ...patch };
    if (patch.type && !CHOICE_TYPES.includes(patch.type)) {
      updated.options = undefined;
    } else if (patch.type && CHOICE_TYPES.includes(patch.type) && !updated.options) {
      updated.options = [
        { id: crypto.randomUUID(), label: "" },
        { id: crypto.randomUUID(), label: "" },
      ];
    }
    next[index] = updated;
    onChange(next);
  };

  const removeQuestion = (index: number) => {
    onChange(questions.filter((_, i) => i !== index));
  };

  const updateOption = (qIndex: number, oIndex: number, label: string) => {
    const next = [...questions];
    const options = [...(next[qIndex].options ?? [])];
    options[oIndex] = { ...options[oIndex], label };
    next[qIndex] = { ...next[qIndex], options };
    onChange(next);
  };

  const addOption = (qIndex: number) => {
    const next = [...questions];
    next[qIndex] = {
      ...next[qIndex],
      options: [...(next[qIndex].options ?? []), { id: crypto.randomUUID(), label: "" }],
    };
    onChange(next);
  };

  const removeOption = (qIndex: number, oIndex: number) => {
    const next = [...questions];
    next[qIndex] = {
      ...next[qIndex],
      options: (next[qIndex].options ?? []).filter((_, i) => i !== oIndex),
    };
    onChange(next);
  };

  return (
    <div className="space-y-4">
      {questions.map((q, index) => (
        <div key={q.id} className="space-y-3 rounded-md border border-input p-4">
          <div className="flex items-start gap-2">
            <div className="flex-1 space-y-2">
              <Label htmlFor={`question-${q.id}`}>Question {index + 1}</Label>
              <Input
                id={`question-${q.id}`}
                value={q.question}
                onChange={(e) => updateQuestion(index, { question: e.target.value })}
                placeholder="Type your question"
              />
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="mt-6"
              onClick={() => removeQuestion(index)}
              aria-label="Remove question"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="space-y-1">
              <Label htmlFor={`type-${q.id}`}>Answer type</Label>
              <select
                id={`type-${q.id}`}
                value={q.type}
                onChange={(e) => updateQuestion(index, { type: e.target.value as QuestionType })}
                className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {Object.entries(TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={q.required}
                onChange={(e) => updateQuestion(index, { required: e.target.checked })}
              />
              Required
            </label>
          </div>

          {CHOICE_TYPES.includes(q.type) && (
            <div className="space-y-2 pl-4">
              <Label>Options</Label>
              {(q.options ?? []).map((opt, oIndex) => (
                <div key={opt.id} className="flex items-center gap-2">
                  <Input
                    value={opt.label}
                    onChange={(e) => updateOption(index, oIndex, e.target.value)}
                    placeholder={`Option ${oIndex + 1}`}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeOption(index, oIndex)}
                    disabled={(q.options ?? []).length <= 1}
                    aria-label="Remove option"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => addOption(index)}>
                <Plus className="mr-1 h-4 w-4" /> Add option
              </Button>
            </div>
          )}
        </div>
      ))}

      <Button type="button" variant="outline" onClick={addQuestion}>
        <Plus className="mr-2 h-4 w-4" /> Add question
      </Button>
    </div>
  );
}
