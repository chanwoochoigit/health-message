"""Patients list page - UI Components and Layout with integrated state."""

import reflex as rx
from ..components.layouts import page_layout
from ..services.patient_service import (
    get_all_patients,
    get_patient_records, 
    get_patient_details,
    handle_file_upload,
    create_new_patient
)
from ..services.database import SessionLocal
from ..pages.auth import AuthState


class PatientsState(rx.State):
    """Patients page state - integrated with UI."""
    
    patients: list[dict] = []
    show_add_form: bool = False
    
    # Expandable row state
    expanded_patient_username: str = ""
    patient_records: list[dict] = []
    patient_details: dict = {}
    
    # General upload
    show_general_upload_form: bool = False
    uploaded_files: list[str] = []
    upload_success: bool = False
    upload_message: str = ""
    show_upload_feedback: bool = False
    
    # Date filtering
    start_date: str = ""
    end_date: str = ""
    
    # Form fields
    form_name: str = ""
    form_gender: str = ""
    form_age: str = ""
    form_phone: str = ""
    form_moderate_hr_min: str = ""
    form_moderate_hr_max: str = ""
    form_vigorous_hr_min: str = ""
    form_vigorous_hr_max: str = ""
    form_target_duration: str = ""
    form_prompt_times: str = ""
    form_medical_condition: str = ""
    form_disability_level: str = ""

    def load_patients(self):
        """Load all patients - delegate to service."""
        # Initialize default dates if not set
        if not self.start_date or not self.end_date:
            from datetime import date, timedelta
            today = date.today()
            self.end_date = today.strftime("%Y-%m-%d")
            self.start_date = (today - timedelta(days=365*2)).strftime("%Y-%m-%d")
        
        db = SessionLocal()
        try:
            self.patients = get_all_patients(db)
        finally:
            db.close()
    
    def toggle_patient_details(self, username: str):
        """Toggle expanded view for a patient."""
        if self.expanded_patient_username == username:
            self.expanded_patient_username = ""
            self.patient_records = []
            self.patient_details = {}
        else:
            self.expanded_patient_username = username
            self.load_patient_details(username)
    
    def load_patient_details(self, username: str):
        """Load detailed patient information - delegate to service."""
        db = SessionLocal()
        try:
            self.patient_details = get_patient_details(db, username) or {}
            # Get all records first, then filter by date
            all_records = get_patient_records(db, username)
            
            # Apply date filtering
            if self.start_date and self.end_date:
                from datetime import datetime
                start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
                
                self.patient_records = [
                    record for record in all_records
                    if record.get('date') and start_date <= record['date'] <= end_date
                ]
            else:
                self.patient_records = all_records
        finally:
            db.close()
    
    def open_upload_form(self):
        """Show general upload form."""
        self.show_general_upload_form = True
        self.uploaded_files = []
    
    def hide_general_upload_form(self):
        """Hide the general upload form."""
        self.show_general_upload_form = False
        self.uploaded_files = []
    
    def clear_upload_message(self):
        """Clear the upload success message."""
        self.upload_success = False
        self.upload_message = ""
        self.show_upload_feedback = False
    
    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload - delegate to service."""
        result = await handle_file_upload(files)
        
        self.uploaded_files = result["uploaded_files"]
        self.upload_success = result["success"]
        self.upload_message = result["message"]
        self.show_upload_feedback = True
        
        self.hide_general_upload_form()
        self.load_patients()
    
    def clear_uploaded_files(self):
        """Clear all uploaded files."""
        self.uploaded_files = []

    def show_add_patient_form(self):
        """Show the add patient form."""
        self.show_add_form = True
    
    def hide_add_patient_form(self):
        """Hide the add patient form and reset fields."""
        self.show_add_form = False
        self.reset_form()
    
    def reset_form(self):
        """Reset all form fields."""
        self.form_name = ""
        self.form_gender = ""
        self.form_age = ""
        self.form_phone = ""
        self.form_moderate_hr_min = ""
        self.form_moderate_hr_max = ""
        self.form_vigorous_hr_min = ""
        self.form_vigorous_hr_max = ""
        self.form_target_duration = ""
        self.form_prompt_times = ""
        self.form_medical_condition = ""
        self.form_disability_level = ""
    
    def add_patient(self):
        """Add new patient - delegate to service."""
        patient_data = {
            "name": self.form_name,
            "gender": self.form_gender,
            "age": self.form_age,
            "phone": self.form_phone,
            "moderate_hr_min": self.form_moderate_hr_min,
            "moderate_hr_max": self.form_moderate_hr_max,
            "vigorous_hr_min": self.form_vigorous_hr_min,
            "vigorous_hr_max": self.form_vigorous_hr_max,
            "target_duration": self.form_target_duration,
            "prompt_times": self.form_prompt_times,
            "medical_condition": self.form_medical_condition,
            "disability_level": self.form_disability_level,
        }
        
        success = create_new_patient(patient_data)
        
        if success:
            self.hide_add_patient_form()
            self.load_patients()
        else:
            print("Failed to create patient")


def add_patient_form() -> rx.Component:
    """Add patient form component using Reflex built-in components."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.heading("Add New Patient", size="6", weight="bold"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            size="2",
                            on_click=PatientsState.hide_add_patient_form,
                        )
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                
                # Form fields in two columns
                rx.hstack(
                    # Left column
                    rx.vstack(
                        rx.vstack(
                            rx.text("Full Name", size="3", weight="medium"),
                            rx.input(
                                placeholder="Enter full name",
                                value=PatientsState.form_name,
                                on_change=PatientsState.set_form_name,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Gender", size="3", weight="medium"),
                            rx.select(
                                ["Male", "Female", "Other"],
                                placeholder="Select gender",
                                value=PatientsState.form_gender,
                                on_change=PatientsState.set_form_gender,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Age", size="3", weight="medium"),
                            rx.input(
                                placeholder="Enter age",
                                type="number",
                                value=PatientsState.form_age,
                                on_change=PatientsState.set_form_age,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Phone Number", size="3", weight="medium"),
                            rx.input(
                                placeholder="Enter phone number",
                                value=PatientsState.form_phone,
                                on_change=PatientsState.set_form_phone,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Moderate Heart Rate (Min)", size="3", weight="medium"),
                            rx.input(
                                placeholder="Min BPM",
                                type="number",
                                value=PatientsState.form_moderate_hr_min,
                                on_change=PatientsState.set_form_moderate_hr_min,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Moderate Heart Rate (Max)", size="3", weight="medium"),
                            rx.input(
                                placeholder="Max BPM",
                                type="number",
                                value=PatientsState.form_moderate_hr_max,
                                on_change=PatientsState.set_form_moderate_hr_max,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Right column
                    rx.vstack(
                        rx.vstack(
                            rx.text("Vigorous Heart Rate (Min)", size="3", weight="medium"),
                            rx.input(
                                placeholder="Min BPM",
                                type="number",
                                value=PatientsState.form_vigorous_hr_min,
                                on_change=PatientsState.set_form_vigorous_hr_min,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Vigorous Heart Rate (Max)", size="3", weight="medium"),
                            rx.input(
                                placeholder="Max BPM",
                                type="number",
                                value=PatientsState.form_vigorous_hr_max,
                                on_change=PatientsState.set_form_vigorous_hr_max,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Target Duration (minutes)", size="3", weight="medium"),
                            rx.input(
                                placeholder="Minutes per session",
                                type="number",
                                value=PatientsState.form_target_duration,
                                on_change=PatientsState.set_form_target_duration,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Prompt Times", size="3", weight="medium"),
                            rx.input(
                                placeholder="Times per day",
                                type="number",
                                value=PatientsState.form_prompt_times,
                                on_change=PatientsState.set_form_prompt_times,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Medical Condition", size="3", weight="medium"),
                            rx.text_area(
                                placeholder="Describe medical condition...",
                                value=PatientsState.form_medical_condition,
                                on_change=PatientsState.set_form_medical_condition,
                                rows="3",
                                resize="vertical",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.vstack(
                            rx.text("Disability Level", size="3", weight="medium"),
                            rx.select(
                                ["None", "Mild", "Moderate", "Severe"],
                                placeholder="Select disability level",
                                value=PatientsState.form_disability_level,
                                on_change=PatientsState.set_form_disability_level,
                                size="3",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                ),
                
                # File upload
                rx.vstack(
                    rx.text("Upload Files", size="3", weight="medium"),
                    rx.upload(
                        rx.vstack(
                            rx.text("Drag and drop DOCX files here, or click to select files"),
                            rx.text("(DOCX only)", size="2", color="#6B7280"),
                            spacing="1",
                        ),
                        accept={
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                        },
                        multiple=False,  # Single file only
                        border="2px dashed #D1D5DB",
                        padding="4",
                        border_radius="8px",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Action buttons
                rx.hstack(
                    rx.button(
                        "Cancel",
                        variant="outline",
                        size="3",
                        on_click=PatientsState.hide_add_patient_form,
                    ),
                    rx.button(
                        "Add",
                        bg="#181C62",
                        color="white",
                        size="3",
                        on_click=PatientsState.add_patient,
                        _hover={"bg": "#141A55"},
                    ),
                    spacing="3",
                    justify="end",
                    width="100%",
                ),
                
                spacing="6",
                width="100%",
            ),
            max_width="800px",
            padding="6",
        ),
        open=PatientsState.show_add_form,
    )


def upload_feedback_popup() -> rx.Component:
    """Upload feedback popup dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header with icon
                rx.hstack(
                    rx.icon(
                        rx.cond(PatientsState.upload_success, "check", "alert_triangle"),
                        size=32,
                        color=rx.cond(PatientsState.upload_success, "#10B981", "#EF4444")
                    ),
                    rx.heading(
                        rx.cond(PatientsState.upload_success, "Upload Successful!", "Upload Failed"),
                        size="6",
                        weight="bold",
                        color=rx.cond(PatientsState.upload_success, "#059669", "#DC2626")
                    ),
                    spacing="3",
                    align="center",
                    justify="center",
                    width="100%",
                ),
                
                # Message
                rx.text(
                    PatientsState.upload_message,
                    size="3",
                    color="#374151",
                    text_align="center",
                    line_height="1.6",
                ),
                
                # OK Button
                rx.button(
                    "OK",
                    bg=rx.cond(PatientsState.upload_success, "#10B981", "#EF4444"),
                    color="white",
                    size="3",
                    width="100%",
                    on_click=PatientsState.clear_upload_message,
                    _hover={
                        "bg": rx.cond(PatientsState.upload_success, "#059669", "#DC2626")
                    },
                ),
                
                spacing="5",
                align="center",
                width="100%",
            ),
            max_width="400px",
            padding="6",
        ),
        open=PatientsState.show_upload_feedback,
    )


def general_upload_form() -> rx.Component:
    """Simple upload form component."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.heading("Upload Records", size="7", weight="bold"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=18),
                            variant="ghost",
                            size="3",
                            on_click=PatientsState.hide_general_upload_form,
                        )
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                
                # Upload area
                rx.upload(
                    rx.vstack(
                        rx.icon("cloud_upload", size=48, color="#6B7280"),
                        rx.heading("Drop your DOCX file here", size="5", color="#374151"),
                        rx.text("or click to browse", size="3", color="#6B7280"),
                        rx.text("Supports: DOCX only", size="2", color="#9CA3AF"),
                        spacing="3",
                        align="center",
                    ),
                    accept={
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                    },
                    multiple=False,  # Single file only
                    border="3px dashed #D1D5DB",
                    border_radius="16px",
                    id="general_upload",
                    min_height="200px",
                    width="100%",
                    _hover={"border_color": "#9CA3AF", "bg": "#F9FAFB"},
                ),
                
                # Show selected files (before upload)
                rx.vstack(
                    rx.foreach(
                        rx.selected_files("general_upload"),
                        lambda file: rx.hstack(
                            rx.icon("file", size=14, color="#6B7280"),
                            rx.text(file, size="2", color="#374151"),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    spacing="1",
                    width="100%",
                ),
                
                # Upload button
                rx.button(
                    "Upload & Parse File",
                    on_click=PatientsState.handle_upload(
                        rx.upload_files(upload_id="general_upload")
                    ),
                    bg="#181C62",
                    color="white",
                    size="3",
                    width="100%",
                    _hover={"bg": "#141A55"},
                ),
                
                # Show uploaded files
                rx.cond(
                    PatientsState.uploaded_files.length() > 0,
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("check", size=16, color="#10B981"),
                                rx.text(
                                    "File Ready",
                                    size="3",
                                    color="#059669",
                                    weight="bold"
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon("trash", size=14),
                                    variant="ghost",
                                    size="1",
                                    color_scheme="red",
                                    on_click=PatientsState.clear_uploaded_files,
                                ),
                                align="center",
                                width="100%",
                            ),
                            rx.box(
                                rx.foreach(
                                    PatientsState.uploaded_files,
                                    lambda filename: rx.hstack(
                                        rx.icon("file", size=14, color="#6B7280"),
                                        rx.text(filename, size="2", color="#374151"),
                                        spacing="2",
                                        align="center",
                                        padding_y="1",
                                    ),
                                ),
                                max_height="120px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        bg="#ECFDF5",
                        border="1px solid #A7F3D0",
                        border_radius="8px",
                        padding="3",
                        width="100%",
                    ),
                ),
                

                
                spacing="6",
                width="100%",
            ),
            max_width="500px",
            padding="6",
        ),
        open=PatientsState.show_general_upload_form,
    )


def patient_row(patient: dict) -> rx.Component:
    """Patient table row component with expandable details."""
    return rx.fragment(
        # Main patient row - make entire row clickable
        rx.table.row(
            rx.table.cell(
                rx.text(patient["name"], color="#111827", weight="medium")
            ),
            rx.table.cell(
                rx.text(
                    rx.cond(patient["age"], patient["age"].to_string(), "N/A"),
                    color="#111827"
                )
            ),
            rx.table.cell(
                rx.badge(
                    rx.cond(patient["target_achieved"], "Yes", "No"),
                    color_scheme=rx.cond(patient["target_achieved"], "green", "red"),
                    variant="soft",
                )
            ),
            rx.table.cell(
                rx.text(
                    rx.cond(
                        patient["last_heart_rate"],
                        patient["last_heart_rate"].to_string() + " bpm",
                        "N/A"
                    ),
                    color="#111827"
                )
            ),
            rx.table.cell(
                rx.text(
                    rx.cond(
                        patient["created_at"],
                        patient["created_at"].to_string(),
                        "N/A"
                    ),
                    color="#111827"
                )
            ),
            on_click=lambda: PatientsState.toggle_patient_details(patient["username"]),
            cursor="pointer",
            _hover={
                "bg": "#F8FAFC",
                "transform": "scale(1.01)",
                "transition": "all 0.2s ease-in-out"
            },
        ),
        
        # Expandable details row (shown only if this patient is selected)
        rx.cond(
            PatientsState.expanded_patient_username == patient["username"],
            rx.table.row(
                rx.table.cell(
                    rx.box(
                        rx.vstack(
                            # Patient info header
                            rx.heading(
                                f"Patient Details: {patient['name']}",
                                size="5",
                                weight="bold",
                                color="#111827",
                                padding_bottom="4",
                            ),
                            
                            # Patient summary cards
                            rx.hstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("Age", size="2", color="#6B7280"),
                                        rx.text(
                                            rx.cond(patient["age"], patient["age"].to_string(), "N/A"),
                                            size="3",
                                            weight="bold",
                                            color="#111827"
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    bg="white",
                                    padding="3",
                                    border_radius="6px",
                                    border="1px solid #E5E7EB",
                                    flex="1",
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("Target Achieved", size="2", color="#6B7280"),
                                        rx.badge(
                                            rx.cond(patient["target_achieved"], "Yes", "No"),
                                            color_scheme=rx.cond(patient["target_achieved"], "green", "red"),
                                            variant="soft",
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    bg="white",
                                    padding="3",
                                    border_radius="6px",
                                    border="1px solid #E5E7EB",
                                    flex="1",
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("Last Heart Rate", size="2", color="#6B7280"),
                                        rx.text(
                                            rx.cond(
                                                patient["last_heart_rate"],
                                                patient["last_heart_rate"].to_string() + " bpm",
                                                "N/A"
                                            ),
                                            size="3",
                                            weight="bold",
                                            color="#111827"
                                        ),
                                        spacing="1",
                                        align="center",
                                    ),
                                    bg="white",
                                    padding="3",
                                    border_radius="6px",
                                    border="1px solid #E5E7EB",
                                    flex="1",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            
                            # Records section
                            rx.vstack(
                                rx.heading("Exercise Records", size="4", weight="bold", color="#111827"),
                                rx.cond(
                                    PatientsState.patient_records.length() > 0,
                                    rx.box(
                                        rx.table.root(
                                            rx.table.header(
                                                rx.table.row(
                                                    rx.table.column_header_cell(
                                                        rx.text("Date", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("Week", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("HR (Fat Burn)", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("HR MVPA", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("HR (Intense)", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("Total Mins", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("Weekly", color="#111827", weight="bold", size="2")
                                                    ),
                                                    rx.table.column_header_cell(
                                                        rx.text("Boost", color="#111827", weight="bold", size="2")
                                                    ),
                                                ),
                                            ),
                                            rx.table.body(
                                                rx.foreach(
                                                    PatientsState.patient_records,
                                                    patient_record_row,
                                                ),
                                            ),
                                            variant="surface",
                                            size="1",
                                        ),
                                        max_height="300px",
                                        overflow_y="auto",
                                    ),
                                    rx.box(
                                        rx.text(
                                            "No records found for this patient.",
                                            color="#6B7280",
                                            size="2",
                                            text_align="center",
                                        ),
                                        padding="4",
                                        bg="#F9FAFB",
                                        border_radius="6px",
                                        border="1px dashed #D1D5DB",
                                        width="100%",
                                    ),
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            
                            spacing="4",
                            width="100%",
                        ),
                        bg="#F8FAFC",
                        border_radius="8px",
                        border="1px solid #E2E8F0",
                        padding="4",
                        width="100%",
                    ),
                    col_span=5,  # Span across all table columns
                ),
            ),
        ),
    )


def patient_record_row(record: dict) -> rx.Component:
    """Patient record table row component."""
    return rx.table.row(
        rx.table.cell(
            rx.text(
                rx.cond(record["date"], record["date"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["week_description"], record["week_description"], "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["hr_fat_burn"], record["hr_fat_burn"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["hr_mvpa"], record["hr_mvpa"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["hr_intense"], record["hr_intense"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["total_mins_per_session"], record["total_mins_per_session"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["total_weekly"], record["total_weekly"].to_string(), "N/A"),
                color="#111827",
                size="2"
            )
        ),
        rx.table.cell(
            rx.text(
                rx.cond(record["boost"], record["boost"], "N/A"),
                color="#111827",
                size="2"
            )
        ),
    )


def patients_page() -> rx.Component:
    """Clean patients page using modular components."""
    return rx.cond(
        AuthState.is_authenticated,
        # Authenticated content
        rx.fragment(
            # Add patient form dialog
            add_patient_form(),
            
            # General upload form dialog
            general_upload_form(),
            
            # Upload feedback popup
            upload_feedback_popup(),
            
            # Main page content
            rx.box(
                page_layout(
                    rx.vstack(
                        rx.box(height="5px"),  
            # Header with date filters and add button
            rx.hstack(
                rx.box(width="10px"),  
                rx.heading("Patients", size="8", weight="bold", color="#111827"),
                rx.spacer(),
                # Date filter section
                rx.hstack(
                    rx.icon("calendar", size=16, color="#6B7280"),
                    rx.input(
                        type="date",
                        value=PatientsState.start_date,
                        on_change=PatientsState.set_start_date,
                        size="2",
                    ),
                    rx.text("-", color="#6B7280", size="3"),
                    rx.input(
                        type="date", 
                        value=PatientsState.end_date,
                        on_change=PatientsState.set_end_date,
                        size="2",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("plus", size=20),
                        rx.text("Add Patient"),
                        spacing="2",
                    ),
                    bg="#181C62",
                    color="white",
                    variant="outline",
                    on_click=PatientsState.show_add_patient_form,
                    _hover={"bg": "#141A55"},
                ),
                justify="between",
                align="center",
                width="100%",
                padding_bottom="8",
                spacing="4",
                margin_left="8",
            ),
            
            # Patients table
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell(
                                rx.text("Name", color="#111827", weight="bold")
                            ),
                            rx.table.column_header_cell(
                                rx.text("Age", color="#111827", weight="bold")
                            ),
                            rx.table.column_header_cell(
                                rx.text("Target Achieved", color="#111827", weight="bold")
                            ),
                            rx.table.column_header_cell(
                                rx.text("Last Heart Rate", color="#111827", weight="bold")
                            ),
                            rx.table.column_header_cell(
                                rx.text("Joined", color="#111827", weight="bold")
                            ),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            PatientsState.patients,
                            patient_row,
                        ),
                    ),
                    variant="surface",
                    size="3",
                ),
                bg="white",
                border_radius="12px",
                border="1px solid #E5E7EB",
                box_shadow="0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
                padding="8",
                width="100%",
            ),
            
                        spacing="6",
                        width="100%",
                    ),
                    "patients"
                ),
                on_mount=PatientsState.load_patients,
                position="relative",  # Enable positioning context
            ),
            
            # Floating Upload Record Button
            rx.box(
                rx.button(
                    rx.vstack(
                        rx.icon("upload", size=24, color="white"),
                        rx.text("Upload Record", size="3", weight="bold", color="white"),
                        spacing="1",
                        align="center",
                    ),
                    bg="#181C62",
                    _hover={"bg": "#141A55", "transform": "scale(1.05)"},
                    border_radius="16px",
                    padding="4",
                    box_shadow="0 8px 25px -8px rgba(0, 0, 0, 0.3)",
                    transition="all 0.2s ease-in-out",
                    cursor="pointer",
                    on_click=PatientsState.open_upload_form,
                    size="4",
                    height="auto",
                    min_height="80px",
                    min_width="120px",
                ),
                position="fixed",
                bottom="2rem",
                right="2rem",
                z_index="1000",
            ),
        ),
        # Not authenticated - show login prompt
        rx.container(
            rx.vstack(
                rx.heading("Access Denied", size="8", color="#EF4444"),
                rx.text("Please login to access patient data.", size="4", color="#6B7280"),
                rx.button(
                    "Go to Login",
                    on_click=lambda: rx.redirect("/"),
                    bg="#181C62",
                    color="white",
                    size="3",
                ),
                spacing="4",
                align="center",
            ),
            padding="8",
            max_width="400px",
            margin="0 auto",
            min_height="100vh",
            display="flex",
            align_items="center",
            justify_content="center",
        )
    ) 