<div align="center">
  <h2 align="center">Crunchyroll Account Checker</h2>
  <p align="center">
    An automated tool for checking Crunchyroll account validity, subscription status, and account details with proxy support and multi-threading capabilities.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Crunchyroll-Account-Checker/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Crunchyroll-Account-Checker/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Automated Crunchyroll account validation
- Subscription status checking (Free, Premium, Fan Pack, Mega Pack)
- Detailed account information capture
- Proxy support with automatic rotation
- Multi-threaded checking
- Real-time progress tracking
- Configurable thread count
- Debug mode for troubleshooting
- Proxy/Proxyless mode support
- Automatic retry system
- Organized output files by account status

---

### 📝 Usage

1. **Configuration**:
   Edit `input/config.toml`:

   ```toml
   [dev]
   Debug = false
   Proxyless = false
   Threads = 1
   ```

2. **Account Setup**:
   Add accounts to `input/accounts.txt`:
   - Format: `email:password`

3. **Proxy Setup** (Optional):
   - Add proxies to `input/proxies.txt` (one per line)
   - Format: `ip:port` or `user:pass@ip:port`

4. **Running the script**:
   ```bash
   python main.py
   ```

5. **Output Files**:
   - `output/valid/valid.txt`: All valid accounts
   - `output/valid/full_valid_capture.txt`: Detailed account information
   - `output/valid/free.txt`: Free accounts
   - `output/premium_accounts.txt`: Premium accounts with subscription type
   - `output/invalid/invalid.txt`: Invalid accounts

---

### 📹 Preview

![Preview](https://i.imgur.com/vrdKO91.gif)

---

### ❗ Disclaimers

- This project is for educational purposes only
- The author is not responsible for any misuse of this tool
- Use responsibly and in accordance with Crunchyroll's terms of service

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 12/26/2024
! Initial release
```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Crunchyroll-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Crunchyroll-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Crunchyroll-Account-Checker.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>
