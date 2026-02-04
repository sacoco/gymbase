# GymBase 💪
### Modern Gym Management System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20Linux-lightgrey.svg)
![Build Status](https://github.com/sacoco/gymbase/actions/workflows/build.yml/badge.svg)

**GymBase** is a lightweight, modern desktop application designed to streamline gym management. Built with Python and CustomTkinter, it offers a robust solution for access control, membership tracking, and facility administration without the bloat of web-based SaaS platforms.

---

## ✨ Key Features

### 🚀 **Smart Access Control**
- **Real-time Verification**: Instantly verify member status by ID.
- **Visual Status Indicators**: Clear color-coded feedback (Granted, Expired, Frozen).
- **Serial Integration**: Supports keypad/RFID readers via serial port connection.

### 👥 **Member Management**
- **Easy Registration**: Quick onboarding flow for new members.
- **Full Tracking**: Manage personal details, contact info, and registration dates.
- **Searchable Database**: Fast lookup by Name or ID.

### 📅 **Flexible Memberships**
- **Granular Extensions**: Renew memberships by weeks, months, or years with a single click.
- **Freeze/Unfreeze**: Pause memberships for injured or traveling members (automatically adjusts expiry dates).
- **Expiration Tracking**: Automatic calculation of remaining days.

### ⚙️ **Administration**
- **Configurable Settings**: Customize gym name and terminal settings directly from the app.
- **Hardware Connection**: seamless setup for serial devices (COM ports / TTY).
- **Detailed Logging**: Comprehensive audit logs for troubleshooting and tracking entry events.

---

## 🛠️ Technology Stack
- **Core**: Python 3
- **GUI**: CustomTkinter (Modern, High DPI aware)
- **Database**: SQLite (Zero configuration, local storage)
- **Hardware**: PySerial for serial communication
- **Packaging**: PyInstaller + GitHub Actions (Automated Builds)

---

## 📥 Installation

### Prerequisites
- Python 3.10 or higher
- Git

### Quick Start (Source)

1. **Clone the repository**
   ```bash
   git clone https://github.com/sacoco/gymbase.git
   cd gymbase
   ```

2. **Set up Virtual Environment (Recommended)**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

---

## 📦 Binary Releases (Windows & Linux)

No Python installed? No problem.
Go to the **[Releases](https://github.com/sacoco/gymbase/releases)** page to download the latest standalone executable for your operating system:
- `GymBase.exe` (Windows)
- `GymBase` (Linux)

---

## 🔧 Hardware Setup

GymBase supports serial input devices (like numpads or RFID scanners) for the Access Control screen.
1. Connect your device to the computer.
2. Go to the **Administration** tab in the app.
3. Select the correct **COM Port** and **Baud Rate**.
4. Click **Connect**.
5. The device will now input IDs directly into the access check field.

---

## 📝 Logging

The application maintains a `gymbase.log` file in the root directory. This log includes:
- Application startup/shutdown events
- Database transaction errors
- Access granted/denied events
- Serial communication status

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Developed by sacoco**
