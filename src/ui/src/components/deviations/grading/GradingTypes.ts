export interface SectionDataRes {
  data: { label: string; content: string }[];
}

export interface SectionData {
  label: string;
  content: string;
}

export interface SuggestionData {
  section_label: string;
  improvement_suggestion: string;
  text: string;
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
