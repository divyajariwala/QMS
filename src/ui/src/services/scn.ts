import { apiRequest } from "src/api/apiClient";
import { ScnDetailsResponse, ScnListResponse } from "src/types";

export async function fetchScnList(
  limit = 50,
  offset = 0,
): Promise<ScnListResponse> {
  return apiRequest<ScnListResponse>(`scn?limit=${limit}&offset=${offset}`, {
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
