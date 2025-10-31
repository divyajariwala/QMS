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
  label: string;
  to?: string;
}

export interface CommonBreadcrumbsProps {
  items: BreadcrumbItem[];
  ariaLabel?: string;
}

export interface LegendItemProps {
  colorClass: "dotPending" | "dotProcessed" | "dotOverdue" | undefined;
  label: string;
  value: string | number;
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
  cardValue: string | number;
  legend?: LegendData[];
}

export interface ComplaintCategoryItem {
  id: string;
  label: string;
  level: number;
  crl: string;
  priority: string;
  unit: number;
  percentage: number;
  color: string;
  bgColor: string;
}
export interface ComplaintCategoryProps {
  complaintCategories: ComplaintCategoryItem[];
  onSave?: (updatedItem: ComplaintCategoryItem) => void;
}

export interface ComplaintHeaderCardProps {
  complaintData: {
    status: string;
    caseId: string;
    overdueDays: number;
    primaryReporter: { name: string; location: string };
    patientName: string;
    physicianName: string;
    drug: string;
    lotNumber: string;
    doseAmount: string;
    expirationDate: string;
    partNumber: string;
  };
  onApproveAndSend: () => void;
}

export interface ComplaintsDueDateChipProps {
  type: "Overdue" | "Today" | "Tomorrow" | "Due";
  label: string;
}

export interface DueDateChipProps {
  iconSrc: string;
  iconAlt: string;
  label: string;
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
}

export interface StatusTabItem {
  label: string;
  count: number;
  description: React.ReactNode;
}

export interface ComplaintProps {
  complaint: {
    "Criticality": string;
    "Report Type": string;
    "Category": string;
    "Receipt Date": string;
    "Case Type": string[];
    "Due Date": string;
  };
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
    "gradingStatus": string
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
}

export type fileUploadStatus = 'idle' | 'uploading' | 'importing' | 'extracting' | 'success' | 'error';

export type FooterProps = { year?: number; className?: string };

export interface PopupProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (value: string) => void;
}