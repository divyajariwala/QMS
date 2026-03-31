export const mapScnDetailsToForm = (apiData: any) => {
  const fields = apiData?.scn_extracted_fields || {};

  return {
    status: (() => {
      const s = (fields?.status || "").toUpperCase().replace(/ /g, "_");
      if (s === "SUPPLIER_ACTION_REQUIRED") return "supplierActionRequired";
      if (s === "PENDING_REVIEW") return "pendingReview";
      if (s === "IN_REVIEW") return "inReview";
      if (s === "SUPPLIER_INFO_REQUESTED") return "supplierInfoRequested";
      if (s === "APPROVED") return "approved";
      if (s === "REJECTED") return "rejected";
      return fields?.status || "";
    })(),
    supplierRef: fields.scn_reference_number || "",
    changeTitle: fields.scn_title_summary || "",
    supplierName: fields.supplier_name || "",
    temporaryChange: fields.temporary_change_yn ? "Yes" : "No",

    currentState: fields.current_state_long_text || "",
    proposedState: fields.proposed_state_long_text || "",
    justification: fields.justification_long_text || "",

    supplierSitesAffected2: Array.isArray(fields.supplier_sites_affected)
      ? fields.supplier_sites_affected.join(", ")
      : fields.supplier_sites_affected || "",

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
    changeType: fields.change_classification_supplier || "",
    extractedFieldSources: apiData?.scn_extracted_field_sources || {},
  };
};
