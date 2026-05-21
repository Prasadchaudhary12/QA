import streamlit as st
import pandas as pd
import datetime

# ------------------------------
# CONFIG + STYLING
# ------------------------------
st.set_page_config(page_title="QA Tool", layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: Calibri, sans-serif;
}
.stButton>button {
    background-color: #f1c40f;
    color: black;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION INIT
# ------------------------------
if "users" not in st.session_state:
    st.session_state["users"] = {"admin": "admin"}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = ""

if "clients" not in st.session_state:
    st.session_state["clients"] = []

if "engagements" not in st.session_state:
    st.session_state["engagements"] = []

if "qa_results" not in st.session_state:
    st.session_state["qa_results"] = []

if "logs" not in st.session_state:
    st.session_state["logs"] = []

MASTER_CHECKLIST = [
    "Audit Planning",
    "Risk Assessment",
    "Control Testing",
    "Evidence Review",
    "Conclusion"
]

# ------------------------------
# LOG
# ------------------------------
def log_action(user, action):
    st.session_state["logs"].append({
        "User": user,
        "Action": action,
        "Time": datetime.datetime.now()
    })

# ------------------------------
# LOGIN
# ------------------------------
def login():
    st.title("🔐 QA Tool Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in st.session_state["users"] and st.session_state["users"][user] == pwd:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
            log_action(user, "Login")
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------------------
# DASHBOARD
# ------------------------------
def dashboard():
    st.title("📊 Dashboard")

    total = len(st.session_state["qa_results"])
    pass_count = len([x for x in st.session_state["qa_results"] if x["result"]=="Pass"])
    fail_count = len([x for x in st.session_state["qa_results"] if x["result"]=="Fail"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total QA", total)
    col2.metric("Pass", pass_count)
    col3.metric("Fail", fail_count)

# ------------------------------
# CREATE CLIENT
# ------------------------------
def create_client():
    st.title("🏢 Create Client")
    name = st.text_input("Client Name")

    if st.button("Save"):
        st.session_state["clients"].append(name)
        st.success("Client added")

# ------------------------------
# CREATE ENGAGEMENT
# ------------------------------
def create_engagement():
    st.title("📁 Create Engagement")

    client = st.selectbox("Client", st.session_state["clients"])
    fy = st.text_input("FY")

    if st.button("Create"):
        st.session_state["engagements"].append({
            "client": client,
            "fy": fy,
            "checklist": MASTER_CHECKLIST
        })
        st.success("Created")

# ------------------------------
# CHECKLIST
# ------------------------------
def checklist():
    st.title("✅ Checklist")

    if not st.session_state["engagements"]:
        st.warning("No engagements")
        return

    eng = st.selectbox("Select Engagement", st.session_state["engagements"])

    for step in eng["checklist"]:
        st.subheader(step)

        st.file_uploader("Upload File", key=step)

        col1, col2, col3 = st.columns(3)

        if col1.button("Pass", key=step+"p"):
            save(step, "Pass")

        if col2.button("Fail", key=step+"f"):
            save(step, "Fail")

        if col3.button("N/A", key=step+"n"):
            save(step, "NA")

# ------------------------------
# SAVE RESULT
# ------------------------------
def save(step, result):
    st.session_state["qa_results"].append({
        "step": step,
        "result": result
    })
    st.success(f"{step} marked {result}")

# ------------------------------
# LOGS
# ------------------------------
def logs():
    st.title("Logs")
    st.dataframe(pd.DataFrame(st.session_state["logs"]))

# ------------------------------
# MAIN
# ------------------------------
if not st.session_state["logged_in"]:
    login()

else:
    st.sidebar.title("Menu")

    st.sidebar.write(f"👤 {st.session_state['user']}")

    # ✅ LOGOUT FIXED
    if st.sidebar.button("🚪 Logout"):
        log_action(st.session_state["user"], "Logout")
        st.session_state["logged_in"] = False
        st.session_state["user"] = ""
        st.rerun()

    menu = st.sidebar.radio("Go to", [
        "Dashboard",
        "Create Client",
        "Create Engagement",
        "Checklist",
        "Logs"
    ])

    if menu == "Dashboard":
        dashboard()
    elif menu == "Create Client":
        create_client()
    elif menu == "Create Engagement":
        create_engagement()
    elif menu == "Checklist":
        checklist()
    elif menu == "Logs":
        logs()
