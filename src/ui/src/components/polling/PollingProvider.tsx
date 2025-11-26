import React, { createContext, ReactNode, useState } from "react";
import { usePolling } from "./Polling"; // your hook
import { getComplaintsApiResponse } from "src/types";

interface PollingContextType {
  pollingData: getComplaintsApiResponse | null;
  polling: boolean;
  error: string | null;
  done: boolean;
  falseCount: number | null;
  retryCount: number;
  setShouldPoll: (val: boolean) => void; // expose setter for controlling polling from outside
  shouldPoll: boolean; // expose current polling on/off state
  idList: string[];
  setIdList: (val: string[]) => void;
}

const PollingContext = createContext<PollingContextType | undefined>(undefined);

export const PollingProvider = ({ children }: { children: ReactNode }) => {
  // Manage the polling state here
  const [shouldPoll, setShouldPoll] = useState(false);

  // Pass the current polling state to your hook so it starts/stops accordingly
  const pollingState = usePolling(shouldPoll);

  // Pass setShouldPoll to allow consumers to toggle polling
  return (
    <PollingContext.Provider value={{ ...pollingState, setShouldPoll, shouldPoll }}>
      {children}
    </PollingContext.Provider>
  );
};

export const usePollingContext = () => {
  const context = React.useContext(PollingContext);
  if (!context) {
    throw new Error("usePollingContext must be used within PollingProvider");
  }
  return context;
};