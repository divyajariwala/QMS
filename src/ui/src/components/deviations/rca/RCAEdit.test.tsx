import { render, screen, fireEvent, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RCAEdit from "./RCAEdit";
import { RcaRecord, DropdownData } from "./RCATypes";

const mockDropdownData: DropdownData = {
  Factors: [
    {
      factor_name: "Factor 1",
      ProblemCategories: [{ name: "Issue 1" }, { name: "Issue 2" }],
    },
    {
      factor_name: "Other Issues",
      ProblemCategories: [{ name: "Other Issue 1" }, { name: "Other Issue 2" }],
    },
  ],
  MajorRootCauseCategories: [
    {
      description: "Major 1",
      properties: {
        details: [
          {
            NearRootCauses: "Near 1",
            rootcauses: [{ name: "Root 1" }, { name: "Root 2" }],
          },
          {
            NearRootCauses: "Near 2",
            rootcauses: [{ name: "Root 3" }],
          },
        ],
      },
    },
    {
      description: "Major 2",
      properties: {
        details: [
          {
            NearRootCauses: "Near 3",
            rootcauses: [{ name: "Root 4" }],
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
    {
      key: "issues",
      title: "Problem category",
      value: "",
      explanation: "",
    },
    {
      key: "major",
      title: "Major root cause category",
      value: "",
      explanation: "",
    },
    {
      key: "near",
      title: "Near root cause",
      value: "",
      explanation: "",
    },
    {
      key: "root",
      title: "Root cause",
      value: "",
      explanation: "",
    },
  ],
  meta: {
    createdFrom: "seed",
    createdAt: new Date().toISOString(),
    isEdited: false,
  },
};

describe("RCAEdit", () => {
  const mockOnSave = jest.fn();
  const mockRegisterOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders all sections when not other issue", () => {
    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    expect(screen.getByText("Major root cause category")).toBeInTheDocument();
    expect(screen.getByText("Near root cause")).toBeInTheDocument();
    expect(screen.getByText("Root cause")).toBeInTheDocument();
  });

  test("hides major, near, root sections when other issue is selected", () => {
    const rcaWithOther = {
      ...mockRca,
      sections: mockRca.sections.map((s) =>
        s.key === "issues" ? { ...s, value: "Other Issue 1" } : s
      ),
    };

    render(
      <RCAEdit
        rca={rcaWithOther}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    expect(
      screen.queryByText("Major root cause category")
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Near root cause")).not.toBeInTheDocument();
    expect(screen.queryByText("Root cause")).not.toBeInTheDocument();
  });

  test("calls registerOnSave on mount", () => {
    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    expect(mockRegisterOnSave).toHaveBeenCalledWith(expect.any(Function));
  });

  test("updates draft when value changes", async () => {
    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );
    const selects = screen.getAllByRole("combobox");
    expect(selects.length).toBeGreaterThan(0);
    fireEvent.mouseDown(selects[0]);
    const listbox = screen.getByRole("listbox");
    await userEvent.click(within(listbox).getByText("Issue 1"));

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    expect(mockOnSave).toHaveBeenCalled();
    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[0].value).toBe("Issue 1");
  });

  test("clears dependent fields when issue changes", async () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "Major 1",
          explanation: "",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "Near 1",
          explanation: "",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "Root 1",
          explanation: "",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    const selects = screen.getAllByRole("combobox");

    fireEvent.mouseDown(selects[0]); // open MUI Select
    const listbox = within(document.body).getByRole("listbox"); // MUI renders in a portal
    await userEvent.click(within(listbox).getByText("Issue 2"));
    fireEvent.keyDown(selects[0], { key: "Escape" }); // close the select to commit

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[0].value).toBe("Issue 2");
    expect(savedRca.sections[1].value).toBe(""); // major cleared
    expect(savedRca.sections[2].value).toBe(""); // near cleared
    expect(savedRca.sections[3].value).toBe(""); // root cleared
  });

  test("clears near and root when major changes", async () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "Major 1",
          explanation: "",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "Near 1",
          explanation: "",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "Root 1",
          explanation: "",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    const selects = screen.getAllByRole("combobox");

    fireEvent.mouseDown(selects[1]); // open MUI Select for "Major root cause category"
    const listbox = within(document.body).getByRole("listbox"); // MUI uses portal
    await userEvent.click(within(listbox).getByText("Major 2"));
    fireEvent.keyDown(selects[1], { key: "Escape" }); // close and commit selection

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[1].value).toBe("Major 2");
    expect(savedRca.sections[2].value).toBe(""); // near cleared
    expect(savedRca.sections[3].value).toBe(""); // root cleared
  });

  test("clears root when near changes", async () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "Major 1",
          explanation: "",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "Near 1",
          explanation: "",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "Root 1",
          explanation: "",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    const selects = screen.getAllByRole("combobox");

    fireEvent.mouseDown(selects[2]); // open MUI Select for "Near root cause"
    const listbox = within(document.body).getByRole("listbox"); // MUI renders via portal
    await userEvent.click(within(listbox).getByText("Near 2"));
    fireEvent.keyDown(selects[2], { key: "Escape" }); // close to commit

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[2].value).toBe("Near 2");
    expect(savedRca.sections[3].value).toBe(""); // root cleared
  });

  test("handles null dropdownData", () => {
    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={null}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    // Should not crash
  });

  test("handles empty dropdownData", () => {
    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={{ Factors: [], MajorRootCauseCategories: [] }}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    // Should not crash with empty arrays
  });

  test("renders sections with pre-filled values", () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "Some explanation",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "Major 1",
          explanation: "Major explanation",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "Near 1",
          explanation: "Near explanation",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "Root 1",
          explanation: "Root explanation",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    expect(screen.getByText("Major root cause category")).toBeInTheDocument();
    expect(screen.getByText("Near root cause")).toBeInTheDocument();
    expect(screen.getByText("Root cause")).toBeInTheDocument();
  });

  test("clears explanation when value changes", async () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "Original explanation",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "",
          explanation: "",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "",
          explanation: "",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "",
          explanation: "",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    const selects = screen.getAllByRole("combobox");
    fireEvent.mouseDown(selects[0]); // open MUI Select
    const listbox = within(document.body).getByRole("listbox"); // MUI renders options in a portal
    await userEvent.click(within(listbox).getByText("Issue 2"));
    fireEvent.keyDown(selects[0], { key: "Escape" }); // close to commit selection

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[0].value).toBe("Issue 2");
    expect(savedRca.sections[0].explanation).toBe(""); // explanation cleared
  });

  test("does not clear explanation when value stays the same", async () => {
    const rcaWithValues: RcaRecord = {
      ...mockRca,
      sections: [
        {
          key: "issues" as const,
          title: "Problem category",
          value: "Issue 1",
          explanation: "Original explanation",
        },
        {
          key: "major" as const,
          title: "Major root cause category",
          value: "",
          explanation: "",
        },
        {
          key: "near" as const,
          title: "Near root cause",
          value: "",
          explanation: "",
        },
        {
          key: "root" as const,
          title: "Root cause",
          value: "",
          explanation: "",
        },
      ],
    };

    render(
      <RCAEdit
        rca={rcaWithValues}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={mockDropdownData}
      />
    );

    const selects = screen.getAllByRole("combobox");

    fireEvent.mouseDown(selects[0]); // open MUI Select
    const listbox = within(document.body).getByRole("listbox"); // MUI renders options in a portal
    await userEvent.click(within(listbox).getByText("Issue 1")); // choose the same value
    fireEvent.keyDown(selects[0], { key: "Escape" }); // close to commit

    const saveFn = mockRegisterOnSave.mock.calls.at(-1)[0];
    await saveFn();

    const savedRca = mockOnSave.mock.calls[0][0];
    expect(savedRca.sections[0].value).toBe("Issue 1");
    expect(savedRca.sections[0].explanation).toBe("Original explanation"); // explanation preserved
  });

  test("handles missing properties in dropdownData", () => {
    const incompleteDropdownData: DropdownData = {
      Factors: [
        {
          factor_name: "Factor 1",
          ProblemCategories: [{ name: "Issue 1" }],
        },
      ],
      MajorRootCauseCategories: [
        {
          description: "Major 1",
          // missing properties
        },
      ],
    };

    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={incompleteDropdownData}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
    // Should not crash with missing properties
  });

  test("handles undefined names in dropdownData", () => {
    const dropdownDataWithUndefined: DropdownData = {
      Factors: [
        {
          factor_name: "Factor 1",
          ProblemCategories: [{ name: undefined }, { name: "Issue 1" }],
        },
      ],
      MajorRootCauseCategories: [
        {
          description: "Major 1",
          properties: {
            details: [
              {
                NearRootCauses: "Near 1",
                rootcauses: [{ name: undefined }, { name: "Root 1" }],
              },
            ],
          },
        },
      ],
    };

    render(
      <RCAEdit
        rca={mockRca}
        onSave={mockOnSave}
        registerOnSave={mockRegisterOnSave}
        dropdownData={dropdownDataWithUndefined}
      />
    );

    expect(screen.getByText("Problem category")).toBeInTheDocument();
  });
});
