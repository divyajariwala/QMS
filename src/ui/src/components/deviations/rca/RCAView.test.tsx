import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RCAView from "./RCAView";
import { RcaRecord } from "./RCATypes";

describe("RCAView", () => {
  const mockRca: RcaRecord = {
    id: "rca-1",
    name: "RCA 1",
    sections: [
      {
        key: "issues",
        title: "Causal factor",
        value: "Issue 1",
        explanation: "Explanation for issue",
      },
      {
        key: "major",
        title: "Major root cause category",
        value: "Major 1",
        explanation: "Explanation for major",
      },
      {
        key: "near",
        title: "Near root cause",
        value: "Near 1",
        explanation: "Explanation for near",
      },
      {
        key: "root",
        title: "Root cause",
        value: "Root 1",
        explanation: "Explanation for root",
      },
    ],
  };

  test("renders RCA sections", () => {
    render(<RCAView rca={mockRca} />);
    expect(screen.getByText("Causal factor")).toBeInTheDocument();
    expect(screen.getByText("Issue 1")).toBeInTheDocument();
  });

  test("renders all section titles", () => {
    render(<RCAView rca={mockRca} />);
    expect(screen.getByText("Causal factor")).toBeInTheDocument();
    expect(screen.getByText("Major root cause category")).toBeInTheDocument();
    expect(screen.getByText("Near root cause")).toBeInTheDocument();
    expect(screen.getByText("Root cause")).toBeInTheDocument();
  });

  test("renders section values", () => {
    render(<RCAView rca={mockRca} />);
    expect(screen.getByText("Issue 1")).toBeInTheDocument();
    expect(screen.getByText("Major 1")).toBeInTheDocument();
    expect(screen.getByText("Near 1")).toBeInTheDocument();
    expect(screen.getByText("Root 1")).toBeInTheDocument();
  });

  test("renders section explanations", () => {
    render(<RCAView rca={mockRca} />);
    expect(screen.getByText("Explanation for issue")).toBeInTheDocument();
    expect(screen.getByText("Explanation for major")).toBeInTheDocument();
    expect(screen.getByText("Explanation for near")).toBeInTheDocument();
    expect(screen.getByText("Explanation for root")).toBeInTheDocument();
  });

  test("renders empty sections when values are empty", () => {
    const emptyRca: RcaRecord = {
      ...mockRca,
      sections: mockRca.sections.map((section) => ({
        ...section,
        value: "",
        explanation: "",
      })),
    };
    render(<RCAView rca={emptyRca} />);
    expect(screen.getByText("Causal factor")).toBeInTheDocument();
  });

  test("renders with different RCA data", () => {
    const differentRca: RcaRecord = {
      id: "rca-2",
      name: "RCA 2",
      sections: [
        {
          key: "issues",
          title: "Causal factor",
          value: "Different Issue",
          explanation: "Different explanation",
        },
        ...mockRca.sections.slice(1),
      ],
    };
    render(<RCAView rca={differentRca} />);
    expect(screen.getByText("Different Issue")).toBeInTheDocument();
    expect(screen.getByText("Different explanation")).toBeInTheDocument();
  });

  test("truncates long explanations and shows See More button", () => {
    const longExplanation = "A".repeat(250); // Longer than CHAR_LIMIT (200)
    const rcaWithLongExplanation: RcaRecord = {
      ...mockRca,
      sections: mockRca.sections.map((section, idx) =>
        idx === 0 ? { ...section, explanation: longExplanation } : section
      ),
    };
    render(<RCAView rca={rcaWithLongExplanation} />);
    expect(screen.getByText("See More")).toBeInTheDocument();
    expect(screen.getByText(/…$/)).toBeInTheDocument(); // Ends with ellipsis
  });

  test("expands and collapses explanation on See More/See Less click", async () => {
    const longExplanation = "A".repeat(250);
    const rcaWithLongExplanation: RcaRecord = {
      ...mockRca,
      sections: mockRca.sections.map((section, idx) =>
        idx === 0 ? { ...section, explanation: longExplanation } : section
      ),
    };
    render(<RCAView rca={rcaWithLongExplanation} />);
    const seeMoreButton = screen.getByText("See More");
    await userEvent.click(seeMoreButton);
    expect(screen.getByText("See Less")).toBeInTheDocument();
    expect(screen.getByText(longExplanation)).toBeInTheDocument();
    const seeLessButton = screen.getByText("See Less");
    await userEvent.click(seeLessButton);
    expect(screen.getByText("See More")).toBeInTheDocument();
  });

  test("does not show See More button for short explanations", () => {
    const shortExplanation = "Short explanation";
    const rcaWithShortExplanation: RcaRecord = {
      ...mockRca,
      sections: mockRca.sections.map((section, idx) =>
        idx === 0 ? { ...section, explanation: shortExplanation } : section
      ),
    };
    render(<RCAView rca={rcaWithShortExplanation} />);
    expect(screen.queryByText("See More")).not.toBeInTheDocument();
    expect(screen.getByText(shortExplanation)).toBeInTheDocument();
  });

  test("handles sections without explanations", () => {
    const rcaWithoutExplanations: RcaRecord = {
      ...mockRca,
      sections: mockRca.sections.map((section) => ({
        ...section,
        explanation: "",
      })),
    };
    render(<RCAView rca={rcaWithoutExplanations} />);
    expect(screen.queryByText("Explanation")).not.toBeInTheDocument();
  });
});
