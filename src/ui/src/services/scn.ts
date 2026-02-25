import { apiRequest } from "src/api/apiClient";
import {
  ScnDetailsResponse,
  ScnListResponse,
  ScnFinalListResponse,
  ScnEditClassifyPayload,
  ScnEditClassifyResponse,
  ScnQmsAuditResponse,
} from "src/types";

// Accepts optional URLSearchParams for filters
export async function fetchScnList(
  limit = 50,
  offset = 0,
  params?: URLSearchParams,
): Promise<ScnListResponse> {
  let query = `limit=${limit}&offset=${offset}`;
  if (params) {
    query = params.toString();
  }
  return apiRequest<ScnListResponse>(`dev/scnList?${query}`, {
    method: "GET",
    token: true,
  });
}

export async function fetchScnDetails(
  emailId: string,
): Promise<ScnDetailsResponse> {
  return apiRequest<ScnDetailsResponse>(
    `dev/scnExtractedDetails?email_id=${emailId}`,
    {
      method: "GET",
      token: false,
    },
  );
}

export const editScn = async (
  emailId: string,
  formData: any,
  files?: File[],
) => {
  const multipart = new FormData();
  multipart.append("email_id", emailId);
  multipart.append("fields", JSON.stringify(formData));
  if (files && files.length > 0) {
    files.forEach((file) => multipart.append("files", file));
  }
  return apiRequest<any>("dev/scnEdit", {
    method: "POST",
    body: multipart,
    token: true,
  });
};

export const uploadScn = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("dev/scnUpload", {
    method: "POST",
    body: formData,
    token: true,
  });
};

export const scnClassify = async (emailId: string) => {
  return apiRequest<any>(`dev/scnClassify?email_id=${emailId}`, {
    method: "POST",
    token: false,
  });
};

export const scnClassificationResults = async (emailId: string) => {
  return apiRequest<any>(`dev/scnClassificationResults?email_id=${emailId}`, {
    method: "GET",
    token: false,
  });
};

export const scnEditClassify = async (
  emailId: string,
  payload: ScnEditClassifyPayload,
): Promise<ScnEditClassifyResponse> => {
  return apiRequest<ScnEditClassifyResponse>(
    `dev/scnEditClassify?email_id=${emailId}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
      headers: { "Content-Type": "application/json" },
      token: false,
    },
  );
};

export async function fetchScnQmsAudit(
  scnId: string,
): Promise<ScnQmsAuditResponse> {
  return apiRequest<ScnQmsAuditResponse>(
    `dev/scnQmsAudit?scn_id=${encodeURIComponent(scnId)}`,
    {
      method: "GET",
      token: false,
    },
  );
}

export async function fetchScnSupplierList(
  limit = 50,
  offset = 0,
  q = "",
): Promise<ScnFinalListResponse> {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  if (q) params.set("q", q);
  return apiRequest<ScnFinalListResponse>(
    `dev/scnFinalGet?${params.toString()}`,
    {
      method: "GET",
      token: true,
    },
  );
}
