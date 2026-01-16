-- Files Table
CREATE TABLE files (
    file_id UUID PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    s3_url VARCHAR(500) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by VARCHAR(100)
);

-- Create sequences for auto-incrementing IDs
CREATE SEQUENCE complaint_id_seq START 1;
CREATE SEQUENCE inference_results_inference_id_seq START 1;
CREATE SEQUENCE audit_id_seq START 1;
CREATE SEQUENCE workflow_id_seq START 1;
CREATE SEQUENCE deviation_workflow_id_seq START 1;
CREATE SEQUENCE deviation_audit_id_seq START 1;

-- Modified Complaints Table with CAS-XXXXX format
CREATE TABLE complaints (
    complaint_id VARCHAR(20) PRIMARY KEY DEFAULT 'CAS-' || LPAD(nextval('complaint_id_seq')::text, 5, '0'),
    file_id UUID REFERENCES files(file_id),
    narrative TEXT,
    narrative_summary TEXT,
    receipt_date DATE,
    primary_reporter VARCHAR(255),
    primary_reporter_address VARCHAR(500),
    patient_name VARCHAR(255),
    physician VARCHAR(255),
    drug VARCHAR(255),
    lot_no VARCHAR(100),
    dosage VARCHAR(100),
    expiration_date DATE,
    part_number VARCHAR(100),
    criticality VARCHAR(50),
    case_type VARCHAR(50),
    report_type VARCHAR(50),
    category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Overdue', 'Processed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text_extracted BOOLEAN DEFAULT FALSE
);

-- Inference Results Table
CREATE TABLE inference_results (
    inference_id INTEGER PRIMARY KEY DEFAULT nextval('inference_results_inference_id_seq'),
    complaint_id VARCHAR(20) NOT NULL REFERENCES complaints(complaint_id),
    levels JSONB NOT NULL,
    subcategories JSONB NOT NULL,
    crl_codes JSONB,
    final_level VARCHAR(10),
    priority INTEGER NOT NULL DEFAULT 0,
    units INTEGER DEFAULT 0,
    priority_reason TEXT,
    priority_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Unified Audit Table
CREATE TABLE unified_audit (
    audit_id VARCHAR(20) PRIMARY KEY DEFAULT 'AUD-' || LPAD(nextval('audit_id_seq')::text, 5, '0'),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('Complaint', 'Inference', 'CategoryDetail')),
    entity_id VARCHAR(20) NOT NULL,
    changed_field VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_flag BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100)
);
-- Deviation Unified Audit Table
CREATE TABLE deviation_field_audit (
    audit_id VARCHAR(20) PRIMARY KEY
        DEFAULT 'DAUD-' || LPAD(nextval('deviation_audit_id_seq')::text, 5, '0'),

    entity_type VARCHAR(20) NOT NULL
        CHECK (entity_type IN ('RCA', 'Grading')),

    deviation_id VARCHAR(20) NOT NULL,
    audit_type VARCHAR(10) NOT NULL
    new_fields JSONB NOT NULL,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Logs
CREATE TABLE workflow_logs (
    log_id VARCHAR(20) PRIMARY KEY DEFAULT 'WFL-' || LPAD(nextval('workflow_id_seq')::text, 5, '0'),
    complaint_id VARCHAR(20) NOT NULL,
    step VARCHAR(100),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    input JSONB,
    output JSONB
);

-- Deviation Workflow Logs
CREATE TABLE deviation_workflow_logs (
    log_id VARCHAR(20) PRIMARY KEY
        DEFAULT 'DWL-' || LPAD(nextval('deviation_workflow_id_seq')::text, 5, '0'),

    deviation_id VARCHAR(20) NOT NULL
        REFERENCES deviations(deviation_id),

    step VARCHAR(100),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    input JSONB,
    output JSONB
);

-- Processed Complaints Table
CREATE TABLE processed_complaints (
    complaint_id VARCHAR(20) PRIMARY KEY REFERENCES complaints(complaint_id),
    approved_at TIMESTAMP,
    approved_by VARCHAR(100),
    approved_category_details JSONB,
    final_label VARCHAR(255),
    final_category VARCHAR(100)
);

-- Case Stats Table
CREATE TABLE case_stats (
    stat_name VARCHAR(50) PRIMARY KEY,
    stat_value INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize case stats
INSERT INTO case_stats (stat_name, stat_value) VALUES 
('Pending', 0),
('Processed', 0),
('Overdue', 0),
('Avg Time', 0);

-- Label List Table
CREATE TABLE label_list (
    label VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize label list
INSERT INTO label_list (label) VALUES 
('Injection incomplete'),
('Leaking unspecified'),
('Needle bent'),
('Dose confirmation'),
('Device not working'),
('Needle not fully extended'),
('Device activated with base cap attached'),
('Device activated before placement on skin'),
('Injection button difficult to press'),
('Needle did not retract'),
('Device defective'),
('Device activated before pressing button'),
('Lack of Drug Effect'),
('Pen was used from package'),
('Needle broken'),
('Miscellaneous Sub-Category'),
('Injection incomplete - Autoinjector/Syringe')
ON CONFLICT (label) DO NOTHING;

-- Procedure to update overdue complaints and case stats counts
CREATE OR REPLACE FUNCTION update_complaints_and_stats()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- Update overdue complaints
    UPDATE complaints 
    SET status = 'Overdue'
    WHERE status = 'Pending' 
    AND created_at < NOW() - INTERVAL '5 days';
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    -- Update case stats counts
    UPDATE case_stats SET stat_value = (SELECT COUNT(*) FROM complaints WHERE status = 'Pending'), updated_at = CURRENT_TIMESTAMP WHERE stat_name = 'Pending';
    UPDATE case_stats SET stat_value = (SELECT COUNT(*) FROM complaints WHERE status = 'Processed'), updated_at = CURRENT_TIMESTAMP WHERE stat_name = 'Processed';
    UPDATE case_stats SET stat_value = (SELECT COUNT(*) FROM complaints WHERE status = 'Overdue'), updated_at = CURRENT_TIMESTAMP WHERE stat_name = 'Overdue';
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

------- rca_approved average time -------
CREATE OR REPLACE FUNCTION approved_avg_cycle_time()
RETURNS void AS $$
BEGIN
    UPDATE deviations_case_stats
    SET
        stat_value = COALESCE((
            SELECT ROUND(
                AVG(
                    CASE
                        WHEN EXTRACT(EPOCH FROM (d.grading_approved_date - d.created_at))/86400 < 1 THEN 1
                        ELSE EXTRACT(EPOCH FROM (d.grading_approved_date - d.created_at))/86400
                    END
                )
            )::INTEGER
            FROM deviations d
            WHERE d.grading_approved_date IS NOT NULL
        ), 0),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'avg_cycle_time';
END;
$$ LANGUAGE plpgsql;

-- Procedure to calculate average cycle time
CREATE OR REPLACE FUNCTION update_avg_cycle_time()
RETURNS void AS $$
BEGIN
    UPDATE case_stats SET 
        stat_value = COALESCE((
            SELECT ROUND(AVG(
                CASE 
                    WHEN EXTRACT(EPOCH FROM (pc.approved_at - c.created_at))/86400 < 1 THEN 1
                    ELSE EXTRACT(EPOCH FROM (pc.approved_at - c.created_at))/86400
                END
            ))::INTEGER
            FROM processed_complaints pc 
            JOIN complaints c ON pc.complaint_id = c.complaint_id
        ), 0),
        updated_at = CURRENT_TIMESTAMP 
    WHERE stat_name = 'Avg Time';
END;
$$ LANGUAGE plpgsql;

-- Indexes for performance
CREATE INDEX idx_complaints_file_id ON complaints(file_id);
CREATE INDEX idx_complaints_status_created ON complaints(status, created_at);
CREATE INDEX idx_inference_results_complaint_id ON inference_results(complaint_id);
CREATE INDEX idx_audit_entity ON unified_audit(entity_type, entity_id);
CREATE INDEX idx_workflow_complaint_id ON workflow_logs(complaint_id);


-- Deviations Module Tables

-- Create sequence for deviations auto-incrementing IDs
CREATE SEQUENCE deviation_id_seq START 1;

-- Deviation Files Table (similar to files table)
CREATE TABLE deviation_files (
    file_id UUID PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    s3_url VARCHAR(500) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by VARCHAR(100)
);

CREATE OR REPLACE FUNCTION update_deviations_and_stats()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- -------------------------------------------------
    -- Update overdue complaints
    -- -------------------------------------------------
    UPDATE deviations
    SET deviation_status = 'Overdue'
    WHERE deviation_status = 'Pending'
      AND created_at < NOW() - INTERVAL '5 days';

    GET DIAGNOSTICS updated_count = ROW_COUNT;

    -- -------------------------------------------------
    -- Update pending stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE deviation_status = 'Pending'
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'Pending';

    -- -------------------------------------------------
    -- Update processed stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE deviation_status = 'Processed'
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'Processed';

    -- -------------------------------------------------
    -- Update overdue stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE deviation_status = 'Overdue'
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'Overdue';

    -- -------------------------------------------------
    -- Update RCA pending stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE rca_approved = false
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'rca_pending';

    -- -------------------------------------------------
    -- Update RCA done stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE rca_approved = true
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'rca_done';

    -- -------------------------------------------------
    -- Update grading pending stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE grading_completed = false
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'grading_pending';

    -- -------------------------------------------------
    -- NEW: Update grading done stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE grading_completed = true
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'grading_done';

    -- -------------------------------------------------
    -- NEW: Update workflow progress stats count
    -- -------------------------------------------------
    UPDATE deviations_case_stats
    SET stat_value = (
            SELECT COUNT(*)
            FROM deviations
            WHERE rca_generated = true
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE stat_name = 'workflow_progress';

    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Deviations Table with DV-XXXXX format
CREATE TABLE deviations (
    deviation_id VARCHAR(20) PRIMARY KEY DEFAULT 'DV-' || LPAD(nextval('deviation_id_seq')::text, 5, '0'),
    file_id UUID REFERENCES deviation_files(file_id),
    title TEXT,
    description TEXT,
    immediate_steps_taken TEXT,
    quality_risk_evaluation TEXT,
    investigation_summary TEXT,
    capa_plan TEXT,
    recurrence_check_details TEXT,
    effectiveness_check_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text_extracted BOOLEAN DEFAULT FALSE,
    rca_generated BOOLEAN DEFAULT FALSE,
    rca_approved BOOLEAN DEFAULT FALSE,
    grading_completed BOOLEAN DEFAULT FALSE,
    deviation_status VARCHAR(20) DEFAULT 'Pending' CHECK (deviation_status IN ('Pending', 'Overdue', 'Processed'))
);

-- Indexes for performance
CREATE INDEX idx_deviations_file_id ON deviations(file_id);
CREATE INDEX idx_deviation_files_upload_time ON deviation_files(upload_time);


-- Adverse Events Table (replica of complaints table)
CREATE TABLE adverse_events (
    complaint_id VARCHAR(20) PRIMARY KEY,
    file_id UUID REFERENCES files(file_id),
    narrative TEXT,
    narrative_summary TEXT,
    receipt_date DATE,
    primary_reporter VARCHAR(255),
    primary_reporter_address VARCHAR(500),
    patient_name VARCHAR(255),
    physician VARCHAR(255),
    drug VARCHAR(255),
    lot_no VARCHAR(100),
    dosage VARCHAR(100),
    expiration_date DATE,
    part_number VARCHAR(100),
    criticality VARCHAR(50),
    case_type VARCHAR(50),
    report_type VARCHAR(50),
    category VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Overdue', 'Processed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text_extracted BOOLEAN DEFAULT FALSE
);

-- Index for performance
CREATE INDEX idx_adverse_events_file_id ON adverse_events(file_id);
CREATE INDEX idx_adverse_events_status_created ON adverse_events(status, created_at);
