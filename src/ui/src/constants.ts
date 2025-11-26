export const COMPLAINT_ID_NAME = 'recordId';
export const COMPLAINT_SESSION_ID = 'sessionId';
export const COMPLAINT_USER_NAME = 'userName';
export const MISC_SUBCAT = 'Miscellaneous Sub-Category';

export const DRUGNAME: { [key: string]: string } = {
  MOUNJARO: 'DEVICE MOUNJARO',
  ZEPBOUND: 'DEVICE ZEPBOUND',
  TRULICITY: 'DEVICE TRULICITY',
};

export const LEVELS: number[] = [1, 2, 3];

export const TOTAL_FILES = 3;

export const MAX_LENGTH = 1500;

export const mapped: { [key: number]: string } = {
  0: 'overdue',
  1: 'pending',
  2: 'processed'
}

export const issueList = [
  "Injection incomplete",
  "Leaking unspecified",
  "Needle bent",
  "Dose confirmation",
  "Device not working",
  "Needle not fully extended",
  "Device activated with base cap attached",
  "Device activated before placement on skin",
  "Injection button difficult to press",
  "Needle did not retract",
  "Device defective",
  "Device activated before pressing button",
  "Lack of Drug Effect",
  "Pen was used from package",
  "Needle broken",
];
