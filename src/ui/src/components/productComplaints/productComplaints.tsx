import { useEffect, useState } from 'react';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import { ComplaintDataset, GetInitialDataResponse, SessionData, UIData } from '../../types';
import { useLocation } from 'react-router-dom';
import Toast from '../../toast';
import { getInitialData } from '../../services/api.service';
import Loader from '../Loader';
import {
  COMPLAINT_ID_NAME,
  COMPLAINT_SESSION_ID,
  COMPLAINT_USER_NAME,
} from '../../constants';

/**
 * Renders the dashboard component.
 *
 * @returns A react component.
 */
const ProductComplaints = () => {
  // Control
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDrugnameEditable, setIsDrugnameEditable] = useState<boolean>(false);
  const [isNarrativeEditable, setIsNarrativeEditable] = useState<boolean>(false);
  const [submitInProgress, setSubmitInProgress] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [isEdit, setIsEdit] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  // Data
  const [complaintId, setComplaintId] = useState<string | null>(null);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [drugName, setDrugName] = useState<string>('');
  const [narrativeText, setNarrativeText] = useState<string>('');
  const [complaintsDatasets, setComplaintsDatasets] = useState<ComplaintDataset[]>([]);
  const [priority, setPriority] = useState<number | null>(null);
  const [checked, setChecked] = useState<number[]>([]);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [summary, setSummary] = useState<string>('');
  const [uiData, setUiData] = useState<UIData | null>(null);

  const location = useLocation();

  /**
   * Fetch the initial data.
   * The result is stored in the local states.
   *
   * @param id - The complaint id (received from Veeva in the URL).
   * @param sessionId - The session id (received from Veeva in the URL).
   * @param userName - The user name (received from Veeva in the URL).
   */
  const getData = async (
    id: string | null,
    sessionId: string | null,
    userName: string | null,
  ) => {
    if (id) {
      setComplaintId(id);

      const toast = new Toast();
      toast.show('info', 'Fetching initial data...', true);

      const data: GetInitialDataResponse = await getInitialData(id, sessionId, userName);

      if (data) {
        setDrugName(data.drugname ?? '');
        setIsDrugnameEditable(!data.drugname);
        setNarrativeText(data.complaint_narrative ?? '');
        setIsNarrativeEditable(!data.complaint_narrative);
        setSessionData({
          session_id: data.session_id ?? null,
          user_name: data.user_name ?? null,
        });
        toast.hide();
      } else {
        toast.show('error', 'Initial data cannot be fetched', false);
      }
    } else {
      setIsDrugnameEditable(true);
      setIsNarrativeEditable(true);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const cId = queryParams.get(COMPLAINT_ID_NAME) ?? '';
    const sId = queryParams.get(COMPLAINT_SESSION_ID) ?? '';
    const user = queryParams.get(COMPLAINT_USER_NAME) ?? '';

    // Executes the initial data retrieval.
    getData(cId, sId, user);
  }, []);

  if (isLoading) {
    return (
      <>
        <div className="loaderWrapper">
          <Loader />
        </div>
      </>
    );
  }

  return (
    <>
      <div className="complaintsDashboard">
        <LeftPanel
          complaintId={complaintId}
          isDrugnameEditable={isDrugnameEditable}
          isNarrativeEditable={isNarrativeEditable}
          drugName={drugName}
          setDrugName={setDrugName}
          narrativeText={narrativeText}
          setNarrativeText={setNarrativeText}
          setComplaintId={setComplaintId}
          setComplaintsDatasets={setComplaintsDatasets}
          setPriority={setPriority}
          setHtmlContent={setHtmlContent}
          setSummary={setSummary}
          setChecked={setChecked}
          setIsEdit={setIsEdit}
          submitInProgress={submitInProgress}
          setSubmitInProgress={setSubmitInProgress}
          setSubmitted={setSubmitted}
          setUiData={setUiData}
          sessionData={sessionData}
        />
        <RightPanel
          complaintId={complaintId}
          setComplaintId={setComplaintId}
          drugName={drugName}
          setDrugName={setDrugName}
          setNarrativeText={setNarrativeText}
          complaintsDatasets={complaintsDatasets}
          setComplaintsDatasets={setComplaintsDatasets}
          priority={priority}
          htmlContent={htmlContent}
          setHtmlContent={setHtmlContent}
          summary={summary}
          setSummary={setSummary}
          submitInProgress={submitInProgress}
          setSubmitInProgress={setSubmitInProgress}
          checked={checked}
          setChecked={setChecked}
          isEdit={isEdit}
          setIsEdit={setIsEdit}
          isSaving={isSaving}
          setIsSaving={setIsSaving}
          submitted={submitted}
          setSubmitted={setSubmitted}
          uiData={uiData}
        />
      </div>
    </>
  );
};

export default ProductComplaints;
