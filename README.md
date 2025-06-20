# 💸 Expensify – Smart Expense Tracker with Login (Streamlit + Supabase)

Expensify is a lightweight, secure, and intuitive expense tracking web app built with **Streamlit** and **Supabase**. It allows users to **register**, **log in**, and manage their expenses with **receipt OCR**, **visual charts**, and **per-user data storage** using Row-Level Security (RLS).

---

## 🚀 Features

### 🔐 Authentication
- Secure **email/password login and registration** powered by Supabase.
- **Persistent session** using access & refresh tokens.
- **Logout & auto session restoration** via `st.session_state`.

### 🧾 Receipt Scanning (OCR)
- Upload images of receipts.
- Automatically extract **merchant name** and **total spend** using `pytesseract` OCR and regex.

### 📊 Visual Insights
- Bar charts for **daily**, **monthly**, and **yearly** spending trends.
- Aggregated data visualizations using **pandas** and **Streamlit charts**.

### 🧠 Smart Merchant Input
- Dropdown + text input for merchant names.
- Suggests from existing database + popular brands.
- All merchant names saved in **uppercase** for consistency.

### ✍️ Inline Editing and Entry
- Add/edit rows without page reload.
- Works seamlessly with Supabase table updates.

---

## 🛠️ Tech Stack

| Layer            | Technology         |
|------------------|--------------------|
| Frontend         | Streamlit          |
| Backend/Auth     | Supabase           |
| OCR              | Tesseract OCR      |
| Data Handling    | Pandas             |
| Database         | Supabase Postgres  |
| Hosting          | Streamlit Cloud    |

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/expensify.git
cd expensify
