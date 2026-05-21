import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from docx import Document

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Audit QA Tool", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: Calibri;
}
.stApp {
    background-color: #f2f2f2;
}
.stButton>button {
    background-color: #f1c40f;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ------------------- SESSION INIT -------------------
def init():
    if "users" not in st.session_state:
        st.session_state.users = {"admin": "admin"}
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "clients" not in st.session_state:
        st.session_state.clients = []
    if "engagements" not in st.session_state:
        st.session_state.engagements = []
    if "qa_data" not in st.session_state:
        st.session_state.qa_data = []
    if "logs" not in st.session_state:
        st.session_state.logs = []

init()

# ------------------- HELPERS -------------------
def log(action):
    st.session_state.logs.append({
        "User": st.session_state.user,
        "Action": action,
        "Time": datetime.datetime.now()
    })

# ------------------- LOGIN -------------------
def login():
    st.title("🔐 Internal Audit QA Tool")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.logged_in = True
            st.session_state.user = u
            log("Login")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------- DASHBOARD -------------------
def dashboard():
    st.title("📊 Dashboard")

    df = pd.DataFrame(st.session_state.qa_data)

    total = len(df)
    completed = total
    inprogress = 0
    notstarted = max(0, len(st.session_state.engagements) - completed)

    pass_count = len(df[df["result"]=="Pass"]) if not df.empty else 0
    fail_count = len(df[df["result"]=="Fail"]) if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total QA", total)
    c2.metric("Completed", completed)
    c3.metric("In Progress", inprogress)
    c4.metric("Not Started", notstarted)

    st.progress((completed/(len(st.session_state.engagements)+1)))

    st.success(f"✅ Pass: {pass_count}")
    st.error(f"❌ Fail: {fail_count}")

# ------------------- CLIENT -------------------
def create_client():
    st.title("🏢 Create Client")

    name = st.text_input("Client Name")

    if st.button("Add Client") and name:
        st.session_state.clients.append(name)
        log(f"Client Created {name}")
        st.success("Client added")

# ------------------- ENGAGEMENT -------------------
def create_engagement():
    st.title("📁 Create Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client = st.selectbox("Client", st.session_state.clients)
    fy = st.text_input("FY")
    process = st.text_input("Audit Process")
    auditor = st.text_input("Auditor")
    auditee = st.text_input("Auditee")
    dept = st.text_input("Department")
    title = st.text_input("Title")

    if st.button("Create Engagement"):
        data = {
            "id": len(st.session_state.engagements),
            "client": client,
            "fy": fy,
            "process": process,
            "auditor": auditor,
            "auditee": auditee,
            "dept": dept,
            "title": title
        }
        st.session_state.engagements.append(data)
        log("Engagement Created")
        st.success("Created successfully")

# ------------------- CHECKLIST -------------------
CHECKLIST = [
    "Planning",
    "Risk Assessment",
    "Control Testing",
    "Evidence",
    "Conclusion"
]

MANDATORY_DOCS = ["Scoping Memo","Audit Report","RCM","Audit Program","Workpapers","Evidence"]

def checklist():
    st.title("✅ QA Checklist")

    if not st.session_state.engagements:
        st.warning("Create engagement first")
        return

    eng = st.selectbox("Select Engagement", st.session_state.engagements, format_func=lambda x: x["client"])

    st.subheader("📎 Mandatory Documents")
    for doc in MANDATORY_DOCS:
        st.file_uploader(doc, key=f"{eng['id']}_{doc}")

    st.divider()

    for step in CHECKLIST:
        st.subheader(step)

        st.file_uploader("Upload Evidence", key=f"{eng['id']}_{step}")

        remark = st.text_area("Remarks", key=f"{eng['id']}_{step}_remark")

        col1, col2, col3 = st.columns(3)

        if col1.button("Pass", key=f"{eng['id']}_{step}_p"):
            save(step, "Pass", remark)

        if col2.button("Fail", key=f"{eng['id']}_{step}_f"):
            save(step, "Fail", remark)

        if col3.button("N/A", key=f"{eng['id']}_{step}_n"):
            save(step, "NA", remark)

        if st.button("💬 Chat Assist", key=f"{eng['id']}_{step}_chat"):
            st.info(f"Suggestion: Improve documentation for {step}")

def save(step, result, remark):
    st.session_state.qa_data.append({
        "step": step,
        "result": result,
        "remark": remark,
        "status": "Completed"
    })
    log(f"{step} {result}")
    st.success("Saved ✅")

# ------------------- REPORT -------------------
def report():
    st.title("📄 Report")

    df = pd.DataFrame(st.session_state.qa_data)
    st.dataframe(df)

    st.download_button("Excel", df.to_csv(index=False), "report.csv")

    # PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, "QA Report")
    c.save()
    st.download_button("PDF", buffer.getvalue(), "report.pdf")

    # Word
    doc = Document()
    doc.add_heading("QA Report", 0)
    for _, row in df.iterrows():
        doc.add_paragraph(str(row.to_dict()))
    buffer = BytesIO()
    doc.save(buffer)
    st.download_button("Word", buffer.getvalue(), "report.docx")

# ------------------- LOGS -------------------
def logs():
    st.title("📜 Logs")
    st.dataframe(pd.DataFrame(st.session_state.logs))

# ------------------- ARCHIVE -------------------
def archive():
    st.title("📦 Archive")

    if st.button("Archive Data"):
        st.session_state.qa_data = []
        log("Archived")
        st.success("Archived")

# ------------------- MAIN -------------------
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("🚆 QA System")

    st.sidebar.write(f"👤 {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        log("Logout")
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()

    menu = st.sidebar.radio("Menu", [
        "Home",
        "Dashboard",
        "Create Client",
        "Create Engagement",
        "Checklist",
        "Report",
        "Logs",
        "Archive"
    ])

    if menu == "Home":
        st.title("🏠 Home")

    elif menu == "Dashboard":
        dashboard()

    elif menu == "Create Client":
        create_client()

    elif menu == "Create Engagement":
        create_engagement()

    elif menu == "Checklist":
        checklist()

    elif menu == "Report":
        report()

    elif menu == "Logs":
        logs()

    elif menu == "Archive":
        archive()
