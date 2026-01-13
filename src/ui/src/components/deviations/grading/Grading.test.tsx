// Grading.test.tsx
import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import Grading from "./Grading";

// Mock static assets & styles
jest.mock("../../../assets/icons/grading.svg", () => "grading");
jest.mock("../../../assets/icons/refresh.svg", () => "refresh");
jest.mock("../../../assets/icons/arrowRight.svg", () => "arrowRight");
jest.mock("./grading.module.scss", () => new Proxy({}, { get: () => "" }));

// Mock services and mockdata
const mockFetchGradingData = jest.fn();
jest.mock("src/services/deviations", () => ({
  fetchGradingData: (...args: any[]) => mockFetchGradingData(...args),
}));

const mockFetchImprovementSuggestions = jest.fn();
const mockFetchExecutiveSummary = jest.fn();
jest.mock("./mockdata", () => ({
  fetchImprovementSuggestionsMock: (...args: any[]) =>
    mockFetchImprovementSuggestions(...args),
  fetchExecutiveSummaryMock: (...args: any[]) =>
    mockFetchExecutiveSummary(...args),
}));

// Helpers
const sections = [
  { label: "Title", content: "Deviation ABC - QA Verification Gap" },
  {
    label: "Description",
    content: "Context of deviation and missing QA step.",
  },
  {
    label: "Immediate Steps Taken",
    content: "Contained issue; notified stakeholders.",
  },
  {
    label: "Quality Risk Evaluation",
    content: "Potential impact pathways listed.",
  },
  { label: "Investigation Details", content: "Timeline, roles, evidence." },
  { label: "CAPA Plan", content: "Owners, due dates, measurable outcomes." },
  { label: "Recurrence Check Details", content: "Scope, acceptance criteria." },
  { label: "Effectiveness Check Plan", content: "Audits, validation plan." },
];

const suggestionsDefault = [
  { text: "Improve title clarity.", score: 7, sectionLabel: "Title" }, // positive
  { text: "Streamline description.", score: 5, sectionLabel: "Description" }, // negative
  { text: "Bulletize steps.", score: 7, sectionLabel: "Immediate Steps Taken" }, // positive
  {
    text: "Strengthen risk rationale.",
    score: 8,
    sectionLabel: "Quality Risk Evaluation",
  },
  {
    text: "Add traceability evidence.",
    score: 9,
    sectionLabel: "Investigation Details",
  },
  { text: "Tie actions to root cause.", score: 8, sectionLabel: "CAPA Plan" },
  {
    text: "Specify sample size.",
    score: 7,
    sectionLabel: "Recurrence Check Details",
  },
  {
    text: "Define zero recurrence.",
    score: 8,
    sectionLabel: "Effectiveness Check Plan",
  },
];

const execSummaryItems = [
  { label: "Title", content: sections[0].content },
  { label: "Overview", content: sections[1].content },
];

const renderWithRouter = (ui: React.ReactNode, path = "/123") => {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/:deviationId" element={ui as React.ReactElement} />
      </Routes>
    </MemoryRouter>
  );
};

describe("Grading", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("compose → grading flow, suggestions, regenerate, executive summary submit", async () => {
    mockFetchGradingData.mockResolvedValue({ data: sections });
    mockFetchImprovementSuggestions.mockResolvedValue(suggestionsDefault);
    mockFetchExecutiveSummary.mockResolvedValue(execSummaryItems);

    const onEnterReview = jest.fn();
    const onProcessed = jest.fn();

    renderWithRouter(
      <Grading onEnterReview={onEnterReview} onProcessed={onProcessed} />
    );

    // Initially loading sections
    expect(screen.getByText(/Loading sections…/i)).toBeInTheDocument();

    // Sections render in compose mode
    await waitFor(() => {
      sections.forEach((s) => {
        expect(screen.getByText(s.label)).toBeInTheDocument();
        expect(screen.getByText(s.content)).toBeInTheDocument();
      });
    });

    // Start Grading
    const startBtn = screen.getByRole("button", { name: /Start Grading/i });
    fireEvent.click(startBtn);

    // Suggestions loading indicator
    expect(screen.getByText(/Updating…/i)).toBeInTheDocument();

    // Suggestions appear and snackbar shows success
    await waitFor(() => {
      suggestionsDefault.forEach((sg) => {
        expect(screen.getByText(/Improvement Suggestion/i)).toBeInTheDocument();
        expect(screen.getByText(sg.text)).toBeInTheDocument();
      });
      expect(
        screen.getByText(/Improvement suggestions updated/i)
      ).toBeInTheDocument();
    });

    // Icon logic: check counts of thumbsUp and thumbsDown via classnames
    const allRows = screen
      .getAllByText(/Improvement Suggestion/i)
      .map((el) => el.closest("div"));
    const thumbsUpIcons = document.querySelectorAll(".thumbsUp");
    const thumbsDownIcons = document.querySelectorAll(".thumbsDown");
    expect(thumbsUpIcons.length).toBeGreaterThan(0); // positives exist
    expect(thumbsDownIcons.length).toBeGreaterThan(0); // one negative exists

    // Regenerate
    const regenBtn = screen.getByRole("button", { name: /Regenerate/i });
    fireEvent.click(regenBtn);
    expect(regenBtn).toBeDisabled();
    await waitFor(() => {
      expect(
        screen.getByText(/Improvement suggestions updated/i)
      ).toBeInTheDocument();
      expect(regenBtn).not.toBeDisabled();
    });

    // Generate Executive Summary
    const genSummaryBtn = screen.getByRole("button", {
      name: /Generate Executive Summary/i,
    });
    fireEvent.click(genSummaryBtn);

    await waitFor(() => {
      // ExecutiveSummary rendered
      expect(
        screen.getByText(/AI Generated Executive Summary/i)
      ).toBeInTheDocument();
    });

    // onEnterReview was called
    expect(onEnterReview).toHaveBeenCalledTimes(1);

    // Save and send
    const saveBtn = screen.getByRole("button", {
      name: /Save and Send to QMS/i,
    });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      // Success snackbar
      expect(
        screen.getByText(/Summary sent successfully./i)
      ).toBeInTheDocument();
      // onProcessed called
      expect(onProcessed).toHaveBeenCalledTimes(1);
    });

    // After submission, ExecutiveSummary should become disabled (no primary action)
    expect(
      screen.queryByRole("button", { name: /Save and Send to QMS/i })
    ).not.toBeInTheDocument();

    // Back to grading view
    const backIcon = screen.getByAltText(/left arrow/i);
    fireEvent.click(backIcon);

    await waitFor(() => {
      expect(
        screen.getByText(/Generate Executive Summary/i)
      ).toBeInTheDocument();
    });

    // In grading view after submission, generate summary button should be disabled
    const genSummaryBtnAfter = screen.getByRole("button", {
      name: /Generate Executive Summary/i,
    });
    expect(genSummaryBtnAfter).toBeDisabled();
  });

  test("handles fetchGradingData error and suggestion fetch error", async () => {
    mockFetchGradingData.mockRejectedValue(new Error("load failed"));
    mockFetchImprovementSuggestions.mockRejectedValue(
      new Error("suggestions failed")
    );

    renderWithRouter(<Grading />);

    // Error snackbar for sections
    await waitFor(() => {
      expect(screen.getByText(/Failed to load sections/i)).toBeInTheDocument();
    });

    // Start grading even with empty values; suggestions fail
    const startBtn = screen.getByRole("button", { name: /Start Grading/i });
    fireEvent.click(startBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/Failed to fetch improvement suggestions/i)
      ).toBeInTheDocument();
    });
  });

  test("neutral icon and no suggestion available branch", async () => {
    mockFetchGradingData.mockResolvedValue({ data: sections });
    // Make one suggestion neutral (no score) and omit last suggestion to trigger "No suggestion available"
    const mixedSuggestions = suggestionsDefault
      .map((s, idx) =>
        idx === 2
          ? { text: "No score suggestion", sectionLabel: s.sectionLabel }
          : s
      )
      .slice(0, sections.length - 1);
    mockFetchImprovementSuggestions.mockResolvedValue(mixedSuggestions);

    renderWithRouter(<Grading />);

    // Go to grading
    await waitFor(() => screen.getByRole("button", { name: /Start Grading/i }));
    fireEvent.click(screen.getByRole("button", { name: /Start Grading/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/Improvement suggestions updated/i)
      ).toBeInTheDocument();
    });
    const sectionRows = screen
      .getAllByText(/Improvement Suggestion/i)
      .map((el) => el.closest("div"));
    const upCount = document.querySelectorAll(".thumbsUp").length;
    const downCount = document.querySelectorAll(".thumbsDown").length;
    expect(upCount).toBeGreaterThan(0);
    expect(downCount).toBeGreaterThan(0);

    expect(
      screen.getByText(/No suggestion available for this section yet\./i)
    ).toBeInTheDocument();
  });
});
