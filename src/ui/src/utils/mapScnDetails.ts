export const mapScnDetailsToForm = (apiData: any) => {
  const fields = apiData?.scn_extracted_fields || {};

  return {
    status: fields?.status || "",
    supplierRef: fields.scn_reference_number || "",
    changeTitle: fields.scn_title_summary || "",
    supplierName: fields.supplier_name || "",
    temporaryChange: fields.temporary_change_yn ? "Yes" : "No",

    currentState: fields.current_state_long_text || "",
    proposedState: fields.proposed_state_long_text || "",
    justification: fields.justification_long_text || "",

    supplierSitesAffected2: fields.supplier_sites_affected?.includes(
      "Manufacturing",
    )
      ? "Manufacturing"
      : "Testing",

    supplierSitesAffected: "",

    supplierContactInfo: fields.supplier_contact_information || "",

    notificationDate: fields.notification_date || "",

    changeTimingPlannedDate: fields.planned_implementation_date || "",

    firstAffectedLotBatch: fields.first_affected_lot_batch || "",

    materialNumber: fields.material_number || "",
    componentNumber: fields.component_number || "",
    materialComponentNumber:
      fields.material_number || fields.component_number || "",
    changeClassificationSupplier: fields.change_classification_supplier || "",
    createdAt: fields.created_at || "",
    attachments: apiData?.attachments || [],
  };
};
