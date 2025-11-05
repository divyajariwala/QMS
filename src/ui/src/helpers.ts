import { ComplaintsDueDateChipProps } from "./types";

export const getDueStatus = (
  dateStr: string
): ComplaintsDueDateChipProps => {
  const dueDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffTime = dueDate.getTime() - today.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: "Overdue",
      label: `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) === 1 ? "" : "s"}`,
    };
  } else if (diffDays === 0) {
    return { type: "Today", label: "Due Today" };
  } else if (diffDays === 1) {
    return { type: "Tomorrow", label: "Due Tomorrow" };
  } else {
    const formattedDate = dueDate
      .toLocaleDateString("en-US", { year: "numeric", month: "short", day: "2-digit" })
      .replace(/,/g, "");
    return { type: "Due", label: `Due on ${formattedDate}` };
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

export function formatHoursToDays(hours: number | undefined): string {
  const days = hours !== undefined ? Math.floor(hours / 24) : 0;
  const remainingHours = hours !== undefined ? hours % 24 : 0;

  const dayStr = days > 0 ? `${days} day${days > 1 ? "s" : ""}` : "";
  const hourStr = remainingHours > 0 ? `${remainingHours} hr${remainingHours > 1 ? "s" : ""}` : "";

  return [dayStr, hourStr].filter(Boolean).join(" ");
}