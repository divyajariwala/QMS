// ExecutiveSummary.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ExecutiveSummary, { ExecutiveSummaryProps } from "./ExecutiveSummary";

// Mock static assets & styles
jest.mock("../../../assets/icons/leftArrow.svg", () => "leftArrow");
jest.mock("../../../assets/icons/aiSummary.svg", () => "aiSummary");
jest.mock(
  "./executiveSummary.module.scss",
  () => new Proxy({}, { get: () => "" })
);

// Mock TinyMCE Editor to a simple textarea
jest.mock("@tinymce/tinymce-react", () => ({
  Editor: (props: any) => {
    const { id, initialValue, onEditorChange, disabled } = props;
    return (
      <textarea
        data-testid={id || "exec-editor"}
        defaultValue={initialValue}
        disabled={!!disabled}
        onChange={(e) => onEditorChange?.(e.target.value)}
      />
    );
  },
}));

const baseItems = [
  { label: "Title", content: "Deviation ABC - QA Oversight Gap" },
  { label: "Overview", content: "Description of deviation with context." },
  { label: "Immediate Actions", content: "Steps taken immediately." },
];

const renderComp = (overrides?: Partial<ExecutiveSummaryProps>) => {
  const props: ExecutiveSummaryProps = {
    items: baseItems,
    onBack: jest.fn(),
    onPrimaryAction: jest.fn(),
    disabled: false,
    ...overrides,
  };
  const utils = render(<ExecutiveSummary {...props} />);
  return { props, utils };
};

describe("ExecutiveSummary", () => {
  test("renders with items, allows editing, back and primary action", async () => {
    const { props } = renderComp();

    // Title and icon present
    expect(
      screen.getByText(/AI Generated Executive Summary/i)
    ).toBeInTheDocument();

    // Back arrow visible when not disabled
    const backIcon = screen.getByAltText("left arrow");
    expect(backIcon).toBeInTheDocument();

    // Editors render with initial content
    baseItems.forEach((item, idx) => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
      const editor = screen.getByTestId(`exec-summary-editor-${idx}`);
      expect(editor).toBeInTheDocument();
      expect((editor as HTMLTextAreaElement).value).toBe(item.content);
    });

    const firstEditor = screen.getByTestId("exec-summary-editor-0");
    fireEvent.change(firstEditor, {
      target: { value: "Updated Title Content" },
    });

    // Save and send
    const saveBtn = screen.getByRole("button", {
      name: /Save and Send to QMS/i,
    });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(props.onPrimaryAction).toHaveBeenCalledTimes(1);
    });

    const payload = (props.onPrimaryAction as jest.Mock).mock.calls[0][0];
    expect(payload).toEqual([
      { label: "Title", content: "Updated Title Content" },
      { label: "Overview", content: "Description of deviation with context." },
      { label: "Immediate Actions", content: "Steps taken immediately." },
    ]);

    // Back click should call onBack
    fireEvent.click(backIcon);
    expect(props.onBack).toHaveBeenCalledTimes(1);
  });

  test("disabled view hides back and primary action; editors are disabled", () => {
    renderComp({ disabled: true });

    // No back icon when disabled
    expect(screen.queryByAltText("left arrow")).not.toBeInTheDocument();

    // No primary action button
    expect(
      screen.queryByRole("button", { name: /Save and Send to Qms/i })
    ).not.toBeInTheDocument();

    // Editors disabled
    const editors = [
      screen.getByTestId("exec-summary-editor-0"),
      screen.getByTestId("exec-summary-editor-1"),
      screen.getByTestId("exec-summary-editor-2"),
    ];
    editors.forEach((ed) => {
      expect(ed).toBeDisabled();
    });
  });

  test("updates local state when items prop changes", () => {
    const { utils } = renderComp();

    const firstEditor = screen.getByTestId("exec-summary-editor-0");
    fireEvent.change(firstEditor, {
      target: { value: "Locally changed Title" },
    });
    expect((firstEditor as HTMLTextAreaElement).value).toBe(
      "Locally changed Title"
    );

    const newItems = [
      { label: "Title", content: "New Title from Props" },
      { label: "Overview", content: "New Overview from Props" },
      { label: "Immediate Actions", content: "New Actions from Props" },
    ];
    utils.rerender(
      <ExecutiveSummary
        items={newItems}
        onBack={() => {}}
        onPrimaryAction={() => {}}
        disabled={false}
      />
    );

    const updatedFirstEditor = screen.getByTestId("exec-summary-editor-0");
    expect((updatedFirstEditor as HTMLTextAreaElement).value).toBe(
      "New Title from Props"
    );
  });

  test("renders empty state when no items", () => {
    renderComp({ items: [], onPrimaryAction: undefined });

    expect(screen.getByText(/No summary available/i)).toBeInTheDocument();
    expect(
      screen.queryByTestId("exec-summary-editor-0")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Save and Send to QMS/i })
    ).not.toBeInTheDocument();
  });
});
