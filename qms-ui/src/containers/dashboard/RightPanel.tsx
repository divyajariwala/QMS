import { useEffect, useState } from 'react';
import ComplaintCard from '../../components/ComplaintCard';
import PriorityComponent from '../../components/PriorityComponent';
import { SelectChangeEvent } from '@mui/material';
import { LEVELS, MISC_SUBCAT } from '../../constants';
import { uiResults } from '../../services/api.service';
import Toast from '../../toast';
import { ComplaintDataset, ComplaintResult, UIData } from '../../types';

const MIN_UNIT = 1;

type SetCheckedType = number[] | ((value: number[]) => number[]);
type InputEvent = { target: { value: string; } };
type SelectEvent = React.ChangeEvent<HTMLInputElement>;

interface RightPanelProps {
  // Data
  complaintId: string | null;
  setComplaintId: (id: string | null) => void;
  drugName: string;
  setDrugName: (value: string) => void;
  setNarrativeText: (value: string) => void;
  complaintsDatasets: ComplaintDataset[];
  setComplaintsDatasets: (data: ComplaintDataset[]) => void;
  priority: number | null;
  htmlContent: string;
  setHtmlContent: (value: string) => void;
  summary: string;
  setSummary: (value: string) => void;
  submitInProgress: boolean;
  setSubmitInProgress: (value: boolean) => void;
  checked: number[];
  setChecked: (value: SetCheckedType) => void;
  isEdit: boolean;
  setIsEdit: (value: boolean) => void;
  isSaving: boolean;
  setIsSaving: (value: boolean) => void;
  submitted: boolean;
  setSubmitted: (value: boolean) => void;
  uiData: UIData | null;
}

/**
 * Renders the dashboard right panel.
 * In this component, the user manages the complaint result.
 *
 * @returns A react component.
 */
const RightPanel = ({
  complaintId,
  complaintsDatasets,
  setComplaintsDatasets,
  priority,
  submitInProgress,
  summary,
  checked,
  setChecked,
  isEdit,
  setIsEdit,
  isSaving,
  setIsSaving,
  submitted,
  setSubmitted,
  uiData,
}: RightPanelProps) => {
  const [errors, setErrors] = useState<number[]>([]);
  const [priorityValue, setPriorityValue] = useState<number | null>(priority);
  const [submitButtonEditMode, setSubmitButtonEditMode] = useState<boolean>(false);

  useEffect(() => {
    if (complaintsDatasets.length > 0) {
      const invalidItems: number[] = [];
      complaintsDatasets.forEach((c: ComplaintDataset, index: number) => {
        // Skip not selected items and default values.
        if (!checked.includes(index) || c?.unit_new === undefined) return;

        const unitValue = typeof c.unit_new === 'string' ? parseInt(c.unit_new) : c.unit_new;

        if (isNaN(unitValue) || unitValue < MIN_UNIT) {
          invalidItems.push(index);
        }
      });
      setErrors(invalidItems);
    }
  }, [checked, complaintsDatasets]);

  /**
   * Handles the check event.
   * This happens when the user selects an element of the result using the checkboxes.
   *
   * @param event - An SelectEvent.
   * @param id - The check element identifier (the value assigned by the position in which it is displayed in the UI).
   */
  const handleCheck = (event: SelectEvent, id: number) => {
    if (event.target.checked) {
      setChecked((prev: number[]) => [...prev, id]);
    } else {
      const data = checked.filter((ch) => ch !== id);
      setChecked(data);
      if (data.length == 0) {
        setIsEdit(false);
        setSubmitButtonEditMode(false);
      }
    }
  }

  /**
   * Handles the priority field changes.
   *
   * @param e - A SelectChangeEvent.
   */
  const handlePriorityChange = (e: SelectChangeEvent<number>) => {
    const newValue = parseInt(e.target.value as string, 10);
    setPriorityValue(newValue);
  }

  /**
   * Handles the category input changes.
   *
   * @param e - An InputEvent.
   * @param index - The category selector identifier (the value assigned by the position in which it is displayed in the UI).
   */
  const updateCategoryName = (e: InputEvent, index: number) => {
    const value = e.target.value;;
    const newComplaintdata = complaintsDatasets.map((complaint: ComplaintDataset, i: number) => {
      if (index === i) {
        complaint['category_new'] = value;

        if (value === MISC_SUBCAT) {
          complaint['level_new'] = 'N/A';
        }

        return complaint;
      }
      return complaint;
    });
    setComplaintsDatasets(newComplaintdata);
  }

  /**
   * Handles the level input changes.
   *
   * @param e - An InputEvent.
   * @param index - The level selector identifier (the value assigned by the position in which it is displayed in the UI).
   */
  const updateLevel = (e: InputEvent, index: number) => {
    const value = parseInt(e.target.value);
    const newComplaintdata = complaintsDatasets.map((complaint: ComplaintDataset, i: number) => {
      if (index === i && !isNaN(value)) {
        complaint['level_new'] = value;
        return complaint;
      }
      return complaint;
    });
    setComplaintsDatasets(newComplaintdata);
  }

  /**
   * Handles the title input changes.
   *
   * @param e - An InputEvent.
   * @param index - The title selector identifier (the value assigned by the position in which it is displayed in the UI).
   */
  const updateTitle = (e: InputEvent, index: number) => {
    const value = e.target.value;
    const newComplaintdata = complaintsDatasets.map((complaint, i) => {
      if (index == i) {
        complaint['title_new'] = value;
        return complaint;
      }
      return complaint;
    });
    setComplaintsDatasets(newComplaintdata);
  }

  /**
   * Handles the unit input changes.
   *
   * @param e - An InputEvent.
   * @param index - The unit input identifier (the value assigned by the position in which it is displayed in the UI).
   */
  const updateUnit = (e: InputEvent, index: number) => {
    const value = parseInt(e.target.value);

    const newComplaintdata = complaintsDatasets.map((complaint, i) => {
      if (index === i) {
        complaint['unit_new'] = !isNaN(value) ? value : '';
        return complaint;
      }
      return complaint;
    });
    setComplaintsDatasets(newComplaintdata);
  }

  /**
   * Handles the final result data submit.
   */
  const handleComplaintSubmit = async () => {
    const toast = new Toast();

    if (!complaintId) {
      toast.show('error', 'The complaint ID is not defined', true);
      return;
    }

    setIsEdit(false);
    setIsSaving(true);

    toast.show('info', 'Saving results...', true);

    const inputData: ComplaintResult[] = checked.map((selectedIndex: number) => {
      const complaint = complaintsDatasets.find(
        (_: ComplaintDataset, i: number) => i === selectedIndex
      );

      let unit = 1;

      if (complaint?.unit_new) {
        unit = typeof complaint?.unit_new === 'string' ? parseInt(complaint.unit_new) : complaint.unit_new;
      }

      if (complaint) {
        const scValue: string = complaint.category_new ?? complaint.category;
        const crlValue: string | null = complaint.title_new ?? complaint.title;
        const lvlValue: number | null = complaint.level_new === 'N/A'
          ? null
          : complaint.level_new === undefined
            ? complaint.level
            : complaint.level_new as number;

        return {
          model: {
            category: complaint.category,
            crl: complaint.title,
            level: complaint.level,
          },
          user: {
            category: scValue,
            crl: (crlValue === 'N/A') ? null : crlValue,
            level: lvlValue,
            unit,
          },
        };
      }
      return {};
    });

    const result = await uiResults(complaintId, inputData, priority, priorityValue);

    if (result) {
      toast.show('success', 'Results have been sent to Veeva', false, false);
    } else {
      toast.show('error', 'Results could not be sent to Veeva', false, false);
    }

    setSubmitted(true);
    setIsSaving(false);
  }

  const shouldShowSummary = summary !== '' && priorityValue === 1;
  const hasErrors = checked.length > 0 && errors.length > 0;

  /**
   * Helper - Renders the priority selector and summary.
   */
  const renderPriorityBlock = () => {
    if (priority === null) {
      return null;
    }

    return (
      <>
        <div>
          <hr className="hr-custom-line" />
        </div>

        <div className="priority">
            <PriorityComponent
              priorityValue={priorityValue ?? 0}
              handlePriorityChange={(e) => handlePriorityChange(e)}
              isChecked={checked.length > 0}
              isEdit={isEdit}
            />
        </div>

        {shouldShowSummary ? (
          <div data-testid="summary-text" className="summary">
            <div>
              <span className="title">Priority Notification Summary</span>
              <p className="text">
                {summary}
              </p>
            </div>
          </div>
        ) : null}
      </>
    );
  }

  /**
   * Helper - Renders the action button block.
   */
  const renderActionButtons = () => {
    const isEditEnabled = checked.length == 0 || isSaving || isEdit || submitted;
    const isSubmitEnabled = checked.length == 0 || isSaving || hasErrors || submitted;

    return (
      <div className="actionButtonDiv">
        {hasErrors ? (
          <div className="validation-error">
            Please update with a valid unit number.
          </div>
        ): null}
        <button
          data-testid="edit-button"
          disabled={isEditEnabled}
          onClick={() => {
            const isEditValue = checked?.length > 0 ? true : false
            setIsEdit(isEditValue);
            setSubmitButtonEditMode(isEditValue);
          }}
        >
          Edit
        </button>
        <button
          data-testid="save-button"
          disabled={isSubmitEnabled}
          onClick={handleComplaintSubmit}
        >
          {" "}
          {submitButtonEditMode ? "Save & Send" : "Agree & Send"}
        </button>
      </div>
    );
  }

  return (
    <div className="complaintsCategoriesBox">
      {complaintsDatasets?.length > 0 ? (
        <div className="complaintsCategories">

          <div className="disclamer">
            <div>
            <span className="title">Disclaimer</span>
              <p className="text">
                User must refer to applicable Common Response Language (CRL) to determine if usage criteria and product return criteria are met prior to finalizing category selection and leveling.
              </p>
            </div>
          </div>

          <h4 className="sectionTitle center">Complaints Categories</h4>

          <div className="complaint-items">
            {complaintsDatasets.map((complaint: ComplaintDataset, i: number) => (
              <ComplaintCard
                key={`complaint-${i}`}
                isSaving={isSaving}
                submitted={submitted}
                isChecked={checked.includes(i)}
                isEdit={isEdit}
                complaint={complaint}
                errors={errors.includes(i) ? { 'unit': true } : {}}
                subcategoryList={uiData?.scList ?? []}
                crlList={uiData?.crlList ?? []}
                levelList={LEVELS}
                handleCheck={(e) => handleCheck(e, i)}
                updateCategoryName={(e) => updateCategoryName(e, i)}
                updateLevel={(e) => updateLevel(e, i)}
                updateTitle={(e) => updateTitle(e, i)}
                updateUnit={(e) => updateUnit(e, i)}
              />
            ))}
          </div>

          {renderPriorityBlock()}
          {renderActionButtons()}
        </div>
      ) : (
        <div className="complaintsCategories">
          <h4 className="sectionTitle">
            {submitInProgress
              ? 'Processing...'
              : 'Please submit complaint narrative to select complaints categories'
            }
          </h4>
        </div>
      )}
    </div>
  );
}

export default RightPanel;
