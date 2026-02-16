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
  return apiRequest<ScnDetailsResponse>(`scn/${emailId}`, {
    method: "GET",
    token: true,
  });
}
