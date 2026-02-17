export const mapScnFormToApi = (formData: any) => {
  const payload: Record<string, any> = {};

  if (formData.supplierName) payload.supplier_name = formData.supplierName;

  if (formData.changeTitle) payload.scn_title_summary = formData.changeTitle;

  if (formData.currentState)
    payload.current_state_long_text = formData.currentState;

  if (formData.proposedState)
    payload.proposed_state_long_text = formData.proposedState;

  if (formData.justification)
    payload.justification_long_text = formData.justification;

  if (formData.temporaryChange)
    payload.temporary_change_yn = formData.temporaryChange === "Yes";

  if (formData.notificationDate)
    payload.notification_date = formData.notificationDate;

  if (formData.changeTimingPlannedDate)
    payload.planned_implementation_date = formData.changeTimingPlannedDate;

  if (formData.materialNumber)
    payload.material_number = formData.materialNumber;

  if (formData.componentNumber)
    payload.component_number = formData.componentNumber;

  if (formData.firstAffectedLotBatch)
    payload.first_affected_lot_batch = formData.firstAffectedLotBatch;

  if (formData.supplierContactInfo)
    payload.supplier_contact_information = formData.supplierContactInfo;

  if (formData.supplierSitesAffected2)
    payload.supplier_sites_affected = [formData.supplierSitesAffected2];

  return payload;
};
