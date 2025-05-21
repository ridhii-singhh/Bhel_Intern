import streamlit as st
import sqlite3
import datetime
import random
import string
import base64
import pandas as pd  
import io
from PIL import Image

st.set_page_config(page_title="Visitor Management System",
                   page_icon=":computer:",
                   layout="wide")

def connection():
    conn = sqlite3.connect('gateKeeper.db')
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitor 
              (  
                name TEXT, contact_number TEXT, purpose_of_visit TEXT, additional_info TEXT, checkIn_time TEXT, checkout_time TEXT, gate_pass TEXT, picture TEXT )''')
    conn.commit()

def add_visitor(conn, name, contact_number, purpose_of_visit, additional_info, checkIn_time, gate_pass, picture):
    c = conn.cursor()
    c.execute('INSERT INTO visitor (name, contact_number, purpose_of_visit, additional_info, checkIn_time, gate_pass, picture) VALUES (?,?,?,?,?,?,?)',
              (name, contact_number, purpose_of_visit, additional_info, checkIn_time, gate_pass, picture))
    conn.commit()

def update_checkout_time(conn, gate_pass, checkout_time):
    c = conn.cursor()
    c.execute('UPDATE visitor SET checkout_time = ? WHERE gate_pass = ?', (checkout_time, gate_pass))
    conn.commit()

def generate_GatePassNo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_allVisitors(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM visitor')
    data = c.fetchall()
    return data

def get_visitor_by_name_and_contact(conn, name, contact_number):
    c = conn.cursor()
    c.execute('SELECT * FROM visitor WHERE name=? AND contact_number=?', (name, contact_number))
    data = c.fetchone()
    return data

def get_gate_pass_by_details(conn, name, contact_number):
    c = conn.cursor()
    c.execute('SELECT gate_pass FROM visitor WHERE name=? AND contact_number=?', (name, contact_number))
    data = c.fetchone()
    return data

conn = connection()
create_table(conn)

st.header("VisitorSync: Integrated Management")
section = st.sidebar.radio("Select Section", ["Home", "Visitor", "Admin"])

if section == "Home":
        st.header("Welcome to the Visitor Management System")
        st.markdown("""
            - Use the Visitor section to check in and check out.
            - Admin section to manage and view all visitors' data.
        """)

if section == "Visitor":
    st.header("Visitor Section")
    tab1, tab2 = st.tabs(["Check-In", "Check-Out"])
    with tab1: 
        st.subheader("CHECK IN")
        with st.form("Check_In form"):
            name = st.text_input("Name")
            contact_number = st.text_input("Contact number")
            purpose_of_visit = st.text_input("Purpose of Visit")
            additional_info = st.text_input("Extra items (e.g., Laptop(HP), Bag)")
            picture = st.camera_input("Capture picture")

            submitted = st.form_submit_button("Submit")
            if submitted:
                if name and contact_number and purpose_of_visit and picture and additional_info:
                    if len(contact_number) == 10 and contact_number[0] in ['6', '7', '8', '9'] and contact_number.isdigit():
                        checkIn_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        gate_pass = generate_GatePassNo()
                        picture_bytes = picture.getvalue()
                        picture_base64 = base64.b64encode(picture_bytes).decode('utf-8')

                        try:
                            add_visitor(conn, name, contact_number, purpose_of_visit, additional_info, checkIn_time, gate_pass, picture_base64)
                            st.success("Check-In Successful")
                            st.info("Your Gate Pass Number will be required at the time of Check Out")
                            st.write(f"Gate Pass Number: {gate_pass}")
                        except Exception as e:
                            st.error("Error adding visitor to the database.")
                            st.error(str(e))
                    else:
                        st.error("Contact number must start with 6, 7, 8, or 9 and have exactly 10 digits and must be numeric.")
                else:
                    st.error("Please fill all fields and capture a picture.")
    with tab2:
        st.subheader("Check-Out or Retrieve Gate Pass Number")
        option = st.radio("Select an option", ["Check-Out", "Forgot Gate Pass Number"])

        if option == "Check-Out":
            gate_pass = st.text_input("Enter your Gate Pass Number")
            check_out = st.button("Check-Out")
            if check_out:
                if gate_pass:
                    checkout_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_checkout_time(conn, gate_pass, checkout_time)
                    st.success("Check-Out Successful!")
                else:
                    st.error("Please enter the gate pass number.")

        if option == "Forgot Gate Pass Number":
            st.subheader("Forgot Gate Pass Number?")
            with st.form("Retrieve Gate Pass"):
                name = st.text_input("Name")
                contact_number = st.text_input("Contact number")
                retrieve_pass = st.form_submit_button("Retrieve Gate Pass")
                if retrieve_pass:
                    if name and contact_number:
                        if len(contact_number) == 10 and contact_number.isdigit():
                            gate_pass_data = get_gate_pass_by_details(conn, name, contact_number)
                            if gate_pass_data:
                                st.success(f"Your Gate Pass Number: {gate_pass_data[0]}")
                            else:
                                st.error("No visitor found with these details.")
                        else:
                            st.error("Contact number should be exactly 10 digits and must be numeric.")
                    else:
                        st.error("Please enter your name and contact number.")       

if section == "Admin":
    password = st.sidebar.text_input("Enter Password", type="password")
    if password == 'bhel@herp':
        st.title("Admin Desk")
    
        st.subheader("Visitor Database")
        data = get_allVisitors(conn)
        df = pd.DataFrame(data, columns=['Name', 'Contact Number', 'Purpose of visit', 'Additional Info', 'Check In time', 'Check Out time', 'Gate pass Number', 'Picture'])
        st.dataframe(df)
       
        
        st.subheader("View Visitor Details")
        name = st.text_input("Enter Name")
        contact_number = st.text_input("Enter Contact Number")

        if st.button("View Visitor"):
            if name and contact_number:
                if len(contact_number) == 10 and contact_number.isdigit():
                    visitor_data = get_visitor_by_name_and_contact(conn, name, contact_number)
                    if visitor_data:
                        st.write("*Name:*", visitor_data[0])
                        st.write("*Contact Number:*", visitor_data[1])
                        st.write("*Purpose:*", visitor_data[2])
                        st.write("*Additional Info:*", visitor_data[3])
                        st.write("*Check-In Time:*", visitor_data[4])
                        st.write("*Check-Out Time:*", visitor_data[5])

                        picture_base64 = visitor_data[7]
                        picture_bytes = base64.b64decode(picture_base64)
                        picture = Image.open(io.BytesIO(picture_bytes))
                        st.image(picture, caption=visitor_data[0])
                    else:
                        st.error("No visitor found with this name and contact number.")
                else:
                    st.error("Contact number should be exactly 10 digits and must be numeric.")
            else:
                st.error("Please enter both gate pass number and contact number.")

        if st.button("Download Data"):
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="visitor_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)      

conn.close()
