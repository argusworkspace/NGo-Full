"use client";

import * as React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { RefreshCw, Sparkles, Users } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { EventTitleEditor } from "./event-title-editor";
import { useDashboard } from "../hooks/use-dashboard";
import type { Project, QuestionStat } from "../types";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#db2777"];

function optionLabel(project: Project, questionId: string, optionId: string): string {
  const question = project.questions.find((q) => q.id === questionId);
  return question?.options?.find((o) => o.id === optionId)?.label ?? optionId;
}

function StatTile({ label, value, hint }: { label: string; value: React.ReactNode; hint?: string }) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 text-3xl font-bold">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

function NumericQuestionCard({ stat }: { stat: QuestionStat }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{stat.question}</CardTitle>
        <CardDescription>{stat.responseCount} responses</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-3 gap-3">
        <StatTile label="Average" value={stat.average ?? "—"} />
        <StatTile label="Min" value={stat.min ?? "—"} />
        <StatTile label="Max" value={stat.max ?? "—"} />
      </CardContent>
    </Card>
  );
}

function BooleanQuestionCard({ stat }: { stat: QuestionStat }) {
  const data = [
    { name: "Yes", value: stat.trueCount ?? 0 },
    { name: "No", value: stat.falseCount ?? 0 },
  ];
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{stat.question}</CardTitle>
        <CardDescription>{stat.responseCount} responses</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" outerRadius={70} label>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function ChoiceQuestionCard({ stat, project }: { stat: QuestionStat; project: Project }) {
  const data = Object.entries(stat.optionCounts ?? {}).map(([id, count]) => ({
    name: optionLabel(project, stat.questionId, id),
    count,
  }));
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{stat.question}</CardTitle>
        <CardDescription>{stat.responseCount} responses</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function TextQuestionCard({ stat }: { stat: QuestionStat }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{stat.question}</CardTitle>
        <CardDescription>{stat.responseCount} responses</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {stat.summary && (
          <div className="flex gap-2 rounded-lg border bg-muted/30 p-3">
            <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <div>
              <p className="text-sm">{stat.summary}</p>
              <p className="mt-1 text-[11px] uppercase tracking-wide text-muted-foreground">
                {stat.summarySource === "ai" ? "AI-generated summary" : "Auto summary"}
              </p>
            </div>
          </div>
        )}
        {stat.sampleAnswers && stat.sampleAnswers.length > 0 && (
          <ul className="space-y-1.5 text-sm text-muted-foreground">
            {stat.sampleAnswers.map((a, i) => (
              <li key={i} className="border-l-2 pl-2 italic">
                “{a}”
              </li>
            ))}
          </ul>
        )}
        {!stat.responseCount && <p className="text-sm text-muted-foreground">No answers yet.</p>}
      </CardContent>
    </Card>
  );
}

export function ImpactDashboard({
  project,
  onProjectUpdated,
}: {
  project: Project;
  onProjectUpdated: (project: Project) => void;
}) {
  const { dashboard, isLoading, error, refresh } = useDashboard(project.id);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <EventTitleEditor project={project} onUpdated={onProjectUpdated} />
          {project.description && (
            <p className="mt-1 text-sm text-muted-foreground">{project.description}</p>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={() => refresh()}>
          <RefreshCw className="mr-2 h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>

      {isLoading && !dashboard ? (
        <p className="text-muted-foreground">Loading impact data...</p>
      ) : error ? (
        <p className="text-destructive">{error}</p>
      ) : dashboard ? (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatTile
              label="Total responses"
              value={
                <span className="flex items-center gap-2">
                  <Users className="h-6 w-6 text-primary" />
                  {dashboard.totalResponses.toLocaleString()}
                </span>
              }
            />
            <StatTile label="Status" value={dashboard.status} />
            <StatTile
              label="Last updated"
              value={new Date(dashboard.generatedAt).toLocaleTimeString()}
              hint="Auto-refreshes every 15s"
            />
          </div>

          {dashboard.questions.length === 0 ? (
            <p className="text-muted-foreground">This event has no questions yet.</p>
          ) : dashboard.totalResponses === 0 ? (
            <p className="text-muted-foreground">
              No responses yet. Once volunteers submit this form, the impact breakdown appears here.
            </p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {dashboard.questions.map((stat) => {
                if (stat.type === "number" || stat.type === "rating") {
                  return <NumericQuestionCard key={stat.questionId} stat={stat} />;
                }
                if (stat.type === "boolean") {
                  return <BooleanQuestionCard key={stat.questionId} stat={stat} />;
                }
                if (stat.type === "single_choice" || stat.type === "multiple_choice") {
                  return <ChoiceQuestionCard key={stat.questionId} stat={stat} project={project} />;
                }
                return <TextQuestionCard key={stat.questionId} stat={stat} />;
              })}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
