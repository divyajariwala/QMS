import { User } from "oidc-client-ts";

export interface SessionData {
  session_id: string;
  user_name: string;
}

export interface GetInitialDataResponse {
  complaint_id: string;
  drugname: string;
  complaint_narrative: string;
  session_id: string;
  user_name: string;
}

export interface InvokeApiPayload {
  time: string;
  narrative: string;
  drugname: string;
}

export interface CategoryInvokeResponse {
  response: {
    "MD5OfMessageBody": string;
    "MessageId": string;
    "ResponseMetadata": {
      "RequestId": string;
      "HTTPStatusCode": number;
      "HTTPHeaders": {
        "x-amzn-requestid": string;
        "date": string;
        "content-type": string;
        "content-length": string;
        "connection": string;
      },
      "RetryAttempts": number;
    };
  }
}

export interface FetchResultsResponseDatailItem {
  category: string;
  category_confidence_score: number;
  crl_value: string;
  level: number;
}

export interface FetchResultsResponse {
  results: {
    uuid: string;
    // priority: number;
    summary: string;
    details: FetchResultsResponseDatailItem[];
  };
  crl_values: string[];
  csc_values: string[];
}

export interface ComplaintDataset {
  title: string | null;
  title_new?: string;
  crlValue: number;
  category: string;
  category_new?: string;
  categoryValue: number;
  level: number | null;
  level_new?: number | string;
  unit_new?: number | string;
}

export interface ComplaintResultItem {
  category: string;
  crl: string | null;
  level: number | null;
  unit?: number;
}

export interface ComplaintResult {
  model?: ComplaintResultItem;
  user?: ComplaintResultItem;
}

export interface UIResultsParams {
  complaint_id: string;
  data: ComplaintResult[];
  priority?: number;
  modelPriority?: number;
}

export interface UIData {
  scList: string[];
  crlList: string[];
}

export interface Narrative {
  id: string;
  ingestedDate: string;
  processedDate?: string;
  description: string;
  types: string[];
  source: string;
}

export interface Filters {
  ingestedStart: Date | null;
  ingestedEnd: Date | null;
  processedStart: Date | null;
  processedEnd: Date | null;
  selectedSources: string[];
  selectedTypes: string[];
}

export interface UploadedDoc {
  name: string;
  size: number;
  type: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  accessToken?: string;
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
  getAccessToken: () => Promise<string | undefined>;
  isLoading: boolean;
};

export interface BreadcrumbItem {
  label: string | undefined;
  to?: string;
}

export interface CommonBreadcrumbsProps {
  items: BreadcrumbItem[];
  ariaLabel?: string;
}

export interface LegendItemProps {
  colorClass: "dotPending" | "dotProcessed" | "dotOverdue" | undefined;
  label: string;
  value: string | number | undefined;
}

export interface LegendData {
  colorClass?: "dotPending" | "dotProcessed" | "dotOverdue";
  label: string;
  value: string | number;
}

export interface StatusCardProps {
  iconSrc: string;
  iconAlt: string;
  title: string;
  cardValue?: string | number | undefined;
  legend?: LegendData[];
  page: string;
}

export interface ComplaintCategoryItem {
  id: string;
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
}
export interface ComplaintCategoryProps {
    complaintCategories: ComplaintCategoryItem[];
  setComplaintCategories: (updatedCategories: ComplaintCategoryItem[]) => void;
}

export interface ComplaintHeaderCardProps {
  complaintData: {
    status?: string | undefined;
    caseId?: string | undefined;
    overdueDays?: number | undefined;
    primaryReporter?: Record<string, any> | undefined;
    patientName?: string | undefined;
    physicianName?: string | undefined;
    drug?: string | undefined;
    lotNumber?: string | undefined;
    doseAmount?: string | undefined;
    expirationDate?: string | undefined;
    partNumber?: string | undefined;
    receipt_date: string | undefined;
  };
  onApproveAndSend: () => void;
  caseStatus: string | undefined;
  isApproved: boolean
}

export interface ComplaintInterHeaderCardProps {
  complaintData: {
    status?: string | undefined;
    caseId?: string | undefined;
    overdueDays?: number | undefined;
    primaryReporter?: Record<string, any> | undefined;
    patientName?: string | undefined;
    physicianName?: string | undefined;
    drug?: string | undefined;
    lotNumber?: string | undefined;
    doseAmount?: string | undefined;
    expirationDate?: string | undefined;
    partNumber?: string | undefined;
    receipt_date: string | undefined;
  };
  caseStatus: string | undefined;
  setOpenModifyDetails: (val: boolean) => void;
}

export interface ComplaintsDueDateChipProps {
  type: "Overdue" | "Today" | "Tomorrow" | "Due" | "" | undefined;
  label: string | undefined;
}

export interface DueDateChipProps {
  iconSrc: string;
  iconAlt: string;
  label: string | undefined;
  className?: string;
}

export interface InfoItemProps {
  label: string;
  iconSrc: string;
  iconAlt: string;
  value: string | React.ReactNode;
}

export interface InfoChipProps {
  iconSrc: string;
  iconAlt: string;
  label: string;
  className?: string;
}

export interface SecondaryInfoCardProps {
  infoItems: Array<InfoItemProps>;
  productComplaintIconSrc: string;
  adverseEventIconSrc: string;
  productComplaintsChipClassName?: string;
  adverseEventChipClassName?: string;
  caseType: string[]
}

export interface StatusTabItem {
  label: string;
  count: number | undefined;
}

export interface ComplaintProps {
  complaint: {
    case_id: string;
    criticality: string;
    report_type: string;
    receipt_date: string; // You might want to correct this to 'receipt_date' if it's a typo
    case_type: string[];
  },
  selected: string
}

export interface ButtonGroupProps {
  onSelect?: (selected: string) => void;
  selected?: string;
}

export interface DeviationProps {
  deviation: {
    "Recieved Date": string,
    "Processed Date": string,
    "Due Date": string,
    "rcaStatus": string,
    "gradingStatus": string,
    "status": string,
    "progress": number;
    "Case Number": string;
  };
}

export type Status = "completed" | "active" | "inactive";

export interface StatusStepProps {
  label: string;
  status: Status;
}
export interface StatusStepsProps {
  rcaStatus: Status;
  gradingStatus: Status;
}

export interface ConnectorProps {
  active: boolean;
}

export interface FileUploadPopupProps {
  open: boolean;
  onClose: () => void;
  onFileSelect: (file: File) => void;
  setProcessing: (val: boolean) => void;
  onSuccess: () => void;
}

export type fileUploadStatus = 'idle' | 'uploading' | 'importing' | 'extracting' | 'success' | 'error';

export type FooterProps = { year?: number; className?: string };

export interface PopupProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (value: string) => void;
  setInputValue: (value: string) => void;
  inputValue: string;
}

export interface Complaint {
  case_id: string;
  criticality: string;
  report_type: string;
  receipt_dtae: string; // You might want to correct this to 'receipt_date' if it's a typo
  case_type: string;
}

export interface CreateComplaintData {
  complaint: Complaint;
  message_id: string;
}

export interface CreateComplaintResponse {
  success: boolean;
  message: string;
  data: CreateComplaintData;
  timestamp: string;
}

export type ComplaintRequest = {
  narrative: string;
};

export type Case = {
  case_id: string;
  criticality: string;
  report_type: string;
  receipt_date: string;
  case_type: string[];
  text_extracted: boolean;
};

export type CaseStatus = {
  pending: Case[];
  processed: Case[];
  overdue: Case[];
};

export type CaseStats = {
  total_complaints: number;
  pending: number;
  processed: number;
  overdue: number;
  avg_cycle_time: number;
  best_time: number;
  longest_time: number;
};


export interface PaginationData {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

export type getComplaintsApiResponse = {
  caseStats: CaseStats;
  caseStatus: CaseStatus;
  pagination: PaginationData;
};

export type CategoryDetail = {
  id: string;
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
};

type PrimaryReporter = {
  name: string;
  address: string;
};

type ProductDetails = {
  drug: string;
  drug_name: string;
  dosage: string;
  lot_no: string;
  expiration_date: string;
  part_number: string;
};
export interface ComplaintDetail {
  case_id: string;
  receipt_date: string;
  criticality: string;
  report_type: string;
  ai_summary: string;
  case_type: string[];
  narrative: string;
  primary_reporter: PrimaryReporter; // undefined structure assumed, adjust if known
  patient_name: string;
  physician_name: string;
  product_details: ProductDetails; // undefined structure assumed, adjust if known
  caseStatus: string;
  category_details: CategoryDetail[];
}

export type CaseStatusKey = "pending" | "processed" | "overdue";

export interface complaintStatsProps {
  complaintStats: {
    "total_complaints": number,
    "pending": number,
    "processed": number,
    "overdue": number,
    "avg_cycle_time": number,
    "best_time": number,
    "longest_time": number,
  } | undefined
}

export type CategoryDetailApi = {
  id: string;
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
};

type PrimaryReporterApi = {
  name: string;
  address: string;
};

type ProductDetailsApi = {
  drug_name: string;
  dosage: string;
  lot_no: string;
  expiration_date: string;
};

export type ApproveComplaintResponse = {
  data: {
    case_id: string;
    receipt_date: string;
    criticality: string;
    report_type: string;
    ai_summary: string;
    case_type: string[];
    narrative: string;
    primary_reporter: PrimaryReporterApi;
    patient_name: string;
    physician_name: string;
    product_details: ProductDetailsApi;
    caseStatus: string;
    category_details: CategoryDetailApi[];
  }
};

export type ApproveComplaintRequest = {
    case_id: string;
    receipt_date: string;
    criticality: string;
    report_type: string;
    ai_summary: string;
    case_type: string[];
    narrative: string;
    primary_reporter: PrimaryReporterApi;
    patient_name: string;
    physician_name: string;
    product_details: ProductDetailsApi;
    caseStatus: string;
    category_details: CategoryDetailApi[];
};
