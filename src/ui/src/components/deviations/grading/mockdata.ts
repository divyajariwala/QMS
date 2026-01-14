export interface SectionDataRes {
  data: { label: string; content: string }[];
}

export interface SectionData {
  label: string;
  content: string;
}

export interface SuggestionData {
  sectionLabel?: string;
  improvement_suggestion: string;
  score: number;
}

export interface ExecutiveSummaryItem {
  label: string;
  content: string;
}

export type GradingSuggestionsPayload =
  | { deviation_id: string | undefined } // Start Grading
  | { deviation_id: string | undefined; previous_result: SectionData[] }; // Regenerate

export type SubmitGradingPayload = {
  deviation_id: string | undefined;
  sections: { label: string; content: string; isEdited: boolean }[];
};

export async function fetchImprovementSuggestionsMock(
  payload: GradingSuggestionsPayload
): Promise<SuggestionData[]> {
  await delay(600);

  const mk = (
    improvement_suggestion: string,
    score: number,
    sectionLabel?: string
  ): SuggestionData => ({
    improvement_suggestion,
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

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}
