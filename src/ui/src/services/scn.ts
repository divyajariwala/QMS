
import { API_BASE_URL } from "src/config";

/* ---------- Types ---------- */

export interface ScnListItem {
  email_id: string;
  scn_reference_number: string;
  supplier_name: string;
  change_classification_supplier: string;
  planned_implementation_date: string;
  notification_date: string;
  created_at: string;
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

/* ---------- API Calls ---------- */

// LEFT PANEL — list
export async function fetchScnList(
  limit = 50,
  offset = 0
): Promise<ScnListResponse> {
  const res = await fetch(
    `${API_BASE_URL}scn?limit=${limit}&offset=${offset}`
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch SCN list`);
  }

  return res.json();
}

// RIGHT PANEL — details
export async function fetchScnDetails(
  emailId: string,
  fields?: string[]
): Promise<ScnDetailsResponse> {
  const url = new URL(`${API_BASE_URL}scn/${emailId}`);

  if (fields?.length) {
    url.searchParams.append("fields", fields.join(","));
  }

  const res = await fetch(url.toString());

  if (!res.ok) {
    throw new Error(`Failed to fetch SCN details`);
  }

  return res.json();
}