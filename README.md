# 🤖 AutoID Validator

**Automated Bank & E-Wallet Account Validation System**

AutoID Validator adalah sistem validasi rekening bank dan e-wallet yang otomatis, menggunakan web automation untuk memvalidasi rekening melalui CIMB OCTO dan KlikBCA.

## 📋 Fitur

- ✅ Validasi rekening bank (BCA, Mandiri, BRI, BNI, dll)
- ✅ Validasi e-wallet (GoPay, OVO, DANA, LinkAja, ShopeePay)
- ✅ Perbandingan nama otomatis dengan logika cerdas
- ✅ Status hasil: VALID, REK TIDAK VALID, REK BELUM PREMIUM, REK BEDA NAMA, REK NAMA TIDAK LENGKAP
- ✅ Integrasi Google Sheets untuk input/output data
- ✅ Notifikasi Telegram dengan screenshot
- ✅ Mode Demo untuk testing tanpa browser
- ✅ Build sebagai executable (.exe) untuk Windows

## 🚀 Cara Menggunakan

### 1. Persiapan

1. Install Python 3.8+ dari [python.org](https://python.org)
2. Clone atau download repository ini
3. Install dependencies:
```bash
pip install -r requirements.txt
python -m playwright install
python -m playwright install chromium
```

### 2. Konfigurasi

Copy `.env.example` ke `.env` dan isi dengan kredensial Anda:

```env
# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_GID=your_sheet_gid
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# CIMB OCTO (Bank)
CIMB_USERNAME=linda0207
CIMB_PASSWORD=@Aa778899

# BCA (E-Wallet)
BCA_USERNAME=NIPUTUAY3610
BCA_PASSWORD=788888
```

### 3. Format Google Sheets

Spreadsheet harus memiliki format berikut:

| Kolom | Header | Deskripsi |
|-------|--------|-----------|
| D | Nama | Nama yang diharapkan dari rekening |
| E | No. Rek | Nomor rekening yang akan divalidasi |
| F | Jenis | Jenis bank/ewallet (bca, mandiri, dana, dll) |
| G | Status | Hasil validasi (kosong untuk pending) |
| H | Nama Aktual | Nama yang muncul dari validasi |
| I | Screenshot | Link screenshot dari Telegram |

### 4. Menjalankan

**Mode Normal (dengan browser):**
```bash
python main.py
```

**Mode Demo (tanpa browser):**
```bash
python main.py --demo
```

**Mode Headless (tanpa tampilan):**
```bash
python main.py --headless
```

**Batas jumlah baris:**
```bash
python main.py --max-rows 10
```

## 📊 Logika Validasi

### Status Hasil

| Status | Deskripsi | Contoh |
|--------|-----------|--------|
| **VALID** | Nama cocok sempurna | Input: Marwan → Output: Marwan ✅ |
| **REK TIDAK VALID** | Rekening tidak ditemukan | Output: "(02) Virtual Account Tidak Ditemukan" ❌ |
| **REK BELUM PREMIUM** | E-wallet tidak premium | Input: 390108979579274 → Output: DNID 08979579274 ⚠️ |
| **REK BEDA NAMA** | Nama berbeda | Input: Marwan → Output: Habibi 🔄 |
| **REK NAMA TIDAK LENGKAP** | Nama tidak lengkap | Input: Marwan Habibi → Output: Marwan Hab 📝 |

### Contoh

```
VALID:
  Input: bca, 25449874, "Marwan"
  Output: "Marwan"
  Status: VALID ✅

REK TIDAK VALID:
  Input: dana, 123456789, ""
  Output: "(02) Virtual Account Tidak Ditemukan"
  Status: REK TIDAK VALID ❌

REK BELUM PREMIUM:
  Input: dana, 390108979579274, ""
  Output: "DNID 08979579274"
  Status: REK BELUM PREMIUM ⚠️

REK BEDA NAMA:
  Input: bca, 25449874, "Marwan"
  Output: "Habibi"
  Status: REK BEDA NAMA 🔄

REK NAMA TIDAK LENGKAP:
  Input: bca, 25449874, "Marwan Habibi"
  Output: "Marwan Hab"
  Status: REK NAMA TIDAK LENGKAP 📝
```

## 🏗️ Build sebagai .exe

Untuk membuat executable Windows:

```bash
pip install pyinstaller
python build_exe.py --all
```

Executable akan berada di folder `dist/AutoIDValidator.exe`

## 📁 Struktur Project

```
AutoID-Validator/
├── config.py           # Konfigurasi utama
├── main.py            # Aplikasi utama
├── name_match.py      # Logika pencocokan nama
├── telegram_client.py  # Client Telegram
├── sheets_client.py   # Client Google Sheets
├── web_validators.py  # Web automation
├── build_exe.py       # Script build executable
├── requirements.txt    # Dependencies
├── run_validator.bat  # Batch file untuk Windows
├── README.md          # Dokumentasi
└── screenshots/       # Folder screenshot
```

## 🔧 Konfigurasi Bank

Bank yang didukung:
- BCA (Bank Central Asia)
- Mandiri (Bank Mandiri)
- BRI (Bank Rakyat Indonesia)
- BNI (Bank Negara Indonesia)
- BTPN (Bank BTPN)
- Permata (Bank Permata)
- CIMB (CIMB Niaga)
- OCBC (OCBC NISP)
- Jago (Bank Jago)
- Danamon (Bank Danamon)

E-Wallet yang didukung:
- GoPay
- OVO
- DANA
- LinkAja
- ShopeePay

## ⚠️ Catatan Penting

1. **Keamanan**: Simpan kredensial dengan aman. Jangan commit file `.env` ke repository publik.
2. **Rate Limiting**: Jangan jalankan terlalu cepat untuk menghindari blokir dari website bank.
3. **Browser**: Pastikan Chrome/Chromium terinstall untuk Playwright.
4. **Google Sheets**: Diperlukan service account JSON untuk akses Google Sheets API.

## 📝 Lisensi

MIT License

## 👨‍💻 Author

AutoID Team

---

**Jika ada pertanyaan atau masalah, silakan buat issue di repository.**
