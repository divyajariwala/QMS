import {
  ComplaintRequest,
  CreateComplaintResponse,
  getComplaintsApiResponse,
  ComplaintDetail,
  ApproveComplaintResponse,
  ApproveComplaintRequest,
  searchComplaintsApiResponse,
  searchAdverseEventsApiResponse,
  getAdverseEventsApiResponse,
} from "../types";

import { API_BASE_URL } from "src/config";

/**
 * Uploads a complaint file to the backend.
 *
 * @param file - The file to upload.
 * @returns The response data from the upload endpoint. May be undefined if an error occurs.
 */
export const uploadComplaintFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}dev/uploadComplaints`, {
      method: "POST",
      body: formData,
    });

    if (res.ok) {
      return await res.json();
    }

    console.log(
      `uploadComplaintFile error: status ${res.status} ${res.statusText}`
    );
    return;
  } catch (err) {
    console.log("uploadComplaintFile error", err);
    return;
  }
};

export const createComplaint = async (
  complaint: ComplaintRequest
): Promise<CreateComplaintResponse> => {
  const response = await fetch(`${API_BASE_URL}dev/createComplaint`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(complaint),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: CreateComplaintResponse = await response.json();
  return data;
};

export async function fetchComplaints(
  status: string,
  page: number
): Promise<getComplaintsApiResponse> {
  const response = await fetch(
    `${API_BASE_URL}dev/getComplaints?status=${status}&page=${page}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: getComplaintsApiResponse = await response.json();
  return data;
}

export async function fetchAdverseEvent(
  page: number
): Promise<getAdverseEventsApiResponse> {
  const response = await fetch(
    `${API_BASE_URL}dev/getComplaints?adverse_events=true&page=${page}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: getAdverseEventsApiResponse = await response.json();
  return data;
}

export async function fetchComplaintDetailById(
  complaint_id: string | undefined
): Promise<ComplaintDetail> {
  const url = new URL(`${API_BASE_URL}dev/getComplaints`);
  if (complaint_id) url.searchParams.append("complaint_id", complaint_id);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: ComplaintDetail = await response.json();
  return data;
}

export async function postApproveComplaint(
  data: ApproveComplaintRequest
): Promise<ApproveComplaintResponse> {
  const response = await fetch(`${API_BASE_URL}dev/approveComplaints`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const responseData: ApproveComplaintResponse = await response.json();
  return responseData;
}

export async function classifyComplaint<T = any>(
  complaintId: string
): Promise<T> {
  const url = `${API_BASE_URL}dev/classifyComplaints`;
  const payload = { complaint_id: complaintId };

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: T = await response.json();
  return data;
}

interface Reporter {
  name: string;
  address: string;
}

interface ModifyExtractedDetailsPayload {
  status: string;
  caseId: string;
  overdueDays: number;
  primaryReporter: Reporter;
  patientName: string;
  physicianName: string;
  drug: string;
  lotNumber: string;
  doseAmount: string;
  expirationDate: string; // ISO string
  partNumber: string;
  receipt_date: string; // ISO string
}

export async function modifyExtractedDetails(
  payload: ModifyExtractedDetailsPayload
): Promise<ModifyExtractedDetailsPayload> {
  const url = `${API_BASE_URL}dev/modifyExtractedDetails`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // Add auth headers if needed
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: ModifyExtractedDetailsPayload = await response.json();
  return data;
}

export async function searchComplaint(
  complaint_id: string,
  page: number
): Promise<searchComplaintsApiResponse> {
  const url = `${API_BASE_URL}dev/getComplaints?search=${complaint_id}&page=${page}`;

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: searchComplaintsApiResponse = await response.json();
  return data;
}

export async function searchAdverseEvent(
  complaint_id: string,
  page: number
): Promise<searchAdverseEventsApiResponse> {
  const url = `${API_BASE_URL}dev/getComplaints?adverse_events=true&search=${complaint_id}&page=${page}`;

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: searchAdverseEventsApiResponse = await response.json();
  return data;
}
