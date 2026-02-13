# Project Configuration
PROJECT_NAME = "AutoID Validator"
VERSION = "1.0.0"
AUTHOR = "AutoID Team"

# Google Sheets Configuration
# Spreadsheet: https://docs.google.com/spreadsheets/d/1MWrSw4S0FhCu3jrFbaQVxirtcXgJaTtAyB1I_oyXzyo/edit
GOOGLE_SHEET_ID = "1MWrSw4S0FhCu3jrFbaQVxirtcXgJaTtAyB1I_oyXzyo"
GOOGLE_SHEET_GID = "2136909409"
GOOGLE_SHEET_RANGE = "D9:I"  # Columns D to I starting from row 9

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8454399356:AAE37qFZs0U-7OITIwrkLaJSAnZjFEVLYAo"
TELEGRAM_CHAT_ID = "8585992120"

# CIMB OCTO Credentials (Bank Validation)
CIMB_USERNAME = "linda0207"
CIMB_PASSWORD = "@Aa778899"

# BCA Credentials (E-Wallet Validation)
BCA_USERNAME = "NIPUTUAY3610"
BCA_PASSWORD = "788888"

# Browser Settings
HEADLESS = False  # Set to True for production
SLOW_MO_MS = 100  # Delay between actions in milliseconds
TIMEOUT_MS = 30000  # Timeout for page operations
POLL_INTERVAL_SEC = 2  # Delay between validations

# Validation Settings
MAX_ROWS_PER_RUN = 0  # 0 = unlimited
NOMINAL = "20000"

# XPath Selectors for CIMB OCTO
CIMB_SELECTORS = {
    "login_url": "https://www.cimbocto.co.id/login",
    "username_input": "/html/body/div/div[2]/div/div[2]/div/div/form/div[1]/div[1]/div/input",
    "password_input": "/html/body/div/div[2]/div/div[2]/div/div/form/div[2]/div[1]/div/div/input",
    "login_button": "/html/body/div/div[2]/div/div[2]/div/div/form/div[3]/button",
    "menu_transfer": "/html/body/div/div/nav/ul/li[2]/a/span",
    "menu_validasi_rekening": "/html/body/div/div/nav/ul/li[2]/ul/li[2]/a",
    "card_validasi_rekening": "/html/body/div/div/main/div/div[2]/div[3]",
    "bank_input": "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[1]/div[1]/div/div/input[1]",
    "bank_confirm": "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[1]/div[1]/div/ul/li/div",
    "rek_input": "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[2]/div[1]",
    "nominal_input": "/html/body/div/div/main/div/form/div[1]/div[3]/div[2]/div[3]/div/div[1]",
    "validate_button": "/html/body/div/div/main/div/form/div[2]/div/div/button",
    "result_container": "/html/body/div/div/main/div/form/div[1]/div[2]/div[1]/div[2]",
    "logout_button": "/html/body/div/div/nav/div[2]/button"
}

# XPath Selectors for BCA (E-Wallet)
BCA_SELECTORS = {
    "login_url": "https://ibank.klikbca.com/",
    "username_input": "/html/body/table[2]/tbody/tr/td[2]/div/table[1]/tbody/tr[4]/td/input",
    "password_input": "/html/body/table[2]/tbody/tr/td[2]/div/table[1]/tbody/tr[9]/td/input",
    "login_button": "/html/body/table[2]/tbody/tr/td[2]/div/form/table/tbody/tr/td/input",
    "menu_info_rekening": "/html/body/table/tbody/tr/td[2]/table/tbody/tr[7]/td/a/font/b",
    "menu_validasi_va": "/html/body/table/tbody/tr/td[2]/table/tbody/tr[4]/td/table/tbody/tr[4]/td[2]/font/a",
    "rek_input": "/html/body/form/table[3]/tbody/tr[3]/td[3]/input",
    "validate_button": "/html/body/form/table[4]/tbody/tr[2]/td/input",
    "result_container": "/html/body/form/table[3]/tbody/tr[3]/td[3]",
    "logout_button": "/html/body/div/font/b/a"
}

# Bank Mapping
BANK_MAPPING = {
    "bca": "Bank Central Asia",
    "bank centra": "Bank Central Asia",
    "central asia": "Bank Central Asia",
    "bri": "Bank Rakyat Indonesia",
    "bank rakyat": "Bank Rakyat Indonesia",
    "mandiri": "Bank Mandiri",
    "bank mandiri": "Bank Mandiri",
    "jago": "Bank Jago",
    "bank jago": "Bank Jago",
    "danamon": "Bank Danamon",
    "bank danamon": "Bank Danamon",
    "bni": "Bank Negara Indonesia",
    "bank negara": "Bank Negara Indonesia",
    "btpn": "Bank BTPN",
    "permata": "Bank Permata",
    "bank permata": "Bank Permata",
    "cimb": "Bank CIMB Niaga",
    "cimb niaga": "Bank CIMB Niaga",
    "niaga": "Bank CIMB Niaga",
    "ocbc": "Bank OCBC NISP",
    "ocbc nisp": "Bank OCBC NISP",
    "nisp": "Bank OCBC NISP",
    "gopay": "GoPay",
    "ovo": "OVO",
    "dana": "DANA",
    "linkaja": "LinkAja",
    "shopeepay": "ShopeePay"
}

EWALLET_LIST = ["gopay", "ovo", "dana", "linkaja", "shopeepay"]
