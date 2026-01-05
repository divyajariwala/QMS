import { ModuleDueDateChipProps } from "./types";

export const getDueStatus = (dateStr: string): ModuleDueDateChipProps => {
  const dueDate = new Date(dateStr);
  dueDate.setDate(dueDate.getDate() + 5);
  dueDate.setHours(0, 0, 0, 0);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: "Overdue",
      label: `Overdue by ${Math.abs(diffDays)} day${
        Math.abs(diffDays) === 1 ? "" : "s"
      }`,
    };
  } else if (diffDays === 0) {
    return { type: "Today", label: "Due Today" };
  } else if (diffDays === 1) {
    return { type: "Tomorrow", label: "Due Tomorrow" };
  } else {
    return {
      type: "Due",
      label: `Due in ${diffDays} day${diffDays === 1 ? "" : "s"}`,
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