import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
from datetime import date
import os
import re
from dateutil import parser
from supabase import create_client
from charts import monthly, yearly, category_pie, filter_by_year_range, daily, select_year, calc_avg


SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://ssxcspxupdgfxmwpkkzf.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzeGNzcHh1cGRnZnhtd3Bra3pmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyNjU2MTYsImV4cCI6MjA2NTg0MTYxNn0.mzrgqmc0G-wK6DvgSkQVBRJt9mTkxgsaVyzbJUAa8PI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


cols = ['Date', 'Merchant', 'Payment', 'Category', 'Total Spend']
for key, default in {
    "df": pd.DataFrame(columns=cols),
    "user": None, 
    "login_state": "logged_out",
    "uploaded_file": None, 
    "date_str": date.today().strftime("%Y-%m-%d"),
    "merchant": "N/A", 
    "pay": "Cash",
    "category": "N/A",
    "discount": 0.0, 
    "tip": 0.0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def set_auth():
    if "access_token" in st.session_state and "refresh_token" in st.session_state:
        supabase.auth.set_session(
            access_token=st.session_state.access_token,
            refresh_token=st.session_state.refresh_token
        )

def is_logged_in():
    try:
        set_auth()
        return bool(supabase.auth.get_user().user)
    except:
        return False


def load_user_data(email):
    try:
        res = supabase.table("expenses").select("*").eq("username", email).execute()
        data = res.data or []
        df = pd.DataFrame(data)
        if not df.empty:
            df["Date"] = pd.to_datetime(df["date"])
            df.rename(columns={
                "merchant": "Merchant", "payment": "Payment",
                "category": "Category", "total_spend": "Total Spend"
            }, inplace=True)
        return df[cols] if not df.empty else pd.DataFrame(columns=cols)
    except:
        return pd.DataFrame(columns=cols)

def insert_row(email, row):
    set_auth()
    try:
        user = supabase.auth.get_user().user
        payload = {
            "uid": user.id, "username": email,
            "date": row["Date"].strftime("%Y-%m-%d"),
            "merchant": row["Merchant"],
            "payment": row["Payment"],
            "category": row["Category"],
            "total_spend": float(row["Total Spend"])
        }
        supabase.table("expenses").insert(payload).execute()
        st.success("✅ Saved to Supabase!")
    except Exception as e:
        st.error(f"Failed to insert: {e}")

# Process OCR text
def normalize_date(date_str):
    try:
        if not date_str:
            return None
        dt = parser.parse(date_str, dayfirst=False, yearfirst=False)
        return dt.strftime('%d/%m/%Y')
    except Exception:
        return None

def get_largest_float(text):
    floats = re.findall(r'(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}', text)
    floats = [float(f.replace(',', '')) for f in floats]
    return max(floats) if floats else None

def extract_merchant(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    top_lines = lines[:5]

    skip_keywords = ['receipt','invoice','order','date','time','tax','total','number','no.','guest','table','party','check','visit','server','dine in','takeout','purchase']

    for line in top_lines:
        line_low = line.lower()
        
        if (
            len(line) > 2 and
            not any(k in line_low for k in skip_keywords) and get_date(line)==None):
            #and
            # not any(char.isdigit() for char in line)):
            return line

    return "Merchant Not Found"

def get_date(lines):
    date_pattern = re.compile(
    r'(\d{1,2}/\d{1,2}/\d{2,4}'                  # 05/20/24
    r'|\d{4}-\d{2}-\d{2}'                        # 2025-06-14
    r'|\d{1,2}-\d{1,2}-\d{2,4}'                  # 05-20-24
    r'|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b'  # 22 May 2004
    r')',
    re.IGNORECASE)
    date_found = None
    for line in reversed(lines):
        if date_match := date_pattern.search(line):
            date_found = date_match.group(1)
            break
    return date_found

def extract_totals_and_dates(text):

    total_pattern = re.compile(r'(?i)^(?!.*sub\s*total).*?\W*total\W*\s*[:\-]?\s*\$?((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})',re.MULTILINE)
    mastercard_pattern = re.compile(r'(?i)\bmaster[\s\-]?card\b.*?\$?((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})')
    amount_pattern = re.compile(r'(?i)\bpamount\b.*?\$?((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})')


    results = []
    lines = text.split('\n')
    is_card = bool(mastercard_pattern.search(text))
    date_found = get_date(lines)

    
    for i, line in enumerate(lines):
        if re.search(r'(?i)sub\s*total', line):
            continue
            
        total_match = total_pattern.search(line)
        if total_match:
            results.append({
                'total': total_match.group(1),
                'date': date_found,
                'payment': 'Card' if is_card==True else 'Cash'
            })
            return results
            
    for i, line in enumerate(lines):
        mastercard_match = mastercard_pattern.search(line)
        if mastercard_match:
            results.append({
                'total': mastercard_match.group(1).replace(',', ''),
                'date': date_found,
                'payment': 'Card' if is_card==True else 'Cash'
            })
            return results
    for i, line in enumerate(lines):
        amount_match = amount_pattern.search(line)
        if amount_match:
            results.append({
                'total': amount_match.group(1).replace(',', ''),
                'date': date_found,
                'payment': 'Card' if is_card==True else 'Cash'
            })
            return results
    largest = get_largest_float(text)
    if largest is not None:
        results.append({
            'total': f"{largest:.2f}",
            'date': date_found,
            'payment': 'Card' if is_card==True else 'Cash'
        })


    return results

def login_sidebar():
    st.sidebar.header("🔐 Login / Register")
    mode = st.sidebar.selectbox("Pick one", ["Login", "Register"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button(mode):
        try:
            if mode == "Login":
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            else:
                res = supabase.auth.sign_up({"email": email, "password": password})
            if res.session:
                st.session_state.update({
                    "user": res.user,
                    "access_token": res.session.access_token,
                    "refresh_token": res.session.refresh_token,
                    "username": email,
                    "login_state": "logged_in",
                    "df": load_user_data(email)
                })
                st.sidebar.success("Logged in successfully!")
                st.rerun()
            else:
                st.sidebar.warning("Check your email for verification.")
        except Exception as e:
            st.sidebar.error(str(e))
    if st.session_state.get("login_state") == "logged_in":
        st.sidebar.success(f"Welcome {st.session_state.username}")
        if st.sidebar.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.clear()
            st.rerun()


st.title("🧾 Expensify - Track Your Spending Easily")
uploaded_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    img = Image.open(uploaded_file)
    text = pytesseract.image_to_string(img)
    results = extract_totals_and_dates(text)
    if results:
        details = results[0]
        st.session_state.update({
            "uploaded_file": uploaded_file,
            "date_str": normalize_date(details.get("date")),
            "merchant": extract_merchant(text),
            "pay": details.get("payment"),
            "ocr_total": float(details.get("total", 0.0))
        })


col1, col2 = st.columns(2)
with col1:
    date_str = st.text_input("📆 Date", st.session_state.date_str)
    merchant = st.text_input("🏫 Merchant", st.session_state.merchant.upper())
with col2:
    pay = st.text_input("💳 Payment Mode", st.session_state.pay)
    category = st.selectbox("🛒 Category", (
        "N/A", "Food and Dining", "Grocery", "Electronics", "Clothes and Accessories",
        "Entertainment", "Medical", "Transportation", "Household", "Others"
    ))
    discount = st.number_input("Discount", min_value=0.0, value=0.0)
    tip = st.number_input("Tip (if any)", min_value=0.0, value=0.0) if category == "Food and Dining" else 0.0

total = float(st.session_state.get("ocr_total", 0.0))
final_total = total - discount + tip
st.text_input("💰 Total Spend", value=final_total, disabled=True)


if st.button("Add"):
    if merchant == "N/A" or category == "N/A":
        st.warning("Fill in required fields.")
    else:
        new_row = {
            "Date": pd.to_datetime(date_str),
            "Merchant": merchant.upper(),
            "Payment": pay,
            "Category": category,
            "Total Spend": final_total
        }
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        if is_logged_in():
            insert_row(st.session_state.username, new_row)
        else:
            st.info("💾 Data stored locally (not logged in)")
    
    st.session_state.update({
        "date_str": date.today().strftime("%Y-%m-%d"),
        "merchant": "N/A",
        "pay": "Cash",
        "category": "N/A",
        "discount": 0.0,
        "tip": 0.0,
        "ocr_total": 0.0,
        "uploaded_file": None
    })


tab1, tab2 = st.tabs(["🔢 Data", "📊 Charts"])
with tab1:
    if st.toggle("Enable editing"):
        st.session_state.df = st.data_editor(st.session_state.df, use_container_width=True)
    st.dataframe(st.session_state.df, use_container_width=True)
    
    st.markdown(f"#### 🎯 Average Daily Spend: {calc_avg(st.session_state.df):.2f}")

with tab2:
    if st.session_state.df.empty:
        st.warning("No data to show.")
    else:
        col3, spacer, col4 = st.columns([1, 0.2, 1])
        with col3:
            filtered_df = filter_by_year_range(st.session_state.df)
            yearly(filtered_df)
            category_pie(filtered_df)
        
        with col4:
            selected_year,df_year = select_year(st.session_state.df)
            monthly(df_year)
            daily(selected_year,df_year)
        


login_sidebar()

with st.sidebar:
    
    st.header("📌 How to Use Expensify")

    st.markdown("""
    1. **Upload an Image**  
       Upload your receipt image (`.jpg`, `.jpeg`, `.png`) for processing.

    2. **Review Extracted Info**  
       You can review and edit the extracted info manually.

    3. **Enter Payment Mode**  
       `Cash`,`Card`

    4. **Select Category**  
       Choose the spending category (`Food`, `Grocery`, etc.).

    5. **Click Add**  
       This adds the data to your existing `.csv` file.

    6. **Enable Editing** *(Optional)*  
       Toggle "Enable editing" to manually adjust in the csv file.

    7. **View Summary**  
       Go to the "Charts" to view your monthly, yearly and more spending statistics.
    

       
    """)

    


