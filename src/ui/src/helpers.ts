import { ComplaintsDueDateChipProps } from "./types";

export const getDueStatus = (
  dateStr: string
): ComplaintsDueDateChipProps => {
  if (!dateStr) {
    return { type: "NA", label: "NA" };
  }

  const inputDate = new Date(dateStr);
  if (isNaN(inputDate.getTime())) {
    return { type: "NA", label: "NA" };
  }

  // Set due date to 5 days from inputDate
  const dueDate = new Date(inputDate);
  dueDate.setDate(dueDate.getDate() + 5);
  dueDate.setHours(0, 0, 0, 0);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays > 0) {
    return {
      type: "Due",
      label: `Due in ${diffDays} day${diffDays === 1 ? "" : "s"}`
    };
  } else if (diffDays === 0) {
    return { type: "Today", label: "Due Today" };
  } else {
    const overdueDays = Math.abs(diffDays);
    return {
      type: "Overdue",
      label: `Overdue by ${overdueDays} day${overdueDays === 1 ? "" : "s"}`
    };
  }
};

export const calculateOverdueDays = (dateStr: string): number => {
  const givenDate = new Date(dateStr);
  const today = new Date();
  givenDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  const diffMs = today.getTime() - givenDate.getTime();

  if (diffMs <= 0) return 0;
  const overdueDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  return overdueDays;
}

export function formatDays(days: number | undefined): string {
  if (days === undefined || days <= 0) {
    return "0 day";
  }
  
  return `${days} day${days > 1 ? "s" : ""}`;
}