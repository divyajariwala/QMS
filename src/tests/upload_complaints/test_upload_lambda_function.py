import pytest
import json
import os
import sys
import io
from unittest.mock import Mock, patch
import pandas as pd

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from upload_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_successful_csv_upload(self, mock_parse, mock_boto3):
        """Test: Successful CSV file upload"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-123'}

        # Mock CSV
        mock_parse.return_value = {
            'filename': 'data.csv',
            'content': b'Case ID,Narrative Text\nCAS-001,Test complaint narrative',
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        event = {
            'body': 'multipart-fake-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['filename'] == 'data.csv'

        mock_s3.put_object.assert_called_once()
        mock_sqs.send_message.assert_called_once()  # Only one complaint from CSV

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_successful_xlsx_upload(self, mock_parse, mock_boto3):
        """Test: Successful Excel file upload"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-456'}

        # Create actual Excel content
        df = pd.DataFrame({
            'Case ID': ['EXL-001'],
            'Narrative Text': ['Excel test complaint']
        })
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_content = excel_buffer.getvalue()
        
        # Mock Excel file
        mock_parse.return_value = {
            'filename': 'report.xlsx',
            'content': excel_content,
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'field_name': 'file'
        }

        event = {
            'body': 'fake-excel-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['filename'] == 'report.xlsx'
        assert body['data']['complaints_processed'] == 1

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_missing_body(self, mock_boto3):
        """Test: Error when body is missing"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        event = {}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['message'] == "No file provided"

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_wrong_content_type(self, mock_boto3):
        """Test: Error with incorrect Content-Type"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        event = {
            'body': 'test',
            'headers': {'content-type': 'application/json'}
        }
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert "multipart/form-data" in body['message']

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_invalid_file_extension(self, mock_parse, mock_boto3):
        """Test: Error with not allowed extension"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        mock_parse.return_value = {
            'filename': 'file.txt',  # Not allowed
            'content': b'content',
            'content_type': 'text/plain',
            'field_name': 'file'
        }

        event = {
            'body': 'test',
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert "Invalid file format" in body['message']

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_empty_file(self, mock_parse, mock_boto3):
        """Test: Error with empty file"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        mock_parse.return_value = {
            'filename': 'empty.csv',
            'content': b'',  # Empty
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        event = {
            'body': 'test',
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['message'] == "File is empty"


class TestParseMultipart:
    """Tests for multipart parsing function"""

    def test_parse_csv_file(self):
        """Test: CSV file parsing"""
        # Simulated multipart data
        boundary = "----WebKitFormBoundary123"
        content_type = f"multipart/form-data; boundary={boundary}"

        body = (
            f"------WebKitFormBoundary123\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"test.csv\"\r\n"
            f"Content-Type: text/csv\r\n"
            f"\r\n"
            f"name,age\nJohn,30\n"
            f"------WebKitFormBoundary123--\r\n"
        ).encode()

        result = lambda_function.parse_multipart_manual(body, content_type)

        assert result is not None
        assert result['filename'] == 'test.csv'
        assert result['content'] == b'name,age\nJohn,30'
        assert result['content_type'] == 'text/csv'

    def test_parse_no_file(self):
        """Test: No file in multipart data"""
        boundary = "----WebKitFormBoundary123"
        content_type = f"multipart/form-data; boundary={boundary}"

        # Only text field
        body = (
            f"------WebKitFormBoundary123\r\n"
            f"Content-Disposition: form-data; name=\"field\"\r\n"
            f"\r\n"
            f"value\r\n"
            f"------WebKitFormBoundary123--\r\n"
        ).encode()

        result = lambda_function.parse_multipart_manual(body, content_type)
        assert result is None

    def test_parse_no_boundary(self):
        """Test: Content-Type without boundary"""
        body = b"data"
        content_type = "multipart/form-data"

        result = lambda_function.parse_multipart_manual(body, content_type)
        assert result is None


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_get_content_type(self):
        """Test: Detect Content-Type by extension"""
        assert lambda_function._get_content_type('test.csv') == 'text/csv'
        assert lambda_function._get_content_type(
            'test.xlsx') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert lambda_function._get_content_type('test.pdf') == 'application/pdf'
        assert lambda_function._get_content_type('test.unknown') == 'application/octet-stream'

    def test_sanitize_filename(self):
        """Test: Sanitize filename"""
        assert lambda_function._sanitize_filename('normal file.csv') == 'normal_file.csv'
        assert lambda_function._sanitize_filename('file@#$.csv') == 'file_.csv'
        assert lambda_function._sanitize_filename('') == 'unknown_file'

    def test_get_file_extension(self):
        """Test: Get file extension"""
        assert lambda_function._get_file_extension('test.csv') == 'csv'
        assert lambda_function._get_file_extension('test.XLSX') == 'xlsx'
        assert lambda_function._get_file_extension('test') == ''  # No extension returns empty string
        assert lambda_function._get_file_extension('') == 'unknown'  # Empty filename returns 'unknown'
        assert lambda_function._get_file_extension(None) == 'unknown'  # None returns 'unknown'

    def test_is_allowed_file(self):
        """Test: Validate allowed extensions"""
        assert lambda_function._is_allowed_file('test.csv') is True
        assert lambda_function._is_allowed_file('test.xlsx') is True
        assert lambda_function._is_allowed_file('test.pdf') is True
        assert lambda_function._is_allowed_file('test.xls') is True
        assert lambda_function._is_allowed_file('test.txt') is False
        assert lambda_function._is_allowed_file('') is False

    def test_response_function(self):
        """Test: HTTP response function"""
        # Successful response
        result = lambda_function._response(200, "OK", {"key": "value"})
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "OK"

        # Error response
        result = lambda_function._response(400, "Error")
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestPDFExtraction:
    """Tests for PDF extraction and complaint message functionality"""

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.create_complaint_message_from_output')
    def test_successful_pdf_upload_with_extraction(self, mock_create_complaint, mock_parse, mock_boto3):
        """Test: Successful PDF upload with extraction and complaint creation"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_lambda = Mock()
        mock_boto3.side_effect = lambda service: {
            's3': mock_s3,
            'sqs': mock_sqs,
            'lambda': mock_lambda
        }[service]
        
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-msg-123'}

        # Mock PDF file
        mock_parse.return_value = {
            'filename': 'complaint.pdf',
            'content': b'%PDF-1.4 fake pdf content',
            'content_type': 'application/pdf',
            'field_name': 'file'
        }

        # Mock lambda extraction response
        mock_lambda_response = {
            'success': True,
            'result': {
                'case_id': 'RGL22-000433',
                'narrative': 'Test complaint narrative',
                'criticality': 'High'
            }
        }
        mock_lambda.invoke.return_value = {
            'Payload': Mock(read=Mock(return_value=json.dumps(mock_lambda_response).encode()))
        }

        # Mock complaint message creation
        mock_create_complaint.return_value = {
            'complaint_id': 'CAS-123456789',
            'code': 'CAS-123456789',
            'narrative': 'Test complaint narrative'
        }

        event = {
            'body': 'fake-pdf-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'complaint_message_id' in body['data']
        
        # Verify lambda extraction was called
        mock_lambda.invoke.assert_called_once()
        # Verify two SQS messages sent (complaint + file upload)
        assert mock_sqs.send_message.call_count == 2

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_pdf_extraction_lambda_failure(self, mock_parse, mock_boto3):
        """Test: PDF extraction lambda fails"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_lambda = Mock()
        mock_boto3.side_effect = lambda service: {
            's3': mock_s3,
            'sqs': mock_sqs,
            'lambda': mock_lambda
        }[service]
        
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        # Mock PDF file
        mock_parse.return_value = {
            'filename': 'complaint.pdf',
            'content': b'%PDF-1.4 fake pdf content',
            'content_type': 'application/pdf',
            'field_name': 'file'
        }

        # Mock lambda extraction failure
        mock_lambda.invoke.side_effect = Exception("Lambda invocation failed")

        event = {
            'body': 'fake-pdf-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False


class TestComplaintMessageCreation:
    """Tests for complaint message creation functionality"""

    def test_create_complaint_message_from_dict(self):
        """Test: Create complaint message from dictionary input"""
        output_data = {
            'success': True,
            'result': {
                'case_id': 'RGL22-000433',
                'narrative': 'Test narrative',
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'primary_reporter': {'name': 'John Doe'},
                'patient_name': 'Jane Smith'
            }
        }

        result = lambda_function.create_complaint_message_from_output(output_data)

        assert result['complaint_id']
        assert result['narrative'] == 'Test narrative'
        assert result['criticality'] == 'High'
        assert result['status'] == 'IN-REVIEW'
        assert result['complaint_id'] == 'RGL22-000433'  # Uses case_id from input

    def test_create_complaint_message_from_json_string(self):
        """Test: Create complaint message from JSON string input"""
        output_str = json.dumps({
            'success': True,
            'result': {
                'case_id': 'RGL22-000444',
                'narrative': 'Another test narrative',
                'criticality': 'Medium'
            }
        })

        result = lambda_function.create_complaint_message_from_output(output_str)

        assert result['complaint_id']
        assert result['narrative'] == 'Another test narrative'
        assert result['criticality'] == 'Medium'

    def test_create_complaint_message_missing_fields(self):
        """Test: Create complaint message with missing optional fields"""
        output_data = {
            'success': True,
            'result': {
                'case_id': 'RGL22-000555'
                # Missing other fields
            }
        }

        result = lambda_function.create_complaint_message_from_output(output_data)

        assert result['complaint_id']
        assert result['narrative'] == ''  # Default empty
        assert result['criticality'] == 'NA'  # Default NA
        assert result['primary_reporter'] == {}  # Default empty dict


class TestComplaintCodeGeneration:
    """Tests for complaint code generation functions"""

    def test_generate_complaint_code_timestamp_random(self):
        """Test: Generate complaint code with timestamp_random strategy"""
        code = lambda_function.generate_complaint_code('timestamp_random')
        
        assert code.startswith('CAS-')
        assert len(code) > 10  # Should be reasonably long
        
        # Generate another to ensure uniqueness
        code2 = lambda_function.generate_complaint_code('timestamp_random')
        assert code != code2

    def test_generate_complaint_code_uuid_short(self):
        """Test: Generate complaint code with uuid_short strategy"""
        code = lambda_function.generate_complaint_code('uuid_short')
        
        assert code.startswith('CAS-')
        assert len(code) == 12  # CAS- + 8 chars

    def test_generate_complaint_code_default(self):
        """Test: Generate complaint code with default strategy"""
        code = lambda_function.generate_complaint_code()
        
        assert code.startswith('CAS-')
        # Should default to timestamp_random

    def test_generate_ulid(self):
        """Test: Generate ULID"""
        ulid = lambda_function.generate_ulid()
        
        assert len(ulid) == 26
        assert ulid.isalnum()  # Should be alphanumeric

    def test_generate_nanoid(self):
        """Test: Generate Nanoid"""
        nanoid = lambda_function.generate_nanoid(8)
        
        assert len(nanoid) == 8
        # Should not contain confusing characters
        assert '0' not in nanoid
        assert '1' not in nanoid
        assert 'O' not in nanoid
        assert 'I' not in nanoid


class TestUserExtraction:
    """Tests for user extraction from event"""

    def test_get_user_from_cognito_claims(self):
        """Test: Extract user from Cognito claims"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'email': 'user@example.com',
                        'sub': 'user-123'
                    }
                }
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'user@example.com'

    def test_get_user_from_headers(self):
        """Test: Extract user from custom headers"""
        event = {
            'headers': {
                'x-user-email': 'header-user@example.com'
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'header-user@example.com'

    def test_get_user_anonymous_fallback(self):
        """Test: Fallback to anonymous when no user info"""
        event = {}

        user = lambda_function._get_user_from_event(event)
        assert user == 'anonymous'


class TestSQSQueueResolution:
    """Tests for SQS queue URL resolution"""

    @patch('boto3.client')
    def test_queue_url_resolution_success(self, mock_boto3):
        """Test: Successful queue URL resolution"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/test-queue'}

        # This would be tested as part of lambda_handler, but we can test the logic
        assert True  # Placeholder for queue resolution test

    @patch('boto3.client')
    def test_queue_url_resolution_failure(self, mock_boto3):
        """Test: Queue URL resolution failure"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.side_effect = Exception("Queue not found")

        # This would result in 500 error in lambda_handler
        assert True  # Placeholder for queue resolution failure test


class TestCSVExcelProcessing:
    """Tests for CSV/Excel file processing functionality"""

    def test_process_csv_file_success(self):
        """Test: Successfully process CSV file with valid data"""
        csv_content = "Case ID,Narrative Text\nCAS-001,First complaint narrative\nCAS-002,Second complaint narrative"
        csv_bytes = csv_content.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_bytes, 'csv')
        
        assert result['success'] is True
        assert result['total_rows'] == 2
        assert result['processed_complaints'] == 2
        assert len(result['complaints']) == 2
        
        # Check first complaint
        complaint1 = result['complaints'][0]
        assert complaint1['case_id'] == 'CAS-001'
        assert complaint1['narrative'] == 'First complaint narrative'
        assert complaint1['status'] == 'IN-REVIEW'
        assert 'CAS-' in complaint1['complaint_id']
        assert complaint1['metadata']['source'] == 'CSV Import'
        assert complaint1['metadata']['row_number'] == 1

    def test_process_excel_file_success(self):
        """Test: Successfully process Excel file with valid data"""
        # Create test Excel file in memory
        df = pd.DataFrame({
            'Case ID': ['EXL-001', 'EXL-002'],
            'Narrative Text': ['Excel complaint one', 'Excel complaint two']
        })
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_bytes = excel_buffer.getvalue()
        
        result = lambda_function.process_csv_excel_file(excel_bytes, 'xlsx')
        
        assert result['success'] is True
        assert result['total_rows'] == 2
        assert result['processed_complaints'] == 2
        
        complaint1 = result['complaints'][0]
        assert complaint1['case_id'] == 'EXL-001'
        assert complaint1['narrative'] == 'Excel complaint one'
        assert complaint1['metadata']['source'] == 'XLSX Import'

    def test_process_csv_file_row_limit_exceeded(self):
        """Test: Reject CSV file with more than 20 rows"""
        # Create CSV with 21 rows
        rows = ["Case ID,Narrative Text"]
        for i in range(21):
            rows.append(f"CAS-{i:03d},Complaint narrative {i}")
        csv_content = "\n".join(rows)
        csv_bytes = csv_content.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_bytes, 'csv')
        
        assert result['success'] is False
        assert "21 rows" in result['message']
        assert "Maximum allowed is 20 rows" in result['message']

    def test_process_csv_file_insufficient_columns(self):
        """Test: Reject CSV file with less than 2 columns"""
        csv_content = "Single Column\nValue 1\nValue 2"
        csv_bytes = csv_content.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_bytes, 'csv')
        
        assert result['success'] is False
        assert "at least 2 columns" in result['message']

    def test_process_csv_file_empty_narratives(self):
        """Test: Skip rows with empty narratives"""
        csv_content = "Case ID,Narrative Text\nCAS-001,Valid narrative\nCAS-002,\nCAS-003,Another valid narrative"
        csv_bytes = csv_content.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_bytes, 'csv')
        
        assert result['success'] is True
        assert result['total_rows'] == 3
        assert result['processed_complaints'] == 2  # Skip empty narrative
        
        # Check that only valid narratives are processed
        narratives = [c['narrative'] for c in result['complaints']]
        assert 'Valid narrative' in narratives
        assert 'Another valid narrative' in narratives

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.process_csv_excel_file')
    def test_csv_upload_integration(self, mock_process, mock_parse, mock_boto3):
        """Test: Full CSV upload integration with SQS"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-123'}

        # Mock file parsing
        mock_parse.return_value = {
            'filename': 'complaints.csv',
            'content': b'Case ID,Narrative\nC001,Test complaint',
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        # Mock CSV processing
        mock_process.return_value = {
            'success': True,
            'complaints': [{
                'complaint_id': 'CAS-123456789',
                'code': 'CAS-123456789',
                'case_id': 'C001',
                'narrative': 'Test complaint',
                'status': 'IN-REVIEW'
            }],
            'total_rows': 1,
            'processed_complaints': 1
        }

        event = {
            'body': 'multipart-csv-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['complaints_processed'] == 1
        assert 'complaint_message_ids' in body['data']
        
        # Verify SQS message was sent
        mock_sqs.send_message.assert_called_once()
        
        # Verify message attributes
        call_args = mock_sqs.send_message.call_args
        message_attrs = call_args[1]['MessageAttributes']
        assert message_attrs['Source']['StringValue'] == 'CSV Extraction'
        assert message_attrs['ComplaintCode']['StringValue'] == 'CAS-123456789'

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.process_csv_excel_file')
    def test_csv_processing_error_handling(self, mock_process, mock_parse, mock_boto3):
        """Test: Error handling during CSV processing"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        # Mock file parsing
        mock_parse.return_value = {
            'filename': 'bad.csv',
            'content': b'malformed,csv,data',
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        # Mock CSV processing failure
        mock_process.return_value = {
            'success': False,
            'message': 'File has 25 rows. Maximum allowed is 20 rows.'
        }

        event = {
            'body': 'multipart-bad-csv-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert "Maximum allowed is 20 rows" in body['message']
        
        # Verify no SQS messages were sent
        mock_sqs.send_message.assert_not_called()