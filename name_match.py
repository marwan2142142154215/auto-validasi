"""
Name Matching and Validation Logic

This module handles the comparison between expected names and actual validation results.
It determines the validation status based on:
- VALID: Names match exactly or closely enough
- REK TIDAK VALID: No name found or invalid account
- REK BELUM PREMIUM: E-wallet account not premium (same number and name)
- REK BEDA NAMA: Names are completely different
- REK NAMA TIDAK LENGKAP: Names match partially but incomplete
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MatchResult:
    """Result of name comparison"""
    status: str  # VALID, REK TIDAK VALID, REK BELUM PREMIUM, REK BEDA NAMA, REK NAMA TIDAK LENGKAP
    confidence: float  # 0.0 to 1.0
    expected_name: str
    actual_name: str
    details: str = ""


def normalize_name(name: str) -> str:
    """Normalize name for comparison"""
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove common prefixes/suffixes
    name = re.sub(r'^dnid\s+', '', name)
    name = re.sub(r'\s+dnid$', '', name)
    name = re.sub(r'^va\s+', '', name)
    name = re.sub(r'\s+va$', '', name)
    
    # Remove special characters but keep spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def calculate_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names using multiple methods"""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    
    if not n1 or not n2:
        return 0.0
    
    # Exact match
    if n1 == n2:
        return 1.0
    
    # Token-based comparison
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # Jaccard similarity for tokens
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    jaccard = intersection / union if union > 0 else 0.0
    
    # Length-based similarity
    len_ratio = min(len(n1), len(n2)) / max(len(n1), len(n2))
    
    # Check if one is substring of other
    substring_bonus = 0.0
    if n1 in n2 or n2 in n1:
        substring_bonus = 0.2
    
    # Combined similarity
    similarity = (jaccard * 0.5 + len_ratio * 0.3 + substring_bonus * 0.2)
    
    return min(similarity, 1.0)


def is_ewallet_not_premium(norek: str, actual_name: str) -> bool:
    """
    Check if e-wallet account is not premium.
    
    A non-premium e-wallet account shows the phone number/VA number in the name field.
    Premium accounts show masked name like 'DNID marxxx'.
    
    Example:
    - Not Premium: DNID 08979579274 (shows phone number)
    - Premium: DNID marxxx (shows masked name)
    """
    if not actual_name or not norek:
        return False
    
    norm_actual = normalize_name(actual_name)
    norm_norek = normalize_name(norek)
    
    # Check if actual name contains the account number
    if norm_norek in norm_actual:
        return True
    
    # Check for common non-premium patterns
    non_premium_patterns = [
        r'^\d+$',  # Pure numbers
        r'^dnid\s*\d+$',  # DNID followed by numbers
        r'^va\s*\d+$',  # VA followed by numbers
        r'^\d{10,}$',  # At least 10 digits
    ]
    
    for pattern in non_premium_patterns:
        if re.match(pattern, norm_actual):
            return True
    
    return False


def is_invalid_account(validation_text: str) -> bool:
    """Check if the validation result indicates an invalid account"""
    invalid_indicators = [
        "virtual account tidak ditemukan",
        "(02) virtual account tidak ditemukan",
        "tidak ditemukan",
        "invalid",
        "error",
        "not found",
        "account not found",
        "rekening tidak ditemukan",
        "nomor tidak valid",
    ]
    
    text_lower = validation_text.lower()
    return any(indicator in text_lower for indicator in invalid_indicators)


def compare_names(expected_name: str, actual_name: str, norek: str = None, is_ewallet: bool = False) -> MatchResult:
    """
    Compare expected name with actual validation result.
    
    Args:
        expected_name: The name from the spreadsheet
        actual_name: The name returned by validation
        norek: The account number
        is_ewallet: Whether this is an e-wallet validation
    
    Returns:
        MatchResult with status and details
    """
    exp_name = normalize_name(expected_name) if expected_name else ""
    act_name = normalize_name(actual_name) if actual_name else ""
    
    # Check for invalid account first
    if is_invalid_account(actual_name or ""):
        return MatchResult(
            status="REK TIDAK VALID",
            confidence=0.0,
            expected_name=expected_name or "",
            actual_name=actual_name or "",
            details="Virtual Account tidak ditemukan atau invalid"
        )
    
    # Check for empty result
    if not act_name:
        return MatchResult(
            status="REK TIDAK VALID",
            confidence=0.0,
            expected_name=expected_name or "",
            actual_name=actual_name or "",
            details="Tidak ada hasil validasi"
        )
    
    # Check for e-wallet non-premium
    if is_ewallet and norek and is_ewallet_not_premium(norek, actual_name):
        return MatchResult(
            status="REK BELUM PREMIUM",
            confidence=0.0,
            expected_name=expected_name or "",
            actual_name=actual_name or "",
            details=f"Account tidak premium (menampilkan nomor: {actual_name})"
        )
    
    # Calculate similarity
    similarity = calculate_similarity(exp_name, act_name)
    
    # Determine status based on similarity
    if similarity >= 0.90:
        # Exact or near-exact match
        status = "VALID"
        details = "Nama cocok sempurna"
    elif similarity >= 0.75:
        # Very close match - might be incomplete name
        # Check if actual name is incomplete (shorter and subset of expected)
        if len(act_name) < len(exp_name) and exp_name.startswith(act_name):
            status = "REK NAMA TIDAK LENGKAP"
            details = f"Nama tidak lengkap. Expected: {exp_name}, Got: {act_name}"
        else:
            status = "REK BEDA NAMA"
            details = f"Nama berbeda. Expected: {exp_name}, Got: {act_name}"
    elif similarity >= 0.50:
        # Partial match - likely different names
        status = "REK BEDA NAMA"
        details = f"Nama berbeda. Expected: {exp_name}, Got: {act_name}"
    else:
        # No meaningful match
        status = "REK BEDA NAMA"
        details = f"Nama tidak cocok. Expected: {exp_name}, Got: {act_name}"
    
    return MatchResult(
        status=status,
        confidence=similarity,
        expected_name=expected_name or "",
        actual_name=actual_name or "",
        details=details
    )


def validate_bank_account(expected_name: str, actual_name: str) -> MatchResult:
    """Validate bank account name"""
    return compare_names(expected_name, actual_name, is_ewallet=False)


def validate_ewallet_account(expected_name: str, actual_name: str, norek: str) -> MatchResult:
    """Validate e-wallet account name"""
    return compare_names(expected_name, actual_name, norek=norek, is_ewallet=True)


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        # (expected, actual, norek, is_ewallet, expected_status)
        ("marwan", "marwan", None, False, "VALID"),
        ("marwan habibi", "marwan habibi", None, False, "VALID"),
        ("marwan", "habibi", None, False, "REK BEDA NAMA"),
        ("marwan habibi", "marwan hab", None, False, "REK NAMA TIDAK LENGKAP"),
        ("marwan", "DNID marxxx", "3901082276553476", True, "VALID"),
        ("marwan", "DNID 08979579274", "390108979579274", True, "REK BELUM PREMIUM"),
        ("marwan", "DNID habxxx", "3901082276553476", True, "REK BEDA NAMA"),
        ("marwan habibi", "marwan hab", "3901082276553476", True, "REK NAMA TIDAK LENGKAP"),
    ]
    
    print("Running test cases...")
    for exp, act, norek, is_ew, expected_status in test_cases:
        result = compare_names(exp, act, norek=norek, is_ewallet=is_ew)
        status_symbol = "✓" if result.status == expected_status else "✗"
        print(f"{status_symbol} Expected: {expected_status}, Got: {result.status} | {result.details}")
