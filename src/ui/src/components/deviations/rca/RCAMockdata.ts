export type SectionKey = "issues" | "major" | "near" | "root";

export interface RcaSection {
  key: SectionKey;
  title: string; 
  value: string;
  explanation: string; 
}

export interface RcaRecord {
  id: string;
  name: string;
  sections: RcaSection[];
  meta?: {
    createdFrom?: "seed" | "add";
    createdAt?: string;
  };
}

const explanationText = `The deviation primarily stems from a company personnel issue. An analyst failed to follow the correct procedure as outlined in STM QC 0800 General Laboratory Practices. Duplicate results were generated for the osmolality assay without supervisor approval and without proper justification to invalidate the original results. This violates the procedure which states that no duplicate testing shall be done without justification and supervisor approval.`;

export const initialRcas: RcaRecord[] = [
  {
    id: "rca-1",
    name: "RCA 1",
    sections: [
      {
        key: "issues",
        title: "Causal factor",
        value: "Company personnel issue",
        explanation: explanationText,
      },
      {
        key: "major",
        title: "Major root cause category",
        value: "Process/manufacturing equipment issue",
        explanation: explanationText,
      },
      {
        key: "near",
        title: "Near root cause",
        value: "Company personnel issue",
        explanation: explanationText,
      },
      {
        key: "root",
        title: "Root cause",
        value: "Process/manufacturing equipment issue",
        explanation: explanationText,
      },
    ],
    meta: { createdFrom: "seed", createdAt: new Date().toISOString() },
  },
  {
    id: "rca-2",
    name: "RCA 2",
    sections: [
      {
        key: "issues",
        title: "Causal factor",
        value: "Training issue",
        explanation: explanationText,
      },
      {
        key: "major",
        title: "Major root cause category",
        value: "Procedure Issue",
        explanation: explanationText,
      },
      {
        key: "near",
        title: "Near root cause",
        value: "Process/manufacturing equipment issue",
        explanation: explanationText,
      },
      {
        key: "root",
        title: "Root cause",
        value: "Documentation issue",
        explanation: explanationText,
      },
    ],
    meta: { createdFrom: "seed", createdAt: new Date().toISOString() },
  },
];
