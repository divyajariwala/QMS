import { render, screen, fireEvent } from "@testing-library/react";
import RCAHeader from "./RCAHeader";
import { RcaRecord } from "./RCATypes";

describe("RCAHeader", () => {
  const mockRcas: RcaRecord[] = [
    {
      id: "rca-1",
      name: "RCA 1",
      sections: [],
    },
    {
      id: "rca-2",
      name: "RCA 2",
      sections: [],
    },
  ];

  const defaultProps = {
    currentTitle: "Test RCA",
    isEditing: false,
    onEdit: jest.fn(),
    onDelete: jest.fn(),
    onCancelEdit: jest.fn(),
    onSave: jest.fn(),
    onReset: jest.fn(),
    showReset: false,
    isSubmittedSuccessfully: false,
    rcas: mockRcas,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders title correctly", () => {
    render(<RCAHeader {...defaultProps} />);
    expect(screen.getByText("Test RCA")).toBeInTheDocument();
  });

  test("renders edit and delete buttons when not editing and not submitted", () => {
    render(<RCAHeader {...defaultProps} />);
    expect(screen.getByLabelText("edit")).toBeInTheDocument();
    expect(screen.getByLabelText("delete")).toBeInTheDocument();
  });

  test("does not render delete button when only one RCA exists", () => {
    render(<RCAHeader {...defaultProps} rcas={[mockRcas[0]]} />);
    expect(screen.getByLabelText("edit")).toBeInTheDocument();
    expect(screen.queryByLabelText("delete")).not.toBeInTheDocument();
  });

  test("renders reset button when showReset is true", () => {
    render(<RCAHeader {...defaultProps} showReset={true} />);
    expect(screen.getByLabelText("restore")).toBeInTheDocument();
  });

  test("does not render action buttons when submitted successfully", () => {
    render(<RCAHeader {...defaultProps} isSubmittedSuccessfully={true} />);
    expect(screen.queryByLabelText("edit")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("delete")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("restore")).not.toBeInTheDocument();
  });

  test("renders cancel and save buttons when editing", () => {
    render(<RCAHeader {...defaultProps} isEditing={true} />);
    expect(screen.getByLabelText("cancel")).toBeInTheDocument();
    expect(screen.getByLabelText("save")).toBeInTheDocument();
  });

  test("does not render action buttons when editing", () => {
    render(<RCAHeader {...defaultProps} isEditing={true} />);
    expect(screen.queryByLabelText("edit")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("delete")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("restore")).not.toBeInTheDocument();
  });

  test("calls onEdit when edit button is clicked", () => {
    render(<RCAHeader {...defaultProps} />);
    fireEvent.click(screen.getByLabelText("edit"));
    expect(defaultProps.onEdit).toHaveBeenCalledTimes(1);
  });

  test("calls onDelete when delete button is clicked", () => {
    render(<RCAHeader {...defaultProps} />);
    fireEvent.click(screen.getByLabelText("delete"));
    expect(defaultProps.onDelete).toHaveBeenCalledTimes(1);
  });

  test("calls onReset when reset button is clicked", () => {
    render(<RCAHeader {...defaultProps} showReset={true} />);
    fireEvent.click(screen.getByLabelText("restore"));
    expect(defaultProps.onReset).toHaveBeenCalledTimes(1);
  });

  test("calls onCancelEdit when cancel button is clicked", () => {
    render(<RCAHeader {...defaultProps} isEditing={true} />);
    fireEvent.click(screen.getByLabelText("cancel"));
    expect(defaultProps.onCancelEdit).toHaveBeenCalledTimes(1);
  });

  test("calls onSave when save button is clicked", () => {
    render(<RCAHeader {...defaultProps} isEditing={true} />);
    fireEvent.click(screen.getByLabelText("save"));
    expect(defaultProps.onSave).toHaveBeenCalledTimes(1);
  });
});
