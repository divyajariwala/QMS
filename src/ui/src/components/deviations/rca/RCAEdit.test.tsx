import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RCAEdit from "./RCAEdit";
import { RcaRecord, DropdownData } from "./RCATypes";

describe("RCAEdit", () => {
  const mockDropdownData: DropdownData = {
    Factors: [
      {
        factor_name: "Factor 1",
        ProblemCategories: [{ name: "Issue 1" }, { name: "Issue 2" }],
      },
      {
        factor_name: "Other Issues",
        ProblemCategories: [{ name: "Other Issue 1" }],
      },
    ],
    MajorRootCauseCategories: [
      {
        description: "Major 1",
        properties: {
          details: [
            {
              NearRootCauses: "Near 1",
              rootcauses: [{ name: "Root 1" }],
            },
          ],
        },
      },
    ],
  };

  const mockRca: RcaRecord = {
    id: "rca-1",
    name: "RCA 1",
    sections: [
      { key: "issues", title: "Causal factor", value: "", explanation: "" },
      {
        key: "major",
        title: "Major root cause category",
        value: "",
        explanation: "",
      },
      { key: "near", title: "Near root cause", value: "", explanation: "" },
      { key: "root", title: "Root cause", value: "", explanation: "" },
    ],
  };

  const defaultProps = {
    rca: mockRca,
    onSave: jest.fn(),
    registerOnSave: jest.fn(),
    dropdownData: mockDropdownData,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders all section titles", () => {
    render(<RCAEdit {...defaultProps} />);
    expect(screen.getByText("Causal factor")).toBeInTheDocument();
    expect(screen.getByText("Major root cause category")).toBeInTheDocument();
    expect(screen.getByText("Near root cause")).toBeInTheDocument();
    expect(screen.getByText("Root cause")).toBeInTheDocument();
  });

  test("renders issues dropdown with options", async () => {
    render(<RCAEdit {...defaultProps} />);
    const issuesSelect = screen.getAllByRole("combobox")[0];
    userEvent.click(issuesSelect);

    expect(
      await screen.findByRole("option", { name: "Issue 1" })
    ).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Issue 2" })).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Other Issue 1" })
    ).toBeInTheDocument();
  });

  test("calls registerOnSave on mount", () => {
    render(<RCAEdit {...defaultProps} />);
    expect(defaultProps.registerOnSave).toHaveBeenCalledWith(
      expect.any(Function)
    );
  });

  test("calls onSave when registered function is called", () => {
    render(<RCAEdit {...defaultProps} />);
    const saveFn = defaultProps.registerOnSave.mock.calls[0][0];
    saveFn();
    expect(defaultProps.onSave).toHaveBeenCalledWith(expect.any(Object));
  });

  test("does not render major/near/root when Other Issues is selected", () => {
    const rcaWithOther = {
      ...mockRca,
      sections: mockRca.sections.map((s) =>
        s.key === "issues" ? { ...s, value: "Other Issue 1" } : s
      ),
    };
    render(<RCAEdit {...defaultProps} rca={rcaWithOther} />);
    expect(
      screen.queryByText("Major root cause category")
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Near root cause")).not.toBeInTheDocument();
    expect(screen.queryByText("Root cause")).not.toBeInTheDocument();
  });

  test("renders major dropdown when issue is selected and not Other", () => {
    const rcaWithIssue = {
      ...mockRca,
      sections: mockRca.sections.map((s) =>
        s.key === "issues" ? { ...s, value: "Issue 1" } : s
      ),
    };
    render(<RCAEdit {...defaultProps} rca={rcaWithIssue} />);
    expect(screen.getByText("Major root cause category")).toBeInTheDocument();
  });

  test("clears dependent fields when issue changes", async () => {
    const rcaWithValues = {
      ...mockRca,
      sections: mockRca.sections.map((s) => {
        if (s.key === "issues") return { ...s, value: "Issue 1" };
        if (s.key === "major") return { ...s, value: "Major 1" };
        if (s.key === "near") return { ...s, value: "Near 1" };
        if (s.key === "root") return { ...s, value: "Root 1" };
        return s;
      }),
    };
    render(<RCAEdit {...defaultProps} rca={rcaWithValues} />);

    const issuesSelect = screen.getAllByRole("combobox")[0];
    await userEvent.click(issuesSelect);

    const issue2Option = await screen.findByRole("option", { name: "Issue 2" });
    await userEvent.click(issue2Option);

    const saveFn =
      defaultProps.registerOnSave.mock.calls[
        defaultProps.registerOnSave.mock.calls.length - 1
      ][0];
    saveFn();
    const savedRca = defaultProps.onSave.mock.calls[0][0];
    expect(savedRca.sections.find((s: any) => s.key === "major")?.value).toBe(
      ""
    );
    expect(savedRca.sections.find((s: any) => s.key === "near")?.value).toBe(
      ""
    );
    expect(savedRca.sections.find((s: any) => s.key === "root")?.value).toBe(
      ""
    );
  });

  test("handles null dropdownData", () => {
    render(<RCAEdit {...defaultProps} dropdownData={null} />);
    expect(screen.getByText("Causal factor")).toBeInTheDocument();
  });
});
