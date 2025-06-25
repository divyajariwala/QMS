import { FormControl, MenuItem, Select, TextField } from '@mui/material';
import { DRUGNAME, MISC_SUBCAT } from '../../constants';
import {
  categoryInvoke,
  fetchResults,
  invokeApi,
} from '../../services/api.service';
import Toast from '../../toast';
import {
  ComplaintDataset,
  FetchResultsResponse,
  FetchResultsResponseDatailItem,
  SessionData,
  UIData,
} from '../../types';
import { getCurrentDate } from '../../utils';

// Fetch Results control constants:
const DEFAULT_INTERVAL = 30000; // Offset between fetchResult call attemps.
const MAX_INTERVALS = 30; // Indicates the maximum number of attemps before displaying an error.

type InputEvent = { target: { value: string; } };

interface LeftPanelProps {
  // Data
  isDrugnameEditable: boolean;
  isNarrativeEditable: boolean;
  drugName: string;
  setDrugName: (value: string) => void;
  narrativeText: string;
  setNarrativeText: (value: string) => void;
  complaintId: string | null;
  setComplaintId: (id: string | null) => void;
  setComplaintsDatasets: (data: ComplaintDataset[]) => void;
  setPriority: (value: number) => void;
  setHtmlContent: (value: string) => void;
  setSummary:(value: string) => void;
  // Control
  setChecked: (value: number[]) => void;
  setIsEdit: (value: boolean) => void;
  submitInProgress: boolean;
  setSubmitInProgress: (value: boolean) => void;
  setSubmitted: (value: boolean) => void;
  setUiData: (data: UIData) => void;
  sessionData: SessionData | null;
}

/**
 * Renders the dashboard left panel.
 * In this component, the user manages the drug name and narrative fields.
 *
 * @returns A react component.
 */
const LeftPanel = ({
  isDrugnameEditable,
  isNarrativeEditable,
  drugName,
  setDrugName,
  narrativeText,
  setNarrativeText,
  complaintId,
  setComplaintId,
  setComplaintsDatasets,
  setSummary,
  setChecked,
  setIsEdit,
  submitInProgress,
  setSubmitInProgress,
  setSubmitted,
  setUiData,
  sessionData,
}: LeftPanelProps) => {

  /**
   * Handles the drug name value changes.
   *
   * @param event - An InputEvent.
   */
  const handleDrugNameChange = (event: InputEvent) => {
    setDrugName(event.target.value);
  }

  /**
   * Handles the narrative text value changes.
   *
   * @param event - An InputEvent.
   */
  const handleNarrativeChange = (event: InputEvent) => {
    setNarrativeText(event.target.value);
  }

  /**
   * Handles the narrative key down event.
   * Used only for the Ctrl/Cmd + Enter key combination.
   *
   * @param event - A KeyboardEvent.
   */
  const handleNarrativeKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      handleNarrativeSubmit();
    }
  }

  /**
   * Clean the drug name and narrative text fields.
   */
  const clearNarratives = () => {
    setDrugName('');
    setNarrativeText('');
  };

  /**
   * Handles the data submit.
   */
  const handleNarrativeSubmit = async () => {
    // Reset control vars.
    setSubmitInProgress(true);
    setChecked([]);
    setComplaintsDatasets([]);
    setSubmitted(false);
    setIsEdit(false);

    const toast = new Toast();
    toast.show('info', 'Processing the text...', true);

    const currentDate = getCurrentDate();

    // STEP 1:
    const cId = await invokeApi(
      complaintId,
      currentDate,
      drugName,
      narrativeText,
      sessionData,
    );

    if (cId) {
      toast.show('success', 'Text Processed Successfully', false);

      setComplaintId(cId);

      // STEP 2:
      await categoryInvoke(cId);

      // STEP 3:
      pollFetchResults(cId);
    } else {
      setSubmitInProgress(false);
      toast.show('error', 'Text Processing Unsuccessful', false);
    }
  };

  /**
   * Try to obtain the complaint result. If it is not possible to obtain it, wait DEFAULT_INTERVAL miliseconds and try again.
   * After MAX_INTERVALS attempts, it displays an error.
   *
   * @param complaintId - The complaint id.
   * @param interval - The interval between API calls.
   */
  const pollFetchResults = (complaintId: string, interval = DEFAULT_INTERVAL) => {
    const toast = new Toast();
    toast.show('info', 'Fetching Results...', true);

    let intervalsElapsed = 0;

    const intervalId = setInterval(async () => {
      try {
        intervalsElapsed++;
        const response: FetchResultsResponse = await fetchResults(complaintId);

        if (response) {
          toast.show('success', 'Data Fetch Successful', false);

          clearInterval(intervalId);

          const data = response.results;

          if (!data?.details) {
            throw 'No result data';
          }

          const result: ComplaintDataset[] = data.details.map((itemData: FetchResultsResponseDatailItem) => {
            return {
              title: itemData.crl_value,
              crlValue: itemData.category_confidence_score,
              category: itemData.category,
              categoryValue: itemData.category_confidence_score,
              level: (itemData.category === MISC_SUBCAT) ? null : itemData.level,
              unit_new: '',
            }
          });

          setSummary(data.summary ?? '');
          setComplaintsDatasets(result);

          setUiData({
            scList: response.csc_values, // Reported Issue dropdown.
            crlList: response.crl_values.filter((item: string) => item !== null), // CRL dropdown.
          });
        } else {
          console.log('Polling response not successful, trying again...');
        }

        if (intervalsElapsed >= MAX_INTERVALS) {
          setSubmitInProgress(false);
          clearInterval(intervalId);
          toast.show('error', 'Data Fetch Failed', false);
        }
      } catch (error) {
        console.error('Error during polling:', error);

        toast.show('error', 'Data Fetch Failed', false);

        clearInterval(intervalId);
        setSubmitInProgress(false);
      }
    }, interval);
  };

  const canSubmitNarrative = !submitInProgress
    && drugName !== ''
    && narrativeText.trim() !== '';

  /**
   * Helper - Renders the drug name selector or an static text.
   */
  const renderDrugname = () => {
    if (!isDrugnameEditable) {
      return (
        <>
          <h4 className="sectionTitle">Product Grouping</h4>

          <section className="drugNameSelector">
            {drugName}
          </section>
        </>
      );
    }

    return (
      <>
        <h4 className="sectionTitle">Select Product Grouping</h4>

        <section className="drugNameSelector">
          <FormControl className="drugNameSelectorControl" fullWidth size="small">
            <label>Product Grouping <span>*</span></label>
            <Select
              data-testid="drugname-selector"
              disabled={submitInProgress}
              className="drugNameSelect"
              value={drugName}
              onChange={handleDrugNameChange}
              displayEmpty
            >
              <MenuItem className="placeholder" disabled value="">
                Select name
              </MenuItem>
              {Object.values(DRUGNAME).map((drugname: string, index: number) => (
                <MenuItem key={`drugname-${index}`} value={drugname}>{drugname}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </section>
      </>
    );
  }

  /**
   * Helper - Renders the narrative text field or an static text.
   */
  const renderNarrative = () => {
    if (!isNarrativeEditable) {
      return (
        <>
          <h4 className="sectionTitle">Customer Complaint Narrative</h4>

          <div className="staticNarrativeBoxContent">
            {narrativeText}
          </div>
        </>
      );
    }

    return (
      <>
        <h4 className="sectionTitle">Enter Customer Complaint Narrative</h4>

        <div className="narrativeBoxContent">
          <TextField
            inputProps={{ "data-testid": "narrative-textinput" }}
            disabled={submitInProgress}
            multiline
            rows={27}
            variant="outlined"
            value={narrativeText}
            onChange={handleNarrativeChange}
            onKeyDown={handleNarrativeKeyDown}
            placeholder="Please enter your complaint narrative here..."
            fullWidth
          />
        </div>
      </>
    );
  }

  return (
    <div className="narrativeBox">
      <div className="qaSection">
        {renderDrugname()}
        {renderNarrative()}
        <div className="actionButtons">
          <>
            <button
              data-testid="reset-button"
              className="outline"
              onClick={clearNarratives}
              disabled={submitInProgress}
              hidden
            >
              Discard
            </button>
            <button
              data-testid="submit-button"
              onClick={handleNarrativeSubmit}
              disabled={!canSubmitNarrative}
            >
              Classify Complaint
            </button>
          </>
        </div>
      </div>
    </div>
  );
};

export default LeftPanel;
