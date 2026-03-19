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
    MD5OfMessageBody: string;
    MessageId: string;
    ResponseMetadata: {
      RequestId: string;
      HTTPStatusCode: number;
      HTTPHeaders: {
        "x-amzn-requestid": string;
        date: string;
        "content-type": string;
        "content-length": string;
        connection: string;
      };
      RetryAttempts: number;
    };
  };
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
}

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
  caseStatus: string | undefined;
  crlList: string[];
  labelList: string[];
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
  isApproved: boolean;
  createdAt: string | undefined;
}

export interface AdverseEventHeaderProps {
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
  createdAt: string | undefined;
  processingFile: boolean;
}

export interface ModuleDueDateChipProps {
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
  caseType: string[];
}

export interface StatusTabItem {
  label: string;
  count: number | undefined;
}

export interface AdverseEventCardProps {
  complaint: {
    case_id: string;
    criticality: string;
    report_type: string;
    receipt_date: string; // You might want to correct this to 'receipt_date' if it's a typo
    case_type: string[];
    text_extracted: boolean;
    created_at: string;
  };
}

export interface ComplaintProps {
  complaint: {
    case_id: string;
    criticality: string;
    report_type: string;
    receipt_date: string; // You might want to correct this to 'receipt_date' if it's a typo
    case_type: string[];
    text_extracted: boolean;
    created_at: string;
    status?: "pending" | "processed" | "overdue";
  };
  selected: string;
  activeStatus: "pending" | "processed" | "overdue";
  loading: boolean;
  searching: boolean;
}

export interface ButtonGroupProps {
  onSelect?: (selected: string) => void;
  selected?: string;
}

export interface DeviationProps {
  deviation: {
    deviation_id: string;
    created_date: string;
    deviation_description: string;
    status: string;
    rca_approved: boolean;
    grading_completed: boolean;
    rca_generated: boolean;
    text_extracted: boolean;
  };
  selected: string;
  activeStatus: "pending" | "processed" | "overdue";
  loading: boolean;
  searching: boolean;
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
  setProcessing: (val: boolean) => void;
  onSuccess: () => void;
  setOpenFileUpload: (val: boolean) => void;
}

export type fileUploadStatus =
  | "idle"
  | "uploading"
  | "importing"
  | "extracting"
  | "success"
  | "error";

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

export interface GenerateRCAData {
  deviation_id: string;
  issues: string;
  issues_category: string;
  major_root_cause_category: string;
  major_root_cause_category_validated: string;
  near_root_cause: string;
  near_root_cause_category: string;
  root_cause: string;
  root_cause_category: string;
}

export interface CreateComplaintResponse {
  success: boolean;
  message: string;
  data: CreateComplaintData;
  timestamp: string;
}

export interface GenerateRCAResponse {
  success: boolean;
  message: string;
  data: GenerateRCAData;
  timestamp: string;
}

export interface DeviationSummaryResponse {
  success: boolean;
  message: string;
}

export type ComplaintRequest = {
  narrative: string;
};

export type DeviationSummary = {
  deviationId: string | undefined;
  summary: string;
};

export type DeviationGenerateRCA = {
  deviationId: string | undefined;
  investigation_summary: string;
};

export type Case = {
  case_id: string;
  criticality: string;
  report_type: string;
  receipt_date: string;
  case_type: string[];
  text_extracted: boolean;
  created_at: string;
};

export type Deviation = {
  deviation_id: string;
  created_date: string;
  deviation_description: string;
  status: string;
  rca_approved: boolean;
  grading_completed: boolean;
  rca_generated: boolean;
  text_extracted: boolean;
};

export type CaseStatus = {
  pending: Case[];
  processed: Case[];
  overdue: Case[];
};

export type CaseStatsComplaints = {
  total_complaints: number;
  pending: number;
  processed: number;
  overdue: number;
  avg_cycle_time: number;
  best_time: number;
  longest_time: number;
};

export type CaseStatsDeviations = {
  total_deviations: number;
  pending: number;
  processed: number;
  overdue: number;
  avg_cycle_time: number;
  rca_pending: number;
  rca_done: number;
  grading_pending: number;
  grading_done: number;
  workflow_progress: number;
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
  caseStats: CaseStatsComplaints;
  caseStatus: CaseStatus;
  pagination: PaginationData;
};

export type getAdverseEventsApiResponse = {
  pagination: PaginationData;
  adverse_events: Case[];
};

export type getDeviationsApiResponse = {
  deviationStats: CaseStatsDeviations;
  pagination: PaginationData;
  deviations: Deviation[];
};

export type searchComplaintsApiResponse = {
  caseStats: CaseStatsComplaints;
  caseStatus: CaseStatus;
  pagination: PaginationData;
  search_results: Case[];
};

export type searchAdverseEventsApiResponse = {
  pagination: PaginationData;
  adverse_events: Case[];
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
  complaintClassified?: boolean;
  created_at?: string;
  crl_list: string[];
  label_list: string[];
  text_extracted?: boolean;
}

export interface DeviationDetail {
  deviation_id: string;
  investigation_summary: string;
  created_date: string;
  status: string;
  rca_approved: boolean;
  grading_completed: boolean;
}

export type CaseStatusKey = "pending" | "processed" | "overdue";

export interface complaintStatsProps {
  complaintStats:
    | {
        total_complaints: number;
        pending: number;
        processed: number;
        overdue: number;
        avg_cycle_time: number;
        best_time: number;
        longest_time: number;
      }
    | undefined;
}

export interface deviationStatsProps {
  deviationStats:
    | {
        total_deviations: number;
        pending: number;
        processed: number;
        overdue: number;
        avg_cycle_time: number;
        rca_pending: number;
        rca_done: number;
        grading_pending: number;
        grading_done: number;
        workflow_progress: number;
      }
    | undefined;
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
  };
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

export interface PaginationObj {
  current_page: number;
  total_pages: number;
  total_items: number;
  items_per_page: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface AdverseEventFilterProps {
  complaintId: string;
  setComplaintId: (val: string) => void;
  setComplaintDetail: (val: searchAdverseEventsApiResponse | null) => void;
  setSearchActive: (val: boolean) => void;
  setPagination: (val: PaginationObj) => void;
  doSearch: (id: string, page?: number) => Promise<void>;
}

export interface ScnVolumeTrend {
  dates: string[];
  counts: number[];
}

export interface AvgProcessingTime {
  seconds: number;
  human_readable: string;
}

export interface ScnListItem {
  email_id: string;
  scn_reference_number: string;
  supplier_name: string;
  change_classification_supplier: string;
  planned_implementation_date: string;
  notification_date: string;
  completion_score: number;
  status: string;
  created_at?: string;
  updated_at: string;
}

export interface ScnListResponse {
  success: boolean;
  message: string;
  data: {
    limit: number;
    offset: number;
    count: number;
    items: ScnListItem[];
    filters: {
      limit: number;
      offset: number;
      q: string | null;
    };
    supplier_names: string[];
    change_classification_supplier_list: string[];
    risk_level_summary?: any;
    classification_summary?: any;
    avg_processing_time?: AvgProcessingTime;
    scn_volume_trend?: ScnVolumeTrend;
  };
  timestamp: string;
}

export interface ScnDetailsResponse {
  success: boolean;
  message: string;
  data: {
    email_id: string;
    scn_extracted_fields: Record<string, any>;
    raw_email: {
      download_url: string;
    };
    attachments: {
      attachment_id: string;
      filename: string;
      status: string;
      download_url: string;
    }[];
  };
  timestamp: string;
}

export interface ScnFinalItem {
  email_id: string;
  scn_reference_number: string;
  supplier_name: string;
  notification_date: string;
  planned_implementation_date: string;
  status: string;
  final_classification: string;
  final_risk_level: string;
  updated_at: string;
  change_classification_supplier: string;
}

export interface ScnFinalSummary {
  total: number;
  approved: number;
  rejected: number;
  pending_review: number;
  in_review: number;
}

export interface ScnFinalListResponse {
  success: boolean;
  message: string;
  data: {
    count: number;
    items: ScnFinalItem[];
    filters: {
      limit: number;
      offset: number;
      q: string | null;
    };
    summary: ScnFinalSummary;
  };
  timestamp: string;
}
export interface ScnEditClassifyPayload {
  change_classification_supplier?: string;
  change_control_required?: "yes" | "no";
  action_required?: string;
  final_risk_level?: string;
  final_assigned_team?: string;
}

export interface ScnEditClassifyResponse {
  success: boolean;
  message: string;
  data: {
    email_id: string;
    updated_fields: string[];
  };
  timestamp: string;
}

export interface ScnAuditItem {
  id: number;
  scn_id: string;
  changed_field: string;
  old_value: string | null;
  new_value: string | null;
  changed_by: string;
  created_at: string;
}

export interface ScnQmsAuditResponse {
  success: boolean;
  message: string;
  data: {
    scn_id: string;
    count: number;
    items: ScnAuditItem[];
  };
  timestamp: string;
}

export interface ScnApproveRequest {
  action: "APPROVE";
  change_control_required: "yes" | "no";
}

export interface ScnRejectRequest {
  action: "REJECT";
  reason_for_reject: string;
}

export interface ScnRequestInfoRequest {
  action: "REQUEST_INFO";
  fields: string;
  comment: string;
}

export type ScnApproveRejectRequest =
  | ScnApproveRequest
  | ScnRejectRequest
  | ScnRequestInfoRequest;

export interface ScnApproveRejectResponse {
  success: boolean;
  message: string;
  data: {
    email_id: string;
    action: "APPROVED" | "REJECTED";
    change_control_required?: string;
    cc_record_id?: string;
    note?: string | null;
    reason_for_reject?: string;
  };
  timestamp: string;
}

export interface ToggleClassificationResponse {
  email_id: string;
  old_classification?: string;
  new_classification?: string;
  changed: boolean;
  risk_analysis_triggered?: boolean;
  message?: string;
}
