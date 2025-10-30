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