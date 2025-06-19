import random
import pathlib
import os
import re
from datetime import datetime, date
from typing import List, Dict, Optional

from .database import Patient, PatientRecords, get_session
from ..common.constants import Constants
from sqlalchemy.orm import Session

def get_patient_statistics(db):
    """Get patient statistics for dashboard."""
    try:
        # Total number of patients
        total_patients = db.query(Patient).count()
        
        # Calculate target achievement based on actual patient records
        # Consider a patient achieved targets if they have records with weekly exercise >= 150 mins (WHO recommendation)
        patients_with_targets = db.query(Patient.id).join(
            PatientRecords, Patient.id == PatientRecords.patient_id
        ).filter(
            PatientRecords.total_weekly.isnot(None),
            PatientRecords.total_weekly >= 150  # WHO recommends 150 mins/week
        ).distinct().count()
        
        target_percentage = (patients_with_targets / total_patients * 100) if total_patients > 0 else 0
        
        # Keep persuasion success as placeholder since this data doesn't exist in database
        persuasion_success = 12  # Placeholder - would come from chatbot interaction data
        
        return {
            "total_patients": total_patients,
            "target_percentage": round(target_percentage, 1),
            "persuasion_success": persuasion_success
        }
    except Exception as e:
        print(f"Error getting patient statistics: {e}")
        return {
            "total_patients": 0,
            "target_percentage": 0,
            "persuasion_success": 0
        }


def get_patient_heart_rate_data(db):
    """Get heart rate data for patients from actual records."""
    try:
        # Get patients with their latest heart rate data from PatientRecords
        heart_rate_data = []
        
        # Get patients and their latest records with heart rate data
        patients = db.query(Patient).limit(7).all()
        
        for patient in patients:
            # Get latest record with heart rate data for this patient
            latest_record = db.query(PatientRecords).filter(
                PatientRecords.patient_id == patient.id,
                PatientRecords.hr_fat_burn.isnot(None)
            ).order_by(PatientRecords.date.desc()).first()
            
            if latest_record:
                # Use actual heart rate data from records
                heart_rate_data.append({
                    "patient_name": patient.username,
                    "moderate": latest_record.hr_fat_burn or 0,  # Fat burn HR as moderate
                    "intense": latest_record.hr_intense or 0    # Intense HR
                })
            else:
                # If no records, use last_heart_rate from Patient table or 0
                heart_rate_data.append({
                    "patient_name": patient.username,
                    "moderate": patient.last_heart_rate or 75,  # Default moderate
                    "intense": (patient.last_heart_rate or 75) + 30  # Default intense
                })
        
        return heart_rate_data
    except Exception as e:
        print(f"Error getting heart rate data: {e}")
        return []


def get_age_distribution(db):
    """Get age group distribution for patients from actual database."""
    try:
        # Get all patients with ages
        patients = db.query(Patient).filter(Patient.age.isnot(None)).all()
        
        # Initialize age groups
        age_groups = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "80+": 0
        }
        
        # Count patients in each age group
        for patient in patients:
            age = patient.age
            if age <= 20:
                age_groups["0-20"] += 1
            elif age <= 40:
                age_groups["21-40"] += 1
            elif age <= 60:
                age_groups["41-60"] += 1
            elif age <= 80:
                age_groups["61-80"] += 1
            else:
                age_groups["80+"] += 1
        
        return age_groups
    except Exception as e:
        print(f"Error getting age distribution: {e}")
        return {}


def create_sample_patients(db):
    """Create sample patient data for testing."""
    try:
        
        # Create sample patients if not enough exist
        for i in range(1, 21):
            patient_name = Constants.SAMPLE_PATIENT_NAMES[i-1]
            username = f"test_patient_{i}"
            
            # Check if patient already exists
            existing_patient = db.query(Patient).filter(Patient.username == username).first()
            if not existing_patient:
                # Create patient record directly
                patient = Patient(
                    username=username,
                    user_id=None,  # Not linking to User table
                    age=random.randint(20, 80),
                    target_achieved=random.choice([True, False]),
                    last_heart_rate=int(random.uniform(60, 120))
                )
                db.add(patient)
                print(f"✓ Created patient: {username} ({patient_name})")
        
        db.commit()
        print("Sample patients created successfully!")
        
    except Exception as e:
        print(f"Error creating sample patients: {e}")


def get_all_patients(db: Session) -> List[Dict]:
    """Get all patients with their information."""
    patients = db.query(Patient).all()
    
    result = []
    for patient in patients:
        result.append({
            "id": patient.id,
            "username": patient.username,
            "name": patient.username,  # Use username as name for now
            "age": patient.age,
            "target_achieved": patient.target_achieved,
            "last_heart_rate": patient.last_heart_rate,
            "created_at": patient.created_at,
        })
    
    return result


def get_patient_records(db: Session, username: str) -> List[Dict]:
    """Get all records for a specific patient by username."""
    records = db.query(PatientRecords).filter(
        PatientRecords.username == username
    ).order_by(PatientRecords.date.desc()).all()
    
    result = []
    for record in records:
        result.append({
            "id": record.id,
            "patient_id": record.patient_id,
            "date": record.date,
            "week_number": record.week_number,
            "week_description": record.week_description,
            "hr_fat_burn": record.hr_fat_burn,
            "hr_mvpa": record.hr_mvpa,
            "hr_intense": record.hr_intense,
            "total_mins_per_session": record.total_mins_per_session,
            "total_weekly": record.total_weekly,
            "boost": record.boost,
            "notes": record.notes,
            "report_file_path": record.report_file_path,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        })
    
    return result


def parse_record(file_path: pathlib.Path, username: str = None) -> List[Dict]:
    """
    Parse uploaded file and extract patient record data.
    
    Args:
        file_path: Path to the uploaded file
        username: Username (optional, will be extracted from DOCX files)
        
    Returns:
        List of dictionaries containing parsed record data ready for database insertion
    """
    records = []
    
    try:
        file_extension = file_path.suffix.lower()
        print(f"Parsing file: {file_path} (type: {file_extension})")
        
        if file_extension in ['.docx']:
            records = _parse_docx_file(file_path)
        else:
            print(f"❌ Unsupported file type: {file_extension}. Only DOCX files are supported.")
        
        print(f"🔍 PARSE RESULTS for {file_path.name}:")
        print(f"   📊 Records found: {len(records)}")
        for i, record in enumerate(records):
            print(f"   📝 Record {i+1}: {record}")
        
    except Exception as e:
        print(f"💥 ERROR parsing file {file_path}: {e}")
        import traceback
        traceback.print_exc()
        
    return records


def _extract_number(value, number_type=float):
    """Extract number from string value, handling various formats."""
    if not value:
        return None
    
    try:
        # Handle string values
        if isinstance(value, str):
            # Remove common non-numeric characters but keep decimal points
            cleaned = re.sub(r'[^\d\.-]', '', value.strip())
            if cleaned:
                return number_type(cleaned)
        else:
            return number_type(value)
    except (ValueError, TypeError):
        pass
    
    return None


def _create_document_record(file_path: pathlib.Path, username: str) -> List[Dict]:
    """Create a record entry for document files (DOCX)."""
    record = {
        "username": username,
        "date": date.today(),
        "week_number": None,
        "week_description": f"Document: {file_path.name}",
        "hr_fat_burn": None,
        "hr_mvpa": None,
        "hr_intense": None,
        "total_mins_per_session": None,
        "total_weekly": None,
        "boost": None,
        "notes": f"Document upload: {file_path.name}",
        "report_file_path": str(file_path),
    }
    return [record]


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date string in various formats. Returns None if no valid date."""
    if not date_str or not date_str.strip():
        return None
        
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%m-%d-%Y',
        '%d-%m-%Y',
        '%m/%d/%y',  # Added 2-digit year support
        '%d/%m/%y',
    ]
    
    date_str = str(date_str).strip()
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt).date()
            print(f"  📅 Successfully parsed date: '{date_str}' → {parsed_date}")
            return parsed_date
        except ValueError:
            continue
            
    # If all formats fail, return None
    print(f"  ⚠️  Could not parse date: '{date_str}', returning None")
    return None


def _is_number(value: str) -> bool:
    """Check if a string represents a number."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_patient_details(db: Session, username: str) -> Optional[Dict]:
    """Get detailed patient information by username."""
    patient = db.query(Patient).filter(Patient.username == username).first()
    
    if not patient:
        return None
        
    return {
        "id": patient.id,
        "username": patient.username,
        "name": patient.username,  # Use username as name for now
        "age": patient.age,
        "target_achieved": patient.target_achieved,
        "last_heart_rate": patient.last_heart_rate,
        "created_at": patient.created_at,
    }


async def handle_file_upload(files: List) -> Dict[str, any]:
    """Handle single file upload, parse it, and save records to database."""
    if not files:
        return {
            "success": False,
            "message": "No files provided",
            "uploaded_files": []
        }
    
    # Only process the first file (single file upload)
    file = files[0]
    uploaded_files = []
    success = True
    message = ""
    
    try:
        # Read the file data
        upload_data = await file.read()
        
        # Get upload directory
        try:
            import reflex as rx
            upload_dir = rx.get_upload_dir()
        except Exception as e:
            print(f"rx.get_upload_dir() failed: {e}")
            upload_dir = os.path.join(os.getcwd(), "uploaded_files")
            upload_dir = pathlib.Path(upload_dir)
        
        # Ensure the directory exists
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create full file path
        file_path = upload_dir / file.name
        
        # Save the file
        with file_path.open("wb") as f:
            f.write(upload_data)
        
        uploaded_files.append(file.name)
        print(f"Successfully saved: {file.name}")
        
        # Parse the file and extract records (username will be extracted from DOCX files)
        parsed_records = parse_record(file_path)
        
        # Save parsed records to database
        db = get_session()
        saved_count = 0
        participants_processed = set()
        data_records = 0
        absence_records = 0
        
        try:
            for record_data in parsed_records:
                username = record_data.get("username")
                if username and add_patient_record(db, username, record_data):
                    saved_count += 1
                    participants_processed.add(username)
                    
                    # Track record types
                    if record_data.get("date") is None:
                        absence_records += 1
                    else:
                        data_records += 1
        finally:
            db.close()
        
        if saved_count > 0:
            participants_list = ", ".join(participants_processed)
            success = True
            message = f"Successfully uploaded and parsed {file.name}. Added {saved_count} record(s) for participants: {participants_list}. ({data_records} data records, {absence_records} absence records)"
        else:
            success = False
            message = f"File {file.name} was uploaded but no records could be parsed."
            
    except Exception as e:
        print(f"Error uploading file {file.name}: {e}")
        success = False
        message = f"Error uploading file: {str(e)}"
    
    return {
        "success": success,
        "message": message,
        "uploaded_files": uploaded_files
    }


def create_new_patient(patient_data: Dict) -> bool:
    """Create a new patient in the database."""
    db = get_session()
    try:
        name = patient_data.get('name')
        if not name:
            print("❌ Patient name is required")
            return False
            
        # Create username from name (simple approach - could be improved)
        username = name.lower().replace(' ', '_')
        
        # Check if patient already exists
        existing_patient = db.query(Patient).filter(Patient.username == username).first()
        if existing_patient:
            print(f"❌ Patient with username {username} already exists")
            return False
        
        # Extract age if provided
        age = None
        if patient_data.get('age'):
            try:
                age = int(patient_data.get('age'))
            except (ValueError, TypeError):
                age = None
        
        # Create new patient
        patient = Patient(
            username=username,
            user_id=None,  # Not linking to User table
            age=age,
            target_achieved=False,
            last_heart_rate=None
        )
        
        db.add(patient)
        db.commit()
        
        print(f"✅ Successfully created patient: {username} ({name})")
        return True
        
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def _parse_docx_file(file_path: pathlib.Path) -> List[Dict]:
    """Parse DOCX file using docx2txt to extract text and split by participants."""
    import re
    
    try:
        # Try to import docx2txt
        import docx2txt
    except ImportError:
        print("❌ docx2txt not available. Please install with: pip install docx2txt")
        return []
    
    records = []
    
    try:
        print(f"📄 Parsing DOCX file using docx2txt: {file_path}")
        
        # Extract all text from DOCX
        full_text = docx2txt.process(file_path)
        print(f"📊 Extracted {len(full_text)} characters of text")
        
        # Parse all participant data using the new logic
        all_parsed_data = _parse_all_participant_data(full_text, file_path)
        
        print(f"📊 DOCX parsing complete. Total records: {len(all_parsed_data)}")
        
                # Convert to our expected format and ensure patients exist
        for data_row in all_parsed_data:
            participant_id = data_row.get('participant_id')
            if participant_id:
                # Ensure patient exists in database
                _ensure_patient_exists(participant_id)
                
                # Convert to our record format
                record = {
                    "username": participant_id,
                    "date": _parse_date(data_row.get('Date')) if data_row.get('Date') else None,
                    "week_number": data_row.get('Week_Number'),
                    "week_description": f"Week {data_row.get('Week_Number')}" if data_row.get('Week_Number') else None,
                    "hr_fat_burn": data_row.get('HR (fat burn)'),
                    "hr_mvpa": data_row.get('HR (cardio)'),
                    "hr_intense": data_row.get('HR (intense)'),
                    "total_mins_per_session": data_row.get('Total mins (per session)'),
                    "total_weekly": data_row.get('Total weekly'),
                    "boost": data_row.get('Boosted'),
                    "notes": data_row.get('Notes') or f"Imported from {file_path.name}",
                    "report_file_path": str(file_path),
                }
                
                records.append(record)
        
        # Summary by participant and type
        if records:
            participants = {}
            for record in records:
                username = record['username']
                if username not in participants:
                    participants[username] = {'data_records': 0, 'absence_records': 0}
                
                if record.get('date'):
                    participants[username]['data_records'] += 1
                else:
                    participants[username]['absence_records'] += 1
            
            print(f"📋 Records by participant:")
            for username, counts in participants.items():
                total = counts['data_records'] + counts['absence_records']
                print(f"  {username}: {total} total ({counts['data_records']} data, {counts['absence_records']} absence)")
        
    except Exception as e:
        print(f"💥 Error parsing DOCX file: {e}")
        import traceback
        traceback.print_exc()
    
    return records


def _parse_participant_data_block(text_block: str, participant_id: str, file_path: pathlib.Path) -> List[Dict]:
    """
    Parses a single participant's data block, extracting structured information
    including date, activity metrics, week number, and notes.
    Adds placeholder rows for weeks without daily data entries.
    """
    import re
    
    parsed_rows = []
    sections = [s.strip() for s in text_block.split('\n\n\n') if s.strip()]

    if not sections:
        return parsed_rows

    expected_data_keys = [
        'Date', 'HR (fat burn)', 'HR (cardio)', 'HR (intense)',
        'Total mins (per session)', 'Total weekly', 'Boosted'
    ]

    # Combine all data sections into a single string to split by double newlines
    raw_data_items = []
    if len(sections) > 1:
        raw_data_items = '\n\n'.join(sections[1:]).split('\n\n')

    current_week_info = {'number': None, 'notes': None, 'has_data': False}
    current_daily_accumulator = []

    def add_placeholder_row():
        """Helper to add a placeholder row for the current week if no data was found."""
        if current_week_info['number'] is not None and not current_week_info['has_data']:
            placeholder_row = {
                'participant_id': participant_id,
                'Week_Number': current_week_info['number'],
                'Notes': current_week_info['notes']
            }
            for key in expected_data_keys:
                placeholder_row[key] = None
            parsed_rows.append(placeholder_row)

    for item in raw_data_items:
        clean_item = item.strip()

        week_match = re.match(r'Week (\d+)\s*(.*)', clean_item, re.IGNORECASE)
        if week_match:
            add_placeholder_row() # Check and add placeholder for the *previous* week

            current_week_info['number'] = int(week_match.group(1))
            current_week_info['notes'] = week_match.group(2).strip() or None
            current_week_info['has_data'] = False
            current_daily_accumulator = []
            continue

        date_match = re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', clean_item)
        if date_match:
            current_daily_accumulator = [clean_item] # Start new daily record with date
            continue

        if current_daily_accumulator: # If a date has been found and we're accumulating data
            current_daily_accumulator.append(clean_item)

            if len(current_daily_accumulator) == len(expected_data_keys):
                row_entry = {
                    'participant_id': participant_id,
                    'Week_Number': current_week_info['number'],
                    'Notes': current_week_info['notes']
                }
                for i, key in enumerate(expected_data_keys):
                    val_str = current_daily_accumulator[i]
                    if key not in ['Date', 'Boosted']:
                        try:
                            row_entry[key] = float(val_str) if val_str.strip() else None
                        except ValueError:
                            row_entry[key] = val_str or None
                    else:
                        row_entry[key] = val_str or None

                parsed_rows.append(row_entry)
                current_week_info['has_data'] = True
                current_daily_accumulator = []

    add_placeholder_row() # Final check for the last week in the block

    return parsed_rows


def _parse_all_participant_data(full_text: str, file_path: pathlib.Path) -> List[Dict]:
    """Parse all participant data from the full DOCX text."""
    import re
    
    all_parsed_data = []
    participant_split_pattern = r'Participant\s+([A-Z]{3}[A-Z0-9P]+)'
    split_result = re.split(participant_split_pattern, full_text, flags=re.IGNORECASE)

    start_index = 0 if split_result and split_result[0].strip() else 1

    i = start_index
    while i < len(split_result):
        if i + 1 < len(split_result):
            participant_id = split_result[i].strip()
            data_block = split_result[i+1].strip()

            if participant_id and data_block:
                parsed_block_data = _parse_participant_data_block(data_block, participant_id, file_path)
                all_parsed_data.extend(parsed_block_data)
            i += 2
        else:
            break
    return all_parsed_data


def _ensure_patient_exists(username: str) -> bool:
    """Check if patient exists in database, create if not exists."""
    db = get_session()
    try:
        print(f"🔍 Checking if patient {username} exists...")
        
        # Check if patient already exists in Patient table
        existing_patient = db.query(Patient).filter(Patient.username == username).first()
        
        if existing_patient:
            print(f"  ✅ Patient {username} already exists with ID {existing_patient.id}")
            return True
        
        # Create new patient entry directly in Patient table
        print(f"  ➕ Creating new patient: {username}")
        
        try:
            # Create patient record with username as primary identifier
            patient = Patient(
                username=username,
                user_id=None,  # Not linking to User table as per user's request
                age=None,  # Will be updated later if needed
                target_achieved=False,
                last_heart_rate=None
            )
            db.add(patient)
            db.flush()  # Get the auto-generated ID
            
            print(f"  ✅ Successfully created patient {username} with ID {patient.id}")
            db.commit()
            return True
                
        except Exception as create_error:
            print(f"  ❌ Error creating patient: {create_error}")
            db.rollback()
            return False
            
    except Exception as e:
        print(f"  💥 Error ensuring patient exists: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def add_patient_record(db: Session, username: str, record_data: Dict) -> bool:
    """Add a new patient record."""
    try:
        print(f"💾 Adding patient record for {username}")
        print(f"   📝 Record data: {record_data}")
        
        # Get patient_id from username
        patient = db.query(Patient).filter(Patient.username == username).first()
        if not patient:
            print(f"   ❌ Patient {username} not found")
            return False
        
        # Handle date field - can be None for absence records
        record_date = record_data.get("date")
        
        # Check if a record already exists for this patient_id and date combination
        existing_record = None
        if record_date is not None:
            existing_record = db.query(PatientRecords).filter(
                PatientRecords.patient_id == patient.id,
                PatientRecords.date == record_date
            ).first()
            print(f"   🔍 Checking for existing record with patient_id={patient.id}, date={record_date}")
        else:
            # For absence records, check by patient_id and week_number
            existing_record = db.query(PatientRecords).filter(
                PatientRecords.patient_id == patient.id,
                PatientRecords.week_number == record_data.get("week_number"),
                PatientRecords.date.is_(None)  # Only match other absence records
            ).first()
            print(f"   🔍 Checking for existing absence record with patient_id={patient.id}, week_number={record_data.get('week_number')}")
        
        if existing_record:
            print(f"   🔄 Updating existing record ID {existing_record.id}")
            # Update existing record
            existing_record.username = username
            existing_record.week_number = record_data.get("week_number")
            existing_record.week_description = record_data.get("week_description")
            existing_record.hr_fat_burn = record_data.get("hr_fat_burn")
            existing_record.hr_mvpa = record_data.get("hr_mvpa")
            existing_record.hr_intense = record_data.get("hr_intense")
            existing_record.total_mins_per_session = record_data.get("total_mins_per_session")
            existing_record.total_weekly = record_data.get("total_weekly")
            existing_record.boost = record_data.get("boost")
            existing_record.notes = record_data.get("notes")
            existing_record.report_file_path = record_data.get("report_file_path")
            
            db.commit()
            action = "UPDATED"
        else:
            print(f"   ➕ Creating new record")
            # Handle absence record date logic
            if record_date is None:
                # For absence records, use None to clearly indicate no activity
                print(f"   📅 Absence record - keeping date as None")
            
            # Create new record
            new_record = PatientRecords(
                patient_id=patient.id,  # Link to Patient table via patient_id
                username=username,
                date=record_date,  # Keep as None for absence records
                week_number=record_data.get("week_number"),
                week_description=record_data.get("week_description"),
                hr_fat_burn=record_data.get("hr_fat_burn"),
                hr_mvpa=record_data.get("hr_mvpa"),
                hr_intense=record_data.get("hr_intense"),
                total_mins_per_session=record_data.get("total_mins_per_session"),
                total_weekly=record_data.get("total_weekly"),
                boost=record_data.get("boost"),
                notes=record_data.get("notes"),
                report_file_path=record_data.get("report_file_path"),
            )
            
            db.add(new_record)
            db.commit()
            action = "ADDED"
        
        # Log the type of record processed
        if record_data.get("date") is None:
            print(f"   ✅ Successfully {action} ABSENCE record (Week {record_data.get('week_number')}) for Patient ID {patient.id}")
        else:
            print(f"   ✅ Successfully {action} DATA record (Week {record_data.get('week_number')}, Date {record_data.get('date')}) for Patient ID {patient.id}")
            
        return True
    except Exception as e:
        db.rollback()
        print(f"   💥 Error adding patient record: {e}")
        import traceback
        traceback.print_exc()
        return False 