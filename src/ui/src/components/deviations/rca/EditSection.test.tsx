import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import EditSection from "./EditSection";

describe("EditSection", () => {
  const defaultProps = {
    title: "Test Section",
    value: "Selected Value",
    options: ["Option 1", "Option 2", "Selected Value"],
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders title correctly", () => {
    render(<EditSection {...defaultProps} />);
    expect(screen.getByText("Test Section")).toBeInTheDocument();
  });

  test("renders select with correct value", () => {
    render(<EditSection {...defaultProps} />);
    expect(screen.getByText("Selected Value")).toBeInTheDocument();
  });

  test("renders all options in select", async () => {
    render(<EditSection {...defaultProps} />);
    const select = screen.getByRole("combobox");
    userEvent.click(select);

    expect(
      await screen.findByRole("option", { name: "Option 1" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Option 2" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Selected Value" })
    ).toBeInTheDocument();
  });

  test("calls onChange when select value changes", async () => {
    render(<EditSection {...defaultProps} />);
    const select = screen.getByRole("combobox");
    userEvent.click(select);

    const option = await screen.findByRole("option", { name: "Option 1" });
    userEvent.click(option);

    expect(defaultProps.onChange).toHaveBeenCalledWith("Option 1");
  });
});
