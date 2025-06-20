# Expensify – Smart Expense Tracker

Expensify is a lightweight, secure, and user-friendly expense tracking web app built with **Streamlit** and **Supabase**. It allows users to **register**, **log in**, and manage their expenses with **receipt detials** and **per-user visual charts**.

---

## Features

### Authentication
- Secure **email/password login and registration** powered by Supabase.
- **Persistent session** using access & refresh tokens.
- **Logout & auto session restoration** via `st.session_state`.

### Receipt Scanning (OCR)
- Upload images of receipts.
- Automatically extract **merchant name**, **total spend**, **date**, **payment mode** using `pytesseract` OCR and regex.
- Select the category, any discounts or tips applicable and add to user-specific database.

### Visual Insights
- Bar charts for **daily**, **monthly**, and **yearly** spending trends.
- Aggregated data visualizations using **pandas** and **Streamlit charts**.

### Inline Editing and Entry
- Add/edit rows without page reload.
- Works seamlessly with Supabase table updates.

---

## Technologies Used
- Streamlit for visually-appealing frontend.
- Supabase authentication of users and Supabase Postgres database for handling the user data.
- PyTesseract OCR for extract data from the receipt images.
- Pandas and Numpy for handling the data and mathematical calculations
- Plotly for plotting data as interactive,visually-appealing charts to represent data in different ways.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/expensify.git
cd expensify
```
### 2. Install Python dependencies
```
pip install -r requirements.txt
```
### 3. Running App locally
```
streamlit run app.py
```

---
<h3 align="center">
    🎈 Try it out here: <a href="https://expensify-app.streamlit.app/">Expensify-app </a>
</h3>

## Screenshots
![Pic1](https://github.com/dachuvg/Expenisfy/blob/main/screenshots/pic1.png)
![Pic2](https://github.com/dachuvg/Expenisfy/blob/main/screenshots/pic2.png)
![Pic3](https://github.com/dachuvg/Expenisfy/blob/main/screenshots/pic3.png)
![Pic4](https://github.com/dachuvg/Expenisfy/blob/main/screenshots/pic4.png)
![Pic5](https://github.com/dachuvg/Expenisfy/blob/main/screenshots/pic5.png)

---


