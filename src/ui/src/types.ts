import { User} from "oidc-client-ts";

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