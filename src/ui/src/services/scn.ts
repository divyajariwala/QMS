import { apiRequest } from "src/api/apiClient";
import { ScnDetailsResponse, ScnListResponse } from "src/types";

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
      token: true,
    },
  );
}

export const editScn = async (emailId: string, formData: any, file?: File) => {
  const multipart = new FormData();
  multipart.append("email_id", emailId);
  multipart.append("fields", JSON.stringify(formData));
  if (file) {
    multipart.append("files", file);
  }
  return apiRequest<any>(`dev/scn/edit?email_id=${emailId}`, {
    method: "POST",
    body: multipart,
    token: true,
  });
};
