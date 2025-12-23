import React, { createContext, ReactNode, useMemo, useState } from "react";
import { usePolling, PollingConfig } from "./Polling";

type ModuleKey =
  | "complaints"
  | "deviations"
  | "adverseEvent"
  | "createNarrative"
  | "dashboard"
  | "other";

interface PollingContextType {
  pollingData: any | null;
  polling: boolean;
  error: string | null;
  done: boolean;
  falseCount: number | null;
  retryCount: number;
  idList: string[];
  setIdList: (val: string[]) => void;

  setShouldPoll: (val: boolean) => void;
  shouldPoll: boolean;

  moduleKey: ModuleKey | null;
  setModuleKey: (m: ModuleKey | null) => void;
  pollingConfig: PollingConfig<any> | null;
  setPollingConfig: (cfg: PollingConfig<any> | null) => void;
}

const PollingContext = createContext<PollingContextType | undefined>(undefined);

export const PollingProvider = ({ children }: { children: ReactNode }) => {
  const [shouldPoll, setShouldPoll] = useState(false);
  const [pollingConfig, setPollingConfig] = useState<PollingConfig<any> | null>(
    null
  );
  const [moduleKey, setModuleKey] = useState<ModuleKey | null>(null);

  const pollingState = usePolling(shouldPoll, pollingConfig);

  const value = useMemo<PollingContextType>(
    () => ({
      ...pollingState,
      setShouldPoll,
      shouldPoll,
      moduleKey,
      setModuleKey,
      pollingConfig,
      setPollingConfig,
    }),
    [pollingState, shouldPoll, moduleKey, pollingConfig]
  );

  return (
    <PollingContext.Provider value={value}>{children}</PollingContext.Provider>
  );
};

export const usePollingContext = () => {
  const context = React.useContext(PollingContext);
  if (!context) {
    throw new Error("usePollingContext must be used within PollingProvider");
  }
  return context;
};
