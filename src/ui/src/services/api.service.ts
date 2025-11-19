import {
  COMPLAINT_ID_NAME,
  COMPLAINT_SESSION_ID,
  COMPLAINT_USER_NAME,
} from '../constants';
import { ComplaintResult, SessionData, UIResultsParams, ComplaintRequest, CreateComplaintResponse, getComplaintsApiResponse,
   ComplaintDetail, ApproveComplaintResponse, ApproveComplaintRequest } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

/**
 * Fetches the initial data from the backend.
 * The initial data includes the drug name and narrative. Any or all of the values can be null.
 *
 * @param id - The complaint id received from Veeva (by URL).
 * @param sessionId - The session id received from Veeva.
 * @param userName - The user name received from Veeva.
 * @returns The initial data object. May be undefined if an error occurs.
 */
export const getInitialData = async (
  id: string,
  sessionId: string | null,
  userName: string | null,
) => {
  try {
    const q = `${COMPLAINT_ID_NAME}=${id}&${COMPLAINT_SESSION_ID}=${sessionId}&${COMPLAINT_USER_NAME}=${userName}`;
    const res = await fetch(`${API_BASE_URL}getinitialdata?${q}`, {
      method: 'GET',
    });

    if (res.ok) {
      return await res.json();
    }

    return;
  } catch (err) {
    console.log('getinitialdata error', err);
    return;
  }
}

/**
 * Sends the drug name and narrative text to the backend.
 *
 * @param id - The complaint id.
 * @param date - A date. Normally the current date.
 * @param drugName - The drug name.
 * @param narrativeText  - The narrative text.
 * @returns A data object containing the result of the drug name and narrative processing in the backend. May be undefined if an error occurs.
 */
export const invokeApi = async (
  id: string | null,
  date: string,
  drugName: string,
  narrativeText: string,
  sessionData: SessionData | null,
) => {
  const params = {
    complaint_id: id,
    time: date,
    narrative: narrativeText,
    drugname: drugName,
    session_id: sessionData?.session_id ?? null,
    user_name: sessionData?.user_name ?? null,
  };

  try {
    const res = await fetch(`${API_BASE_URL}invokeapi`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (res.ok) {
      return await res.json();
    }

    return;
  } catch (err) {
    console.log('invokeApi error', err);
    return;
  }
}

/**
 * Triggers the backend categorization process. Uses the data sent by the invokeApi endpoint.
 * This method must be called after the invokeApi method.
 *
 * @param id - The complaint id.
 * @returns Control data. May be undefined if an error occurs.
 */
export const categoryInvoke = async (id: string) => {
  const params = {
    complaint_id: id,
  };

  try {
    const res = await fetch(`${API_BASE_URL}categoryinvoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (res.ok) {
      return await res.json();
    }

    return;
  } catch (err) {
    console.log('categoryInvoke error', err);
    return;
  }
}

/**
 * Fetches the final result of the complaint.
 *
 * @param id - The complaint id.
 * @returns The complaint result object. May be undefined if an error occurs.
 */
export const fetchResults = async (id: string) => {
  const params = {
    complaint_id: id,
  };

  try {
    const response = await fetch(`${API_BASE_URL}fetchresults`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (response.ok) {
      return await response.json();
    }

    return;
  } catch (err) {
    console.log('fetchResults error', err);
    return;
  }
}

/**
 * Sends the final results (edited and approved by the user) to the backend.
 *
 * @param id - The complaint id.
 * @param data - The complete result data.
 * @param priority - The original priority value.
 * @param modelPriority - The edited priority value.
 * @returns Control data (not used in the UI). May be undefined if an error occurs.
 */
export const uiResults = async (
  id: string,
  data: ComplaintResult[],
  priority: number | null,
  modelPriority: number | null,
) => {
  const params: UIResultsParams = {
    complaint_id: id,
    data,
  };

  if (priority !== null && modelPriority !== null) {
    params.priority = priority;
    params.modelPriority = modelPriority;
  }

  try {
    const res = await fetch(`${API_BASE_URL}uiresults`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (res.ok) {
      return await res.json();
    }

    return;
  } catch (err) {
    console.log('uiResults error', err);
    return;
  }
}

/**
 * Obtains an html content.
 *
 * @param url - The URL to the HTML file stored in an S3 bucket.
 * @returns The HTML content.
 */
export const fetchHtml = async (url: string) => {
  try {
    const res = await fetch(url);

    if (res.ok) {
      return await res.text();
    }

    return;
  } catch (err) {
    console.log('fetchHtml error', err);
    return;
  }
}

/**
 * Uploads a complaint file to the backend.
 *
 * @param file - The file to upload.
 * @returns The response data from the upload endpoint. May be undefined if an error occurs.
 */
export const uploadComplaintFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/uploadComplaints`, {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      return await res.json();
    }

    console.log(`uploadComplaintFile error: status ${res.status} ${res.statusText}`);
    return;
  } catch (err) {
    console.log('uploadComplaintFile error', err);
    return;
  }
};


export const createComplaint = async (
  complaint: ComplaintRequest
): Promise<CreateComplaintResponse> => {
  const response = await fetch(
    "https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/createComplaint",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(complaint),
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: CreateComplaintResponse = await response.json();
  return data;
};

export async function fetchComplaints(status: string, page: Number): Promise<getComplaintsApiResponse> {
  const response = await fetch(
    `https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/getComplaints?status=${status}&page=${page}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: getComplaintsApiResponse = await response.json();
  return data;
}

export async function fetchComplaintDetailById(complaint_id: string | undefined): Promise<ComplaintDetail> {
  const url = new URL("https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/getComplaints");
  if(complaint_id) url.searchParams.append("complaint_id", complaint_id);

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
  const response = await fetch("https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/approveComplaints", {
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


export async function classifyComplaint<T = any>(complaintId: string): Promise<T> {
  const url = 'https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/classifyComplaints';
  const payload = { complaint_id: complaintId };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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
  expirationDate: string;  // ISO string
  partNumber: string;
  receipt_date: string;    // ISO string
}

export async function modifyExtractedDetails(
  payload: ModifyExtractedDetailsPayload
): Promise<ModifyExtractedDetailsPayload> {
  const url = 'https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/modifyExtractedDetails';

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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



