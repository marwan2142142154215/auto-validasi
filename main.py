"""
AutoID Validator - Main Application

This is the main entry point for the account validation system.
It orchestrates:
- Reading data from Google Sheets
- Validating bank/e-wallet accounts via web automation
- Sending results to Telegram
- Updating Google Sheets with results

Usage:
    python main.py [--demo] [--headless] [--max-rows N]

Options:
    --demo      Run in demo mode (no actual browser)
    --headless  Run browser in headless mode
    --max-rows  Maximum number of rows to process
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright

# Import our modules
from config import (
    GOOGLE_SHEET_ID, GOOGLE_SHEET_GID, GOOGLE_SHEET_RANGE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    CIMB_USERNAME, CIMB_PASSWORD,
    BCA_USERNAME, BCA_PASSWORD,
    HEADLESS, SLOW_MO_MS, TIMEOUT_MS, POLL_INTERVAL_SEC, MAX_ROWS_PER_RUN, NOMINAL,
    BANK_MAPPING, EWALLET_LIST
)
from name_match import compare_names, is_invalid_account, is_ewallet_not_premium
from telegram_client import TelegramClient
from sheets_client import SheetsClient, RowData, DemoSheetsClient
from web_validators import CimbOctoValidator, KlikBcaEwalletValidator


def resolve_bank_display(kind: str) -> tuple[str, bool]:
    """Resolve bank display name and check if e-wallet"""
    k = SheetsClient.normalize_kind(kind)
    is_ew = k in EWALLET_LIST
    display = BANK_MAPPING.get(k, kind)
    return display, is_ew


def should_process(row: RowData) -> bool:
    """Check if row should be processed"""
    return not row.status or row.status.strip() == ""


def determine_status(expected_name: str, norek: str, is_ewallet: bool, validation_text: str) -> tuple[str, str, str]:
    """
    Determine validation status based on validation result
    
    Returns: (status, actual_name, details)
    """
    raw = (validation_text or "").strip()
    
    # Check for invalid account first
    if is_invalid_account(raw):
        return "REK TIDAK VALID", raw, "Virtual Account tidak ditemukan"
    
    # Check for empty result
    if not raw:
        return "REK TIDAK VALID", raw, "Tidak ada hasil validasi"
    
    # Check for e-wallet non-premium
    if is_ewallet and is_ewallet_not_premium(norek=norek, actual_name=raw):
        return "REK BELUM PREMIUM", raw, f"Account tidak premium (menampilkan nomor)"
    
    # Compare names
    match_result = compare_names(expected_name, raw)
    return match_result.status, match_result.actual_name, match_result.details


def get_screenshot_path(row_index: int) -> str:
    """Get path for screenshot file"""
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    return os.path.join(screenshots_dir, f"row{row_index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")


def process_bank_validation(
    page: Page,
    validator: CimbOctoValidator,
    bank_display: str,
    norek: str,
    row_index: int
) -> tuple[str, str, str]:
    """
    Process bank validation
    
    Returns: (status, actual_name, screenshot_path)
    """
    screenshot_path = get_screenshot_path(row_index)
    
    result = validator.validate_account(page, bank_display, norek, NOMINAL)
    
    # Take screenshot
    try:
        page.screenshot(path=screenshot_path, full_page=True)
    except Exception:
        screenshot_path = ""
    
    return result.actual_name, result.raw_result, screenshot_path


def process_ewallet_validation(
    page: Page,
    validator: KlikBcaEwalletValidator,
    norek: str,
    row_index: int
) -> tuple[str, str, str]:
    """
    Process e-wallet validation
    
    Returns: (status, actual_name, screenshot_path)
    """
    screenshot_path = get_screenshot_path(row_index)
    
    result = validator.validate_account(page, norek)
    
    # Take screenshot
    try:
        page.screenshot(path=screenshot_path, full_page=True)
    except Exception:
        screenshot_path = ""
    
    return result.actual_name, result.raw_result, screenshot_path


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="AutoID Validator")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-rows", type=int, default=0, help="Maximum rows to process")
    parser.add_argument("--slow", type=int, default=SLOW_MO_MS, help="Slow motion in ms")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 AutoID Validator - Bank & E-Wallet Validation System")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DEMO' if args.demo else 'PRODUCTION'}")
    print(f"Headless: {args.headless or HEADLESS}")
    print(f"Max Rows: {args.max_rows or MAX_ROWS_PER_RUN or 'Unlimited'}")
    print("=" * 60)
    
    # Initialize clients
    if args.demo:
        print("\n📋 Initializing DEMO mode (no Google Sheets)...")
        sheets = DemoSheetsClient([
            {"name": "Marwan", "norek": "25449874", "kind": "bca"},
            {"name": "Ahmad", "norek": "1234567890", "kind": "mandiri"},
            {"name": "Budi", "norek": "3901082276553476", "kind": "dana"},
        ])
    else:
        print("\n📋 Initializing Google Sheets client...")
        sheets = SheetsClient(
            service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
            sheet_id=GOOGLE_SHEET_ID,
            gid=GOOGLE_SHEET_GID
        )
    
    print("📱 Initializing Telegram client...")
    tg = TelegramClient(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # Send start notification
    tg.send_message("🚀 AutoID Validator Started\n\nMode: Production\nReady for validations!")
    
    # Read queue
    max_rows = args.max_rows or MAX_ROWS_PER_RUN
    rows = sheets.read_queue(start_row=9, max_rows=max_rows)
    
    if not rows:
        print("\n❌ No rows to process or error reading spreadsheet")
        return
    
    pending_count = sum(1 for r in rows if should_process(r))
    print(f"\n📊 Found {len(rows)} rows, {pending_count} pending validation")
    
    # Initialize validators
    cimb_validator = CimbOctoValidator(CIMB_USERNAME, CIMB_PASSWORD, TIMEOUT_MS)
    bca_validator = KlikBcaEwalletValidator(BCA_USERNAME, BCA_PASSWORD, TIMEOUT_MS)
    
    # Track login state
    cimb_ready = False
    bca_ready = False
    
    # Process rows
    processed = 0
    successful = 0
    failed = 0
    
    with sync_playwright() as p:
        # Launch browser
        headless = args.headless or HEADLESS
        slow_mo = args.slow
        
        print(f"\n🌐 Launching browser (headless={headless}, slow_mo={slow_mo}ms)...")
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        
        # Create pages
        cimb_page = context.new_page()
        bca_page = context.new_page()
        
        try:
            for row in rows:
                if not should_process(row):
                    print(f"\n⏭️  Skipping row {row.row_index} (already processed)")
                    continue
                
                print(f"\n{'='*60}")
                print(f"📝 Processing Row {row.row_index}")
                print(f"   Type: {row.kind} | No. Rek: {row.norek} | Name: {row.expected_name}")
                print(f"{'='*60}")
                
                bank_display, is_ewallet = resolve_bank_display(row.kind)
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                caption = f"[{timestamp}] {row.kind} | norek={row.norek} | expected={row.expected_name}"
                
                try:
                    if is_ewallet:
                        # E-wallet validation via KlikBCA
                        if not bca_ready:
                            print("\n🔐 Logging into KlikBCA...")
                            if bca_validator.login(bca_page):
                                bca_ready = True
                                print("✓ KlikBCA login successful")
                            else:
                                print("❌ KlikBCA login failed")
                                failed += 1
                                continue
                        
                        print(f"\n🔍 Validating e-wallet account: {row.norek}")
                        actual_name, raw_result, screenshot_path = process_ewallet_validation(
                            bca_page, bca_validator, row.norek, row.row_index
                        )
                    else:
                        # Bank validation via CIMB OCTO
                        if not cimb_ready:
                            print("\n🔐 Logging into CIMB OCTO...")
                            if cimb_validator.login(cimb_page):
                                cimb_ready = True
                                print("✓ CIMB OCTO login successful")
                            else:
                                print("❌ CIMB OCTO login failed")
                                failed += 1
                                continue
                        
                        print(f"\n🔍 Validating bank account: {bank_display} - {row.norek}")
                        actual_name, raw_result, screenshot_path = process_bank_validation(
                            cimb_page, cimb_validator, bank_display, row.norek, row.row_index
                        )
                    
                    # Determine status
                    status, actual_name_result, details = determine_status(
                        row.expected_name, row.norek, is_ewallet, raw_result
                    )
                    
                    print(f"\n✅ Validation Result:")
                    print(f"   Status: {status}")
                    print(f"   Actual Name: {actual_name_result}")
                    print(f"   Details: {details}")
                    
                    # Upload screenshot to Telegram
                    screenshot_url = ""
                    if screenshot_path and os.path.exists(screenshot_path):
                        print(f"\n📤 Uploading screenshot to Telegram...")
                        tg_result = tg.send_photo(screenshot_path, caption=f"{caption}\nstatus={status}\nactual={actual_name_result}")
                        if tg_result.success:
                            screenshot_url = tg_result.direct_url or ""
                            print(f"✓ Screenshot uploaded: {screenshot_url}")
                        else:
                            print(f"❌ Failed to upload screenshot: {tg_result.error_message}")
                    
                    # Update Google Sheets
                    print(f"\n💾 Updating spreadsheet...")
                    update_success = sheets.update_result(
                        row_index=row.row_index,
                        status=status,
                        actual_name=actual_name_result,
                        screenshot_url=screenshot_url
                    )
                    
                    if update_success:
                        print(f"✓ Spreadsheet updated")
                        successful += 1
                    else:
                        print(f"❌ Failed to update spreadsheet")
                        failed += 1
                    
                    processed += 1
                    
                    # Send Telegram notification
                    tg.send_validation_result(
                        status=status,
                        bank_type=row.kind,
                        norek=row.norek,
                        expected_name=row.expected_name,
                        actual_name=actual_name_result,
                        screenshot_path=screenshot_path,
                        details=details
                    )
                    
                    # Wait between validations
                    time.sleep(POLL_INTERVAL_SEC)
                
                except Exception as e:
                    print(f"\n❌ Error processing row {row.row_index}: {e}")
                    failed += 1
                    
                    # Try to recover
                    try:
                        tg.send_message(f"❌ Error processing row {row.row_index}:\n{e}")
                    except Exception:
                        pass
        
        finally:
            # Logout
            print("\n🔒 Logging out...")
            if cimb_ready:
                try:
                    cimb_validator.logout(cimb_page)
                except Exception as e:
                    print(f"Error logging out CIMB: {e}")
            
            if bca_ready:
                try:
                    bca_validator.logout(bca_page)
                except Exception as e:
                    print(f"Error logging out KlikBCA: {e}")
            
            # Close browser
            context.close()
            browser.close()
            
            print("✓ Browser closed")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION COMPLETE")
    print("=" * 60)
    print(f"Total Rows: {len(rows)}")
    print(f"Processed: {processed}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Send completion notification
    tg.send_message(
        f"🏁 AutoID Validator Completed\n\n"
        f"Processed: {processed}\n"
        f"Successful: {successful} ✅\n"
        f"Failed: {failed} ❌"
    )


if __name__ == "__main__":
    main()
