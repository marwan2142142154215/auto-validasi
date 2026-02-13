"""
Telegram Client for sending validation results and screenshots

This module handles:
- Sending screenshots to Telegram
- Sending validation result messages
- Uploading files and getting shareable links
"""

import os
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TelegramResponse:
    """Response from Telegram API"""
    success: bool
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file_id: Optional[str] = None
    direct_url: Optional[str] = None


class TelegramClient:
    """Client for interacting with Telegram Bot API"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram client
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID (user or group)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self._file_url_cache: Dict[str, str] = {}
    
    def _make_request(self, method: str, data: Dict = None, files: Dict = None) -> TelegramResponse:
        """Make API request to Telegram"""
        try:
            url = f"{self.base_url}/{method}"
            
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return TelegramResponse(success=True, data=result.get("result"))
                else:
                    return TelegramResponse(
                        success=False,
                        error_message=result.get("description", "Unknown error")
                    )
            else:
                return TelegramResponse(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            return TelegramResponse(success=False, error_message=str(e))
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> TelegramResponse:
        """
        Send text message to chat
        
        Args:
            text: Message text
            parse_mode: Text formatting mode (HTML, Markdown)
        """
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        return self._make_request("sendMessage", data=data)
    
    def send_photo(self, photo_path: str, caption: str = "") -> TelegramResponse:
        """
        Send photo to chat
        
        Args:
            photo_path: Path to the image file
            caption: Photo caption
        
        Returns:
            TelegramResponse with file_id and direct_url for sharing
        """
        if not os.path.exists(photo_path):
            return TelegramResponse(
                success=False,
                error_message=f"Photo file not found: {photo_path}"
            )
        
        try:
            with open(photo_path, "rb") as photo:
                files = {"photo": photo}
                data = {
                    "chat_id": self.chat_id,
                    "caption": caption
                }
                result = self._make_request("sendPhoto", data=data, files=files)
                
                if result.success and result.data:
                    # Try to get file_id
                    photo_data = result.data
                    if "photo" in photo_data:
                        photos = photo_data["photo"]
                        if isinstance(photos, list) and photos:
                            result.file_id = photos[-1].get("file_id")
                    
                    # Generate direct URL for sharing
                    if result.file_id:
                        result.direct_url = f"https://api.telegram.org/file/bot{self.bot_token}/{result.file_id}"
                
                return result
        except Exception as e:
            return TelegramResponse(success=False, error_message=str(e))
    
    def send_validation_result(
        self,
        status: str,
        bank_type: str,
        norek: str,
        expected_name: str,
        actual_name: str,
        screenshot_path: str = None,
        details: str = ""
    ) -> TelegramResponse:
        """
        Send complete validation result with formatted message
        
        Args:
            status: Validation status (VALID, REK TIDAK VALID, etc.)
            bank_type: Bank or e-wallet type
            norek: Account number
            expected_name: Expected name from spreadsheet
            actual_name: Actual name from validation
            screenshot_path: Path to screenshot
            details: Additional details
        
        Returns:
            TelegramResponse with upload result
        """
        # Format message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create status emoji
        status_emoji = {
            "VALID": "✅",
            "REK TIDAK VALID": "❌",
            "REK BELUM PREMIUM": "⚠️",
            "REK BEDA NAMA": "🔄",
            "REK NAMA TIDAK LENGKAP": "📝",
        }.get(status, "❓")
        
        message = f"""<b>🔐 Validasi Rekening</b>

<b>Waktu:</b> {timestamp}
<b>Status:</b> {status_emoji} {status}
<b>Jenis:</b> {bank_type}
<b>No. Rek:</b> <code>{norek}</code>

<b>📋 Data:</b>
• Expected: {expected_name}
• Actual: {actual_name}

<b>📝 Detail:</b> {details}
"""
        
        # Send message first
        msg_result = self.send_message(message)
        
        if not msg_result.success:
            return msg_result
        
        # Send screenshot if available
        screenshot_ref = None
        if screenshot_path and os.path.exists(screenshot_path):
            photo_result = self.send_photo(screenshot_path, caption=f"Validasi {bank_type} - {norek}")
            if photo_result.success:
                screenshot_ref = photo_result.direct_url or photo_result.file_id
        
        # Update response with screenshot info
        if msg_result.data:
            msg_result.data["screenshot_ref"] = screenshot_ref
        
        return msg_result
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """
        Get file path from file_id
        
        Args:
            file_id: Telegram file_id
        
        Returns:
            File path on Telegram server
        """
        # Check cache first
        if file_id in self._file_url_cache:
            return self._file_url_cache[file_id]
        
        result = self._make_request("getFile", data={"file_id": file_id})
        if result.success and result.data:
            file_path = result.data.get("file_path")
            if file_path:
                self._file_url_cache[file_id] = file_path
                return file_path
        return None
    
    def download_file(self, file_id: str, save_path: str) -> bool:
        """
        Download file from Telegram
        
        Args:
            file_id: Telegram file_id
            save_path: Local path to save file
        
        Returns:
            True if successful
        """
        file_path = self.get_file_path(file_id)
        if not file_path:
            return False
        
        try:
            url = f"{self.base_url}/file/bot{self.bot_token}/{file_path}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
        except Exception:
            pass
        
        return False
    
    def upload_screenshot_to_host(self, screenshot_path: str) -> Optional[str]:
        """
        Upload screenshot and get direct URL
        
        Args:
            screenshot_path: Path to screenshot
        
        Returns:
            Direct URL for sharing or None
        """
        result = self.send_photo(screenshot_path)
        if result.success:
            return result.direct_url
        return None


# Example usage
if __name__ == "__main__":
    # Test with provided credentials
    client = TelegramClient(
        bot_token="8454399356:AAE37qFZs0U-7OITIwrkLaJSAnZjFEVLYAo",
        chat_id="8585992120"
    )
    
    # Send test message
    result = client.send_message("🤖 AutoID Validator Bot Started\n\nReady for validation requests!")
    print(f"Message sent: {result.success}")
    if not result.success:
        print(f"Error: {result.error_message}")
