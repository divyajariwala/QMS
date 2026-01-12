export interface SectionDataRes {
  data: { label: string; content: string }[];
}

export interface SectionData {
  label: string;
  content: string;
}

export interface SuggestionData {
  sectionLabel?: string;
  text: string;
  score: number;
}

export interface ExecutiveSummaryItem {
  label: string;
  content: string;
}

export async function fetchImprovementSuggestionsMock(
  currentValues: string[]
): Promise<SuggestionData[]> {
  await delay(600);

  const mk = (
    text: string,
    score: number,
    sectionLabel?: string
  ): SuggestionData => ({
    text,
    score,
    sectionLabel,
  });

  return [
    mk(
      "Use a concise, action-oriented title that clearly states the deviation and the affected process/system. Consider including the system name and the specific gap (e.g., 'QA Verification Gap for Non-Routine Analytical Results in HP ALM').",
      7,
      "Title"
    ),
    mk(
      "The description provides sufficient context but would read more smoothly with concise phrasing and consistent verb tenses. Consider splitting the long sentence and clarifying the specific verification step lacking QA oversight.",
      5,
      "Description"
    ),
    mk(
      "This section effectively outlines the actions taken. To refine, present the immediate steps in bullet points and maintain consistent past tense to improve scanability and professional tone.",
      7,
      "Immediate Steps Taken"
    ),
    mk(
      "Strengthen the risk rationale: explicitly state the potential impact pathways (e.g., data integrity, decision-making on cleaning validation) and reference risk ratings (severity, occurrence, detection) if available.",
      8,
      "Quality Risk Evaluation"
    ),
    mk(
      "Your investigation details are logical. Consider adding a timeline of events, roles involved, and objective evidence (procedure versions, audit trail references) to increase traceability and completeness.",
      9,
      "Investigation Details"
    ),
    mk(
      "The CAPA plan is clear. Improve by adding owners, due dates, measurable outcomes, and linking each action to a root cause. Include verification/validation steps for the ALM workflow change.",
      8,
      "CAPA Plan"
    ),
    mk(
      "Recurrence check criteria are reasonable. Specify the sample size or scope (e.g., all non-routine runs in 12 months), acceptance criteria, and how exceptions will be handled.",
      7,
      "Recurrence Check Details"
    ),
    mk(
      "Effectiveness criteria are appropriate. Add data sources, audit schedule, and define what constitutes 'zero recurrence' (e.g., no deviations linked to the same root cause). Include a fallback plan if effectiveness is not met.",
      8,
      "Effectiveness Check Plan"
    ),
  ];
}

export async function fetchExecutiveSummaryMock(
  values: string[]
): Promise<ExecutiveSummaryItem[]> {
  await delay(500);

  const title = values[0] ?? "";
  const desc = values[1] ?? "";
  const steps = values[2] ?? "";
  const risk = values[3] ?? "";
  const inv = values[4] ?? "";
  const capa = values[5] ?? "";
  const recur = values[6] ?? "";
  const eff = values[7] ?? "";

  return [
    {
      label: "Title",
      content: title || "No title provided.",
    },
    {
      label: "Overview",
      content: desc || "No description provided.",
    },
    {
      label: "Immediate Actions",
      content: steps || "No immediate steps documented.",
    },
    {
      label: "Quality Risk Evaluation",
      content: risk || "No quality risk evaluation provided.",
    },
    {
      label: "Investigation Summary",
      content: inv || "No investigation details provided.",
    },
    {
      label: "CAPA Plan",
      content: capa || "No CAPA plan provided.",
    },
    {
      label: "Recurrence Check",
      content: recur || "No recurrence check details provided.",
    },
    {
      label: "Effectiveness Check",
      content: eff || "No effectiveness check plan provided.",
    },
  ];
}

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}
