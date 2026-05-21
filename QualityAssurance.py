import streamlit as st
import pandas as pd
import datetime

# ------------------------------
# PAGE CONFIG + STYLING
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
    border-radius: 8px;
    font-weight: bold;
}
.sidebar .sidebar-content {
    background-color: #2c2c2c;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION STATE INIT
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

# ------------------------------
# MASTER CHECKLIST
# ------------------------------
MASTER_CHECKLIST = [
    "Audit Planning & Scoping",
    "Risk Assessment",
    "Control Testing",
    "Evidence Documentation",
    "Audit Conclusion",
]

# ------------------------------
# LOG FUNCTION
# ------------------------------
def log_action(user, action):
    st.session_state["logs"].append({
        "User": user,
        "Action": action,
        "Time": datetime.datetime.now()
    })

# ------------------------------
# LOGIN PAGE
# ------------------------------
def login():
    st.title("🔐 Internal Audit QA Tool")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in st.session_state["users"] and st.session_state["users"][user] == pwd:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
            log_action(user, "Logged in")
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# ------------------------------
# DASHBOARD
# ------------------------------
def dashboard():
    st.title("📊 Dashboard")

    total = len(st.session_state["qa_results"])
    completed = len([q for q in st.session_state["qa_results"] if q["status"] == "Completed"])
    in_progress = len([q for q in st.session_state["qa_results"] if q["status"] == "In Progress"])
    not_started = total - completed - in_progress

    pass_count = len([q for q in st.session_state["qa_results"] if q.get("result") == "Pass"])
    fail_count = len([q for q in st.session_state["qa_results"] if q.get("result") == "Fail"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total QA", total)
    c2.metric("Completed", completed)
    c3.metric("In Progress", in_progress)
    c4.metric("Not Started", not_started)

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
        log_action(st.session_state["user"], f"Created client {name}")
        st.success("Client Created")

# ------------------------------
# CREATE ENGAGEMENT
# ------------------------------
def create_engagement():
    st.title("📁 Create Engagement")

    client = st.selectbox("Client", st.session_state["clients"])
    fy = st.text_input("Financial Year")
    process = st.text_input("Audit Process")
    auditor = st.text_input("Auditor Name")
    auditee = st.text_input("Auditee Name")
    dept = st.text_input("Department")
    title = st.text_input("Title")

    if st.button("Create Engagement"):
        st.session_state["engagements"].append({
            "client": client,
            "fy": fy,
            "process": process,
            "auditor": auditor,
            "auditee": auditee,
            "dept": dept,
            "title": title,
            "checklist": MASTER_CHECKLIST.copy(),
            "status": "Not Started"
        })

        log_action(st.session_state["user"], f"Created engagement for {client}")
        st.success("Engagement Created")

# ------------------------------
# CHECKLIST
# ------------------------------
def run_checklist():
    st.title("✅ QA Checklist")

    if not st.session_state["engagements"]:
        st.warning("No engagements available")
        return

    eng = st.selectbox("Select Engagement", st.session_state["engagements"])

    for step in eng["checklist"]:
        st.subheader(step)

        st.file_uploader("Upload Evidence", key=step)
        remarks = st.text_area("Remarks", key=step+"_remarks")

        col1, col2, col3 = st.columns(3)

        if col1.button("✔ Pass", key=step+"pass"):
            save_result(step, "Pass")

        if col2.button("❌ Fail", key=step+"fail"):
            save_result(step, "Fail")

        if col3.button("N/A", key=step+"na"):
            save_result(step, "NA")

        if st.button("💬 AI Assist", key=step+"_chat"):
            st.info(f"Suggestion: Ensure proper documentation and validation for '{step}'")

# ------------------------------
# SAVE RESULT
# ------------------------------
def save_result(step, result):
    st.session_state["qa_results"].append({
        "step": step,
        "result": result,
        "status": "Completed"
    })

# ------------------------------
# REPORT
# ------------------------------
def generate_report():
    st.title("📄 Final Report")

    df = pd.DataFrame(st.session_state["qa_results"])

    st.dataframe(df)

    st.download_button("📥 Download Excel", df.to_csv(index=False), "QA_Report.csv")

# ------------------------------
# LOGS
# ------------------------------
def logs():
    st.title("📜 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state["logs"]))

# ------------------------------
# ARCHIVE
# ------------------------------
def archive():
    st.title("📦 Archive")

    if st.button("Archive All Data"):
        st.session_state["qa_results"] = []
        st.success("Data Archived")

# ------------------------------
# MAIN
# ------------------------------
if not st.session_state["logged_in"]:
    login()

else:
    st.sidebar.title("📌 Navigation")

    st.sidebar.write(f"👤 Logged in as: {st.session_state['user']}")

    # ✅ LOGOUT BUTTON
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        log_action(st.session_state["user"], "Logged out")
        st.session_state["logged_in"] = False
        st.session_state["user"] = ""
        st.experimental_rerun()

    menu = st.sidebar.radio("Go to", [
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
