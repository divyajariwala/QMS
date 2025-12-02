import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Status = 'pending' | 'processed' | 'overdue';

interface StatusContextProps {
  activeStatus: Status;
  setActiveStatus: React.Dispatch<React.SetStateAction<Status>>;
}

const StatusContext = createContext<StatusContextProps | undefined>(undefined);

export const StatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [activeStatus, setActiveStatus] = useState<Status>('pending');

  return (
    <StatusContext.Provider value={{ activeStatus, setActiveStatus }}>
      {children}
    </StatusContext.Provider>
  );
};

export const useStatus = (): StatusContextProps => {
  const context = useContext(StatusContext);
  if (!context) {
    throw new Error('useStatus must be used within a StatusProvider');
  }
  return context;
};