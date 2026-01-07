export type SectionKey = "issues" | "major" | "near" | "root";

export interface ApiRcaItem {
  deviation_id: string | undefined;
  problem_category: string;
  problem_category_validated: string;
  major_root_cause_category: string;
  major_root_cause_category_validated: string;
  near_root_cause: string;
  near_root_cause_category: string;
  root_cause: string;
  root_cause_category: string;
}

export interface RootCauseAnalysisProps {
  rcaData: ApiRcaItem[];
  onSubmitSuccess?: () => void;
}

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
    createdFrom?: "seed" | "add" | "new";
    createdAt?: string;
  };
}
type Factor = { factor_name: string; ProblemCategories: { name?: string }[] };
type DetailsItem = {
  NearRootCauses: string;
  rootcauses?: { name?: string }[];
};

type MajorRootCauseCategory = {
  description: string;
  properties?: { details?: DetailsItem[] };
};

export type DropdownData = {
  Factors: Factor[];
  MajorRootCauseCategories: MajorRootCauseCategory[];
};
