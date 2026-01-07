export interface SectionData {
  id: string;
  label: string;
  content: string;
}

export interface SuggestionData {
  sectionId: string;
  text: string;
  score: number;
}

/** Simulates fetching sections & their initial content */
export async function fetchSectionsMock(): Promise<SectionData[]> {
  await delay(400);

  return [
    {
      id: "description",
      label: "Description",
      content:
        "On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. ",
    },
    {
      id: "steps",
      label: "Immediate steps taken",
      content:
        "Cleaning representatives were notified and this record was raised. It was discovered upon investigation that there is a discrepancy in the approval requirements for analytical runs...",
    },
    {
      id: "summary",
      label: "Investigation Summary",
      content:
        "It was discovered during the investigation that there is a discrepancy in the approval requirements for analytical runs in procedures KIN-OVR-42071 and KIN-OVR-41656...",
    },
  ];
}

/** Simulates calling an API to get improvement suggestions based on current text */

export async function fetchImprovementSuggestionsMock(
  currentValues: Record<string, string>
): Promise<SuggestionData[]> {
  await delay(600);

  const mk = (
    sectionId: string,
    text: string,
    score: number
  ): SuggestionData => ({
    sectionId,
    text,
    score,
  });

  return [
    mk(
      "description",
      "The description provides sufficient context but could read more smoothly with concise phrasing and consistent verb tenses. Simplifying long sentences will improve flow and comprehension. Strengthening transitions between ideas will make the section more cohesive. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure. On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by QA representative that Non routine Analytical Results verification do not have QA oversight as per procedure.",
      4 // → shows thumbs down
    ),
    mk(
      "steps",
      "This section effectively outlines the actions taken, demonstrating strong procedural awareness. To refine it, simplify lengthy sentences and ensure verbs remain consistent in tense throughout. This will help maintain clarity and strengthen the professional tone.",
      7 // → shows thumbs up
    ),
    mk(
      "summary",
      "Your investigation summary is detailed and connects the findings logically to the deviation. However, it could benefit from reducing repetition of earlier content and improving transitions between key points. Enhancing grammatical consistency will make it more polished and easy to follow.",
      9 // → shows thumbs up
    ),
  ];
}

/** Simulates generating an executive summary */
export async function fetchExecutiveSummaryMock(
  values: Record<string, string>
): Promise<string> {
  await delay(500);

  // A simple synthesized summary from provided values
  const desc = values["description"]?.slice(0, 280) ?? "";
  const steps = values["steps"]?.slice(0, 280) ?? "";
  const sum = values["summary"]?.slice(0, 280) ?? "";

  return [
    "Executive Summary",
    "",
    "Overview:",
    desc || "No description provided.",
    "",
    "Immediate Actions:",
    steps || "No immediate steps documented.",
    "",
    "Investigation Summary:",
    sum || "No investigation summary provided.",
    "",
    "Conclusion:",
    "Controls and approval steps require alignment to ensure consistent QA oversight and analytical review process integrity.",
  ].join("\n");
}

function delay(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}
