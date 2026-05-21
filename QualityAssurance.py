import streamlit as st
import pandas as pd
import datetime

# ------------------------------
# Styling (Calibri + Grey/Yellow Theme)
# ------------------------------
st.set_page_config(page_title="Internal Audit QA Tool", layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: Calibri, sans-serif;
}
.main {
    background-color: #f5f5f5;
}
.stButton>button {
    background-color: #f1c40f;
    color: black;
    border-radius: 6px;
    font-weight: bold;
}
.sidebar .sidebar-content {
    background-color: #2c2c2c;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Dummy Data Storage (Replace with DB in production)
# ------------------------------
if "users" not in st.session_state:
    st.session_state["users"] = {"admin": "admin"}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "clients" not in st.session_state:
    st.session_state["clients"] = []

if "engagements" not in st.session_state:
    st.session_state["engagements"] = []

if "qa_results" not in st.session_state:
    st.session_state["qa_results"] = []

if "logs" not in st.session_state:
    st.session_state["logs"] = []

# Master checklist
MASTER_CHECKLIST = [
    "Audit Planning & Scoping",
    "Risk Assessment",
    "Control Testing",
    "Evidence Documentation",
    "Audit Conclusion",
]

# ------------------------------
# LOGIN
# ------------------------------
def login():
    st.title("🔐 Internal Audit QA Tool - Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in st.session_state["users"] and st.session_state["users"][user] == pwd:
            st.session_state["logged_in"] = True
            log_action(user, "Logged in")
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# ------------------------------
# LOGGING FUNCTION
# ------------------------------
def log_action(user, action):
    st.session_state["logs"].append({
        "user": user,
        "action": action,
        "time": datetime.datetime.now()
    })

# ------------------------------
# DASHBOARD
# ------------------------------
def dashboard():
    st.title("📊 Dashboard")

    total = len(st.session_state["qa_results"])
    completed = len([q for q in st.session_state["qa_results"] if q["status"] == "Completed"])
    in_progress = len([q for q in st.session_state["qa_results"] if q["status"] == "In Progress"])
    not_started = total - (completed + in_progress)

    pass_count = len([q for q in st.session_state["qa_results"] if q.get("result") == "Pass"])
    fail_count = len([q for q in st.session_state["qa_results"] if q.get("result") == "Fail"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total QA", total)
    col2.metric("Completed", completed)
    col3.metric("In Progress", in_progress)
    col4.metric("Not Started", not_started)

    st.divider()

    st.metric("✅ Pass", pass_count)
    st.metric("❌ Fail", fail_count)

# ------------------------------
# CREATE CLIENT
# ------------------------------
def create_client():
    st.title("🏢 Create Client")

    name = st.text_input("Client Name")

    if st.button("Save Client"):
        st.session_state["clients"].append(name)
        log_action("admin", f"Created client {name}")
        st.success("Client Created")

# ------------------------------
# CREATE ENGAGEMENT
# ------------------------------
def create_engagement():
    st.title("📁 Create Engagement")

    client = st.selectbox("Select Client", st.session_state["clients"])
    fy = st.text_input("Financial Year")
    process = st.text_input("Audit Process")
    auditor = st.text_input("Auditor Name")
    auditee = st.text_input("Auditee Name")
    dept = st.text_input("Department")
    title = st.text_input("Title")

    if st.button("Create Engagement"):
        engagement = {
            "client": client,
            "fy": fy,
            "process": process,
            "auditor": auditor,
            "auditee": auditee,
            "dept": dept,
            "title": title,
            "checklist": MASTER_CHECKLIST.copy(),
            "status": "Not Started"
        }
        st.session_state["engagements"].append(engagement)
        log_action("admin", f"Created engagement for {client}")
        st.success("Engagement Created")

# ------------------------------
# CHECKLIST EXECUTION
# ------------------------------
def run_checklist():
    st.title("✅ QA Checklist")

    if not st.session_state["engagements"]:
        st.warning("No engagements found")
        return

    eng = st.selectbox("Select Engagement", st.session_state["engagements"])

    for step in eng["checklist"]:
        st.subheader(step)

        doc = st.file_uploader(f"Upload Evidence for {step}", key=step)
        remark = st.text_area("Remarks", key=step+"_remark")

        col1, col2, col3 = st.columns(3)

        if col1.button("✔ Pass", key=step+"pass"):
            save_result(step, "Pass")

        if col2.button("❌ Fail", key=step+"fail"):
            save_result(step, "Fail")

        if col3.button("N/A", key=step+"na"):
            save_result(step, "NA")

        # Chat simulation
        if st.button("💬 Chat Assistance", key=step+"_chat"):
            prompt = st.text_input("Enter prompt")
            st.info(f"AI Suggestion: Improve {step} by ensuring documentation is complete.")

    update_dashboard()

def save_result(step, result):
    st.session_state["qa_results"].append({
        "step": step,
        "result": result,
        "status": "Completed"
    })

# ------------------------------
# DASHBOARD AUTO UPDATE
# ------------------------------
def update_dashboard():
    st.success("Dashboard Updated")

# ------------------------------
# FINAL REPORT
# ------------------------------
def generate_report():
    st.title("📄 Generate Final Report")

    if st.button("Generate Report"):
        df = pd.DataFrame(st.session_state["qa_results"])
        st.dataframe(df)

        st.download_button("Download Excel", df.to_csv(), "report.csv")

# ------------------------------
# ARCHIVE
# ------------------------------
def archive():
    st.title("📦 Archive")
    if st.button("Archive Completed Items"):
        st.session_state["qa_results"] = []
        st.success("Archived Successfully")

# ------------------------------
# AUDIT LOGS
# ------------------------------
def logs():
    st.title("📝 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state["logs"]))

# ------------------------------
# MAIN APP
# ------------------------------
if not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Menu", [
        "Dashboard",
        "Create Client",
        "Create Engagement",
        "Checklist",
        "Report",
        "Logs",
        "Archive"
    ])

    if menu == "Dashboard":
        dashboard()
    elif menu == "Create Client":
        create_client()
    elif menu == "Create Engagement":
        create_engagement()
    elif menu == "Checklist":
        run_checklist()
    elif menu == "Report":
        generate_report()
    elif menu == "Logs":
        logs()
    elif menu == "Archive":
        archive()
``
