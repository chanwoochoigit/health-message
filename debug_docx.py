#!/usr/bin/env python3
"""Debug script to test DOCX parsing directly."""

import pathlib
import docx2txt
import re

def parse_participant_data_block(text_block: str, participant_id: str) -> list[dict]:
    """
    Parses a single participant's data block, extracting structured information
    including date, activity metrics, week number, and notes.
    Adds placeholder rows for weeks without daily data entries.

    Args:
        text_block: The raw text block for a single participant, starting with headers.
        participant_id: The ID of the participant this block belongs to (e.g., 'ABCP123').

    Returns:
        A list of dictionaries, where each dictionary represents a parsed row
        of daily activity data for the participant or a placeholder for a week
        without data.
    """
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


def parse_all_participant_data(full_text: str) -> list[dict]:
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
                parsed_block_data = parse_participant_data_block(data_block, participant_id)
                all_parsed_data.extend(parsed_block_data)
            i += 2
        else:
            break
    return all_parsed_data


if __name__ == "__main__":
    # Update this path to your DOCX file
    docx_path = pathlib.Path("uploaded_files/data_sample.docx")
    
    record_txt = docx2txt.process(docx_path)
    parsed_data_output = parse_all_participant_data(record_txt)

    import json
    print("--- Complete Parsed Data ---")
    print(json.dumps(parsed_data_output, indent=2))

    # Demonstrate filtering for rows with specific "Notes"
    print("\n--- Rows with 'Notes' (Reasons for less activity) ---")
    excuse_rows = [
        row for row in parsed_data_output
        if row.get('Notes') is not None
    ]

    if excuse_rows:
        for row in excuse_rows:
            print(f"Participant: {row.get('participant_id')}, "
                  f"Week: {row.get('Week_Number')}, "
                  f"Date: {row.get('Date')}, "
                  f"Notes: {row.get('Notes')}")
    else:
        print("No rows found with specific 'Notes'.")