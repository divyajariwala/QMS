import { render, screen, fireEvent } from "@testing-library/react";
import RCATabs from "./RCATabs";
import { RcaRecord } from "./RCATypes";

describe("RCATabs", () => {
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
    rcas: mockRcas,
    pendingRca: null,
    selectedIndex: 0,
    onChange: jest.fn(),
    onAdd: jest.fn(),
    isSubmittedSuccessfully: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders tabs for each RCA", () => {
    render(<RCATabs {...defaultProps} />);
    expect(screen.getByRole("tab", { name: "RCA 1" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "RCA 2" })).toBeInTheDocument();
  });

  test("renders Add RCA button when not submitted successfully", () => {
    render(<RCATabs {...defaultProps} />);
    expect(screen.getByRole("button", { name: /Add RCA/ })).toBeInTheDocument();
  });

  test("does not render Add RCA button when submitted successfully", () => {
    render(<RCATabs {...defaultProps} isSubmittedSuccessfully={true} />);
    expect(
      screen.queryByRole("button", { name: /Add RCA/ })
    ).not.toBeInTheDocument();
  });

  test("renders pending RCA as tab", () => {
    const pendingRca: RcaRecord = {
      id: "pending",
      name: "RCA 3",
      sections: [],
    };
    render(<RCATabs {...defaultProps} pendingRca={pendingRca} />);
    expect(screen.getByRole("tab", { name: "RCA 3" })).toBeInTheDocument();
  });

  test("calls onChange when tab is clicked", () => {
    render(<RCATabs {...defaultProps} />);
    const tab = screen.getByRole("tab", { name: "RCA 2" });
    fireEvent.click(tab);
    expect(defaultProps.onChange).toHaveBeenCalledWith(expect.any(Object), 1);
  });

  test("calls onAdd when Add RCA button is clicked", () => {
    render(<RCATabs {...defaultProps} />);
    const addButton = screen.getByRole("button", { name: /Add RCA/ });
    fireEvent.click(addButton);
    expect(defaultProps.onAdd).toHaveBeenCalledTimes(1);
  });

  test("disables Add RCA button when more than 2 RCAs", () => {
    const threeRcas = [
      ...mockRcas,
      { id: "rca-3", name: "RCA 3", sections: [] },
    ];
    render(<RCATabs {...defaultProps} rcas={threeRcas} />);
    const addButton = screen.getByRole("button", { name: /Add RCA/ });
    expect(addButton).toBeDisabled();
  });

  test("enables Add RCA button when 2 or fewer RCAs", () => {
    render(<RCATabs {...defaultProps} />);
    const addButton = screen.getByRole("button", { name: /Add RCA/ });
    expect(addButton).not.toBeDisabled();
  });

  test("sets correct selected tab", () => {
    render(<RCATabs {...defaultProps} selectedIndex={1} />);
    const tab1 = screen.getByRole("tab", { name: "RCA 1" });
    const tab2 = screen.getByRole("tab", { name: "RCA 2" });
    expect(tab1).toHaveAttribute("aria-selected", "false");
    expect(tab2).toHaveAttribute("aria-selected", "true");
  });
});
