import {
  SectionDataRes,
  GradingSuggestionsPayload,
  SubmitGradingPayload,
} from "@components/deviations/grading/GradingTypes";
import {
  getDeviationsApiResponse,
  DeviationDetail,
  DeviationSummary,
  DeviationSummaryResponse,
  DeviationGenerateRCA,
  GenerateRCAResponse,
} from "../types";

import { API_BASE_URL } from "src/config";

export const uploadDeviationFile = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}dev/uploadDeviations`, {
      method: "POST",
      body: formData,
    });

    if (res.ok) {
      return await res.json();
    }

    console.log(
      `uploadDeviationFile error: status ${res.status} ${res.statusText}`
    );
    return;
  } catch (err) {
    console.log("uploadDeviationFile error", err);
    return;
  }
};

export async function searchDeviation(
  deviation_id: string,
  page: number
): Promise<getDeviationsApiResponse> {
  const url = `${API_BASE_URL}dev/getDeviation?page=${page}&search=${deviation_id}`;

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: getDeviationsApiResponse = await response.json();
  return data;
}

export async function fetchDeviations(
  status: string,
  page: number
): Promise<getDeviationsApiResponse> {
  const response = await fetch(
    `${API_BASE_URL}dev/getDeviation?status=${status}&page=${page}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: getDeviationsApiResponse = await response.json();
  return data;
}

export async function fetchDeviationDetailById(
  deviation_id: string | undefined
): Promise<DeviationDetail> {
  const url = new URL(`${API_BASE_URL}dev/getDeviation`);
  if (deviation_id) url.searchParams.append("deviation_id", deviation_id);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: DeviationDetail = await response.json();
  return data;
}

export const saveInvestigationSummary = async (
  summary: DeviationSummary
): Promise<DeviationSummaryResponse> => {
  const response = await fetch(`${API_BASE_URL}dev/addInvestigationSummary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(summary),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: DeviationSummaryResponse = await response.json();
  return data;
};

export const generateRCA = async (
  deviation: DeviationGenerateRCA
): Promise<GenerateRCAResponse> => {
  const response = await fetch(`${API_BASE_URL}dev/generateRCA`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(deviation),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: GenerateRCAResponse = await response.json();
  return data;
};

export async function fetchRcaCategories() {
  const response = await fetch(`${API_BASE_URL}dev/getRCACategories`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

export const submitRca = async (rcaPayload) => {
  const response = await fetch(`${API_BASE_URL}dev/submitRCA`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(rcaPayload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
};

export async function fetchGradingData(
  deviation_id: string | undefined
): Promise<SectionDataRes> {
  const url = new URL(
    `${API_BASE_URL}dev/getGrading?deviation_id=${deviation_id}`
  );

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: SectionDataRes = await response.json();
  return data;
}

export const fetchGradingSuggestions = async (
  payload: GradingSuggestionsPayload
) => {
  const response = await fetch(`${API_BASE_URL}dev/startGrading`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
};

export const submitGrading = async (payload: SubmitGradingPayload) => {
  const response = await fetch(`${API_BASE_URL}dev/submitGrading`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
};
