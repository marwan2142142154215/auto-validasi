"""
Web Validators for Bank and E-Wallet Account Validation

This module handles:
- CIMB OCTO Validator (Bank validation)
- BCA E-Wallet Validator (E-wallet validation)
- Login/logout automation
- Account validation workflows
"""

import os
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from playwright.sync_api import Page, expect


@dataclass
class ValidationResult:
    """Result of account validation"""
    success: bool
    actual_name: str
    raw_result: str
    error_message: Optional[str] = None


class BaseValidator:
    """Base class for web validators"""
    
    def __init__(self, username: str, password: str, timeout_ms: int = 30000):
        """
        Initialize validator
        
        Args:
            username: Login username
            password: Login password
            timeout_ms: Timeout for page operations
        """
        self.username = username
        self.password = password
        self.timeout_ms = timeout_ms
        self.logged_in = False
    
    def _wait_for_element(self, page: Page, selector: str, timeout: int = None) -> None:
        """Wait for element to be visible"""
        timeout = timeout or self.timeout_ms
        try:
            element = page.locator(selector)
            element.wait_for(timeout=timeout, state="visible")
        except Exception:
            pass  # Continue even if not found
    
    def _click_element(self, page: Page, selector: str, timeout: int = None) -> bool:
        """Click element by selector"""
        timeout = timeout or self.timeout_ms
        try:
            element = page.locator(selector)
            element.wait_for(timeout=timeout, state="visible")
            element.click(timeout=timeout)
            return True
        except Exception as e:
            print(f"Error clicking {selector}: {e}")
            return False
    
    def _fill_input(self, page: Page, selector: str, value: str, timeout: int = None) -> bool:
        """Fill input field"""
        timeout = timeout or self.timeout_ms
        try:
            element = page.locator(selector)
            element.wait_for(timeout=timeout, state="visible")
            element.fill(value)
            return True
        except Exception as e:
            print(f"Error filling {selector}: {e}")
            return False
    
    def _get_text(self, page: Page, selector: str, timeout: int = None) -> str:
        """Get text content from element"""
        timeout = timeout or self.timeout_ms
        try:
            element = page.locator(selector)
            element.wait_for(timeout=timeout, state="visible")
            return element.text_content() or ""
        except Exception:
            return ""
    
    def _screenshot(self, page: Page, path: str, full_page: bool = True) -> bool:
        """Take screenshot"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            page.screenshot(path=path, full_page=full_page)
            return True
        except Exception:
            return False


class CimbOctoValidator(BaseValidator):
    """Validator for CIMB OCTO Bank Validation"""
    
    def __init__(self, username: str, password: str, timeout_ms: int = 30000):
        super().__init__(username, password, timeout_ms)
        self.base_url = "https://www.cimbocto.co.id/login"
    
    def login(self, page: Page) -> bool:
        """
        Login to CIMB OCTO
        
        Args:
            page: Playwright page
        
        Returns:
            True if login successful
        """
        try:
            print("Opening CIMB OCTO login page...")
            page.goto(self.base_url, timeout=self.timeout_ms)
            
            # Fill username
            print("Entering username...")
            if not self._fill_input(page, "/html/body/div/div[2]/div/div[2]/div/div/form/div[1]/div[1]/div/input", self.username):
                return False
            
            # Fill password
            print("Entering password...")
            if not self._fill_input(page, "/html/body/div/div[2]/div/div[2]/div/div/form/div[2]/div[1]/div/div/input", self.password):
                return False
            
            # Click login button (if exists)
            print("Clicking login button...")
            self._click_element(page, "/html/body/div/div[2]/div/div[2]/div/div/form/div[3]/button")
            
            # Wait for login to complete
            time.sleep(3)
            
            self.logged_in = True
            print("✓ CIMB OCTO login successful")
            return True
        
        except Exception as e:
            print(f"Error during CIMB OCTO login: {e}")
            return False
    
    def navigate_to_validation(self, page: Page) -> bool:
        """
        Navigate to account validation page
        
        Args:
            page: Playwright page
        
        Returns:
            True if navigation successful
        """
        try:
            if not self.logged_in:
                if not self.login(page):
                    return False
            
            # Click Transfer menu
            print("Navigating to Transfer menu...")
            if not self._click_element(page, "/html/body/div/div/nav/ul/li[2]/a/span"):
                return False
            
            time.sleep(1)
            
            # Click Validasi Rekening
            print("Opening Validasi Rekening...")
            if not self._click_element(page, "/html/body/div/div/nav/ul/li[2]/ul/li[2]/a"):
                return False
            
            time.sleep(1)
            
            # Click the validation card
            print("Opening validation form...")
            if not self._click_element(page, "/html/body/div/div/main/div/div[2]/div[3]"):
                return False
            
            time.sleep(2)
            print("✓ Navigated to validation page")
            return True
        
        except Exception as e:
            print(f"Error navigating to validation: {e}")
            return False
    
    def validate_account(
        self,
        page: Page,
        bank_name: str,
        account_number: str,
        nominal: str = "20000"
    ) -> ValidationResult:
        """
        Validate bank account
        
        Args:
            page: Playwright page
            bank_name: Bank name to select
            account_number: Account number to validate
            nominal: Amount for validation (default: 20000)
        
        Returns:
            ValidationResult with actual name
        """
        try:
            # Navigate to validation if not already there
            if not self._is_on_validation_page(page):
                if not self.navigate_to_validation(page):
                    return ValidationResult(
                        success=False,
                        actual_name="",
                        raw_result="",
                        error_message="Failed to navigate to validation page"
                    )
            
            # Select bank
            print(f"Selecting bank: {bank_name}")
            if not self._fill_input(page, "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[1]/div[1]/div/div/input[1]", bank_name):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to fill bank name"
                )
            
            time.sleep(1)
            
            # Click to confirm bank selection
            self._click_element(page, "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[1]/div[1]/div/ul/li/div")
            
            time.sleep(1)
            
            # Enter account number
            print(f"Entering account number: {account_number}")
            if not self._fill_input(page, "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[2]/div[1]", account_number):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to fill account number"
                )
            
            # Enter nominal
            print(f"Entering nominal: {nominal}")
            if not self._fill_input(page, "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[3]/div/div[1]", nominal):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to fill nominal"
                )
            
            # Click validate button
            print("Clicking validate button...")
            if not self._click_element(page, "/html/body/div/div/main/div/form/div[2]/div/div/button"):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to click validate button"
                )
            
            # Wait for result
            time.sleep(3)
            
            # Get result
            raw_result = self._get_text(page, "/html/body/div/div/main/div/form/div[1]/div[2]/div[1]/div[2]")
            
            # Extract name from result
            actual_name = self._extract_name_from_result(raw_result)
            
            print(f"Validation result: {actual_name}")
            
            return ValidationResult(
                success=True,
                actual_name=actual_name,
                raw_result=raw_result
            )
        
        except Exception as e:
            return ValidationResult(
                success=False,
                actual_name="",
                raw_result="",
                error_message=str(e)
            )
    
    def _is_on_validation_page(self, page: Page) -> bool:
        """Check if currently on validation page"""
        try:
            # Check for validation form elements
            element = page.locator("/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[1]/div[1]/div/div/input[1]")
            return element.count() > 0
        except Exception:
            return False
    
    def _extract_name_from_result(self, raw_result: str) -> str:
        """Extract account holder name from raw validation result"""
        if not raw_result:
            return ""
        
        # Clean up the result
        result = raw_result.strip()
        
        # Remove common prefixes
        result = result.replace("Nama:", "").replace("Name:", "").strip()
        result = result.replace("ACCOUNT HOLDER:", "").strip()
        
        return result
    
    def logout(self, page: Page) -> bool:
        """
        Logout from CIMB OCTO
        
        Args:
            page: Playwright page
        
        Returns:
            True if logout successful
        """
        try:
            if self.logged_in:
                print("Logging out from CIMB OCTO...")
                self._click_element(page, "/html/body/div/div/nav/div[2]/button")
                time.sleep(2)
                self.logged_in = False
                print("✓ CIMB OCTO logged out")
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False


class KlikBcaEwalletValidator(BaseValidator):
    """Validator for BCA E-Wallet Validation (KlikBCA)"""
    
    def __init__(self, username: str, password: str, timeout_ms: int = 30000):
        super().__init__(username, password, timeout_ms)
        self.base_url = "https://ibank.klikbca.com/"
    
    def login(self, page: Page) -> bool:
        """
        Login to KlikBCA
        
        Args:
            page: Playwright page
        
        Returns:
            True if login successful
        """
        try:
            print("Opening KlikBCA login page...")
            page.goto(self.base_url, timeout=self.timeout_ms)
            
            # Fill username
            print("Entering username...")
            if not self._fill_input(page, "/html/body/table[2]/tbody/tr/td[2]/div/table[1]/tbody/tr[4]/td/input", self.username):
                return False
            
            # Fill password
            print("Entering password...")
            if not self._fill_input(page, "/html/body/table[2]/tbody/tr/td[2]/div/table[1]/tbody/tr[9]/td/input", self.password):
                return False
            
            # Click login button
            print("Clicking login button...")
            if not self._click_element(page, "/html/body/table[2]/tbody/tr/td[2]/div/form/table/tbody/tr/td/input"):
                return False
            
            # Wait for login to complete
            time.sleep(3)
            
            self.logged_in = True
            print("✓ KlikBCA login successful")
            return True
        
        except Exception as e:
            print(f"Error during KlikBCA login: {e}")
            return False
    
    def navigate_to_validation(self, page: Page) -> bool:
        """
        Navigate to e-wallet validation page
        
        Args:
            page: Playwright page
        
        Returns:
            True if navigation successful
        """
        try:
            if not self.logged_in:
                if not self.login(page):
                    return False
            
            # Click Info Rekening menu
            print("Navigating to Info Rekening...")
            if not self._click_element(page, "/html/body/table/tbody/tr/td[2]/table/tbody/tr[7]/td/a/font/b"):
                return False
            
            time.sleep(1)
            
            # Click Validasi VA
            print("Opening Validasi VA...")
            if not self._click_element(page, "/html/body/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr[4]/td[2]/font/a"):
                return False
            
            time.sleep(2)
            print("✓ Navigated to VA validation page")
            return True
        
        except Exception as e:
            print(f"Error navigating to validation: {e}")
            return False
    
    def validate_account(self, page: Page, account_number: str) -> ValidationResult:
        """
        Validate e-wallet account
        
        Args:
            page: Playwright page
            account_number: Account number to validate
        
        Returns:
            ValidationResult with actual name
        """
        try:
            # Navigate to validation if not already there
            if not self._is_on_validation_page(page):
                if not self.navigate_to_validation(page):
                    return ValidationResult(
                        success=False,
                        actual_name="",
                        raw_result="",
                        error_message="Failed to navigate to validation page"
                    )
            
            # Enter account number
            print(f"Entering account number: {account_number}")
            if not self._fill_input(page, "/html/body/form/table[3]/tbody/tr[3]/td[3]/input", account_number):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to fill account number"
                )
            
            # Click validate button
            print("Clicking validate button...")
            if not self._click_element(page, "/html/body/form/table[4]/tbody/tr[2]/td/input"):
                return ValidationResult(
                    success=False,
                    actual_name="",
                    raw_result="",
                    error_message="Failed to click validate button"
                )
            
            # Wait for result
            time.sleep(3)
            
            # Get result
            raw_result = self._get_text(page, "/html/body/form/table[3]/tbody/tr[3]/td[3]")
            
            # Extract name from result
            actual_name = self._extract_name_from_result(raw_result)
            
            print(f"Validation result: {actual_name}")
            
            return ValidationResult(
                success=True,
                actual_name=actual_name,
                raw_result=raw_result
            )
        
        except Exception as e:
            return ValidationResult(
                success=False,
                actual_name="",
                raw_result="",
                error_message=str(e)
            )
    
    def _is_on_validation_page(self, page: Page) -> bool:
        """Check if currently on validation page"""
        try:
            element = page.locator("/html/body/form/table[3]/tbody/tr[3]/td[3]/input")
            return element.count() > 0
        except Exception:
            return False
    
    def _extract_name_from_result(self, raw_result: str) -> str:
        """Extract account holder name from raw validation result"""
        if not raw_result:
            return ""
        
        result = raw_result.strip()
        
        # Remove common prefixes
        result = result.replace("DNID", "").strip()
        result = result.replace("Nama:", "").replace("Name:", "").strip()
        result = result.replace("VA", "").strip()
        
        return result
    
    def logout(self, page: Page) -> bool:
        """
        Logout from KlikBCA
        
        Args:
            page: Playwright page
        
        Returns:
            True if logout successful
        """
        try:
            if self.logged_in:
                print("Logging out from KlikBCA...")
                self._click_element(page, "/html/body/div/font/b/a")
                time.sleep(2)
                self.logged_in = False
                print("✓ KlikBCA logged out")
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("Web Validators Module")
    print("=" * 50)
    print("Available validators:")
    print("  - CimbOctoValidator: For bank account validation")
    print("  - KlikBcaEwalletValidator: For e-wallet validation")
    print("\nUsage:")
    print("  validator = CimbOctoValidator(username, password)")
    print("  validator.login(page)")
    print("  result = validator.validate_account(page, 'Bank Central Asia', '25449874')")
