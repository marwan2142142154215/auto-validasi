"""
Google Sheets Client for reading and writing validation data

This module handles:
- Reading validation queue from spreadsheet
- Writing validation results back to spreadsheet
- Managing spreadsheet structure and formatting
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


@dataclass
class RowData:
    """Data for a single row in the spreadsheet"""
    row_index: int  # 1-based row index
    expected_name: str  # Column D (name to validate)
    norek: str  # Column E (account number)
    kind: str  # Column F (bank/ewallet type)
    status: str  # Column G (validation result)
    actual_name: str  # Column H (actual name from validation)
    screenshot_url: str  # Column I (screenshot link)


class SheetsClient:
    """Client for interacting with Google Sheets API"""
    
    def __init__(self, service_account_json: str = None, sheet_id: str = None, gid: str = None):
        """
        Initialize Google Sheets client
        
        Args:
            service_account_json: Path to service account JSON or JSON string
            sheet_id: Google Sheet ID
            gid: Sheet GID (worksheet ID)
        """
        self.sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID")
        self.gid = gid or os.getenv("GOOGLE_SHEET_GID")
        self._service = None
        
        # Initialize Google Sheets API
        if GOOGLE_AVAILABLE:
            self._init_service(service_account_json)
        else:
            print("Warning: Google Sheets API not available. Install google-auth and google-api-python-client")
    
    def _init_service(self, service_account_json: str = None):
        """Initialize Google Sheets service"""
        try:
            # Get credentials from env or file
            creds_json = service_account_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            
            if not creds_json:
                print("Warning: No Google credentials provided")
                return
            
            # Parse credentials
            if os.path.exists(creds_json):
                with open(creds_json, "r") as f:
                    creds_info = json.load(f)
            else:
                creds_info = json.loads(creds_json)
            
            # Create credentials
            credentials = Credentials.from_service_account_info(
                creds_info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            
            # Build service
            self._service = build("sheets", "v4", credentials=credentials)
            print("✓ Google Sheets API initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Google Sheets API: {e}")
            self._service = None
    
    def read_queue(self, start_row: int = 9, max_rows: int = 0) -> List[RowData]:
        """
        Read validation queue from spreadsheet
        
        Args:
            start_row: Starting row number (1-based)
            max_rows: Maximum rows to read (0 = all)
        
        Returns:
            List of RowData objects
        """
        if not self._service:
            print("Warning: Google Sheets service not available")
            return []
        
        try:
            # Determine range
            range_prefix = "D"  # Start from column D (name)
            range_suffix = f"I{start_row + max_rows if max_rows > 0 else ''}"
            range_name = f"Sheet1!{range_prefix}{start_row}:{range_suffix}"
            
            # Read data
            result = self._service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            
            rows = []
            for i, row in enumerate(values):
                if max_rows > 0 and i >= max_rows:
                    break
                
                # Extract data (columns D, E, F, G, H, I)
                expected_name = row[0] if len(row) > 0 else ""
                norek = row[1] if len(row) > 1 else ""
                kind = row[2] if len(row) > 2 else ""
                status = row[3] if len(row) > 3 else ""
                actual_name = row[4] if len(row) > 4 else ""
                screenshot_url = row[5] if len(row) > 5 else ""
                
                rows.append(RowData(
                    row_index=start_row + i,
                    expected_name=expected_name,
                    norek=norek,
                    kind=kind,
                    status=status,
                    actual_name=actual_name,
                    screenshot_url=screenshot_url
                ))
            
            return rows
        
        except Exception as e:
            print(f"Error reading spreadsheet: {e}")
            return []
    
    def update_result(
        self,
        row_index: int,
        status: str,
        actual_name: str,
        screenshot_url: str = None
    ) -> bool:
        """
        Update validation result in spreadsheet
        
        Args:
            row_index: Row number (1-based)
            status: Validation status
            actual_name: Actual name from validation
            screenshot_url: Screenshot URL from Telegram
        
        Returns:
            True if successful
        """
        if not self._service:
            print("Warning: Google Sheets service not available")
            return False
        
        try:
            # Prepare update data
            values = [[status, actual_name, screenshot_url or ""]]
            
            # Update columns G, H, I (status, actual_name, screenshot_url)
            range_name = f"Sheet1!G{row_index}:I{row_index}"
            
            result = self._service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": values}
            ).execute()
            
            return result.get("updatedCells", 0) > 0
        
        except Exception as e:
            print(f"Error updating spreadsheet: {e}")
            return False
    
    def update_status_only(self, row_index: int, status: str) -> bool:
        """Update only the status column"""
        return self.update_result(row_index, status, "", "")
    
    def mark_as_valid(self, row_index: int, actual_name: str, screenshot_url: str = None) -> bool:
        """Mark row as VALID"""
        return self.update_result(row_index, "VALID", actual_name, screenshot_url)
    
    def mark_as_invalid(self, row_index: int, actual_name: str = "", screenshot_url: str = None) -> bool:
        """Mark row as REK TIDAK VALID"""
        return self.update_result(row_index, "REK TIDAK VALID", actual_name, screenshot_url)
    
    def mark_as_not_premium(self, row_index: int, actual_name: str, screenshot_url: str = None) -> bool:
        """Mark row as REK BELUM PREMIUM"""
        return self.update_result(row_index, "REK BELUM PREMIUM", actual_name, screenshot_url)
    
    def mark_as_different_name(self, row_index: int, actual_name: str, screenshot_url: str = None) -> bool:
        """Mark row as REK BEDA NAMA"""
        return self.update_result(row_index, "REK BEDA NAMA", actual_name, screenshot_url)
    
    def mark_as_incomplete_name(self, row_index: int, actual_name: str, screenshot_url: str = None) -> bool:
        """Mark row as REK NAMA TIDAK LENGKAP"""
        return self.update_result(row_index, "REK NAMA TIDAK LENGKAP", actual_name, screenshot_url)
    
    def get_pending_count(self, start_row: int = 9) -> int:
        """Get count of pending validations"""
        rows = self.read_queue(start_row=start_row, max_rows=1000)
        return sum(1 for r in rows if not r.status or r.status.strip() == "")
    
    def should_process(self, row: RowData) -> bool:
        """Check if row should be processed"""
        return not row.status or row.status.strip() == ""
    
    @staticmethod
    def normalize_kind(kind: str) -> str:
        """Normalize bank/ewallet type name"""
        if not kind:
            return ""
        return kind.lower().strip()
    
    @staticmethod
    def is_ewallet(kind: str) -> bool:
        """Check if type is e-wallet"""
        normalized = SheetsClient.normalize_kind(kind)
        ewallets = ["gopay", "ovo", "dana", "linkaja", "shopeepay"]
        return normalized in ewallets


# Demo/Test mode when no Google credentials
class DemoSheetsClient:
    """Demo client for testing without Google credentials"""
    
    def __init__(self, demo_data: List[Dict] = None):
        self.demo_data = demo_data or []
        self.updates: List[Dict] = []
    
    def read_queue(self, start_row: int = 9, max_rows: int = 0) -> List[RowData]:
        rows = []
        for i, data in enumerate(self.demo_data):
            if max_rows > 0 and i >= max_rows:
                break
            rows.append(RowData(
                row_index=start_row + i,
                expected_name=data.get("name", ""),
                norek=data.get("norek", ""),
                kind=data.get("kind", ""),
                status="",
                actual_name="",
                screenshot_url=""
            ))
        return rows
    
    def update_result(self, row_index: int, status: str, actual_name: str, screenshot_url: str = None) -> bool:
        self.updates.append({
            "row": row_index,
            "status": status,
            "actual_name": actual_name,
            "screenshot_url": screenshot_url
        })
        return True


# Example usage
if __name__ == "__main__":
    # Test with demo mode
    demo_data = [
        {"name": "Marwan", "norek": "25449874", "kind": "bca"},
        {"name": "Ahmad", "norek": "1234567890", "kind": "mandiri"},
        {"name": "Budi", "norek": "3901082276553476", "kind": "dana"},
    ]
    
    client = DemoSheetsClient(demo_data)
    rows = client.read_queue()
    
    print("Demo Mode - Reading queue:")
    for row in rows:
        print(f"  Row {row.row_index}: {row.kind} | {row.norek} | {row.expected_name}")
    
    print("\nUpdating results:")
    for row in rows:
        client.update_result(row.row_index, "VALID", f"Result for {row.expected_name}", "https://t.me/...")
        print(f"  ✓ Row {row.row_index} updated")
    
    print("\nUpdates made:", client.updates)
