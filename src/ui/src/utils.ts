/**
 * Retrieves the current date.
 *
 * @returns The current date as string. Format: YYYY-MM-DD
 */
export const getCurrentDate = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export const formatDateMMM_D_YYYY = (dateStr: string) => {
  const date = new Date(dateStr);
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const monthAbbr = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();

  return `${monthAbbr} ${day} ${year}`;
}