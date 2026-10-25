import streamlit as st
from config import Config
from schemas import StudentInfo
from grievance_analyzer import GrievanceAnalyzer
from email_service import EmailService

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Campus Grievance Portal",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.3rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 20px; }
    .card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; margin-bottom: 15px; }
    .critical-banner { background-color: #FEF2F2; border-left: 5px solid #EF4444; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .review-banner { background-color: #FFFBEB; border-left: 5px solid #F59E0B; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "draft_email" not in st.session_state:
    st.session_state.draft_email = None
if "dispatch_status" not in st.session_state:
    st.session_state.dispatch_status = None

# -----------------------------------------------------------------------------
# Header Component
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">Smart Campus Grievance Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Campus Issue Reporting, Intelligent Categorization & Automated Escalation</div>', unsafe_allow_html=True)

st.info("ℹ️ **How it works:** Enter your student credentials and describe your grievance in natural language. Our system uses an LLM to classify the issue, extract location metadata, and construct an actionable formal escalation email.")

# -----------------------------------------------------------------------------
# Sidebar Configuration & Help
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key_env = Config.get_gemini_api_key()
    if not api_key_env:
        user_api_key = st.text_input("Gemini API Key", type="password", help="Enter API key if not set in .env")
    else:
        user_api_key = api_key_env
        st.success("API Key detected from Environment/Secrets.")

    model_name = st.text_input("LLM Model Name", value=Config.get_gemini_model_name())

    st.markdown("---")
    st.subheader("📬 Authorized Receivers")
    dept_map = Config.get_department_emails()
    for dept, email in dept_map.items():
        st.caption(f"**{dept}**: `{email}`")

    st.markdown("---")
    if st.button("🗑️ Reset Session Data"):
        st.session_state.analysis_result = None
        st.session_state.draft_email = None
        st.session_state.dispatch_status = None
        st.rerun()

# -----------------------------------------------------------------------------
# Main Application Layout
# -----------------------------------------------------------------------------
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📝 Student Grievance Submission Form")
    
    with st.form(key="grievance_form"):
        name = st.text_input("Full Name *", placeholder="e.g. Jane Doe")
        email = st.text_input("Student Email Address *", placeholder="e.g. jane.doe@student.campus.edu")
        student_id = st.text_input("Student Roll No. / ID *", placeholder="e.g. CS2024-089")
        dept_year = st.text_input("Department & Academic Year", placeholder="e.g. Computer Engineering, 3rd Year")
        
        location_context = st.text_input("Specific Location / Context (Optional)", placeholder="e.g. Main Library 2nd Floor or Hostel Block C")
        
        description = st.text_area(
            "Detailed Complaint Description *",
            height=200,
            placeholder="Describe the problem clearly. Mention room numbers, lab computers, Wi-Fi nodes, or specific equipment if applicable..."
        )

        submit_button = st.form_submit_button(label="🔍 Analyze Complaint with AI")

    if submit_button:
        # Form Validation
        errors = []
        if not name.strip(): errors.append("Student Name is required.")
        if not email.strip() or not Config.validate_email_address(email): errors.append("A valid Student Email Address is required.")
        if not student_id.strip(): errors.append("Student ID is required.")
        if len(description.strip()) < 15: errors.append("Complaint Description must be at least 15 characters long.")

        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        else:
            student_info = StudentInfo(
                name=name.strip(),
                email=email.strip(),
                student_id=student_id.strip(),
                department_year=dept_year.strip(),
                complaint_description=description.strip(),
                location_context=location_context.strip()
            )
            st.session_state.student_info = student_info

            analyzer = GrievanceAnalyzer(api_key=user_api_key, model_name=model_name)
            with st.spinner("🤖 Analyzing grievance with AI... Extracting location entities and evaluating urgency..."):
                analysis_res, err_msg = analyzer.analyze_complaint(student_info)

            if err_msg:
                st.error(f"❌ Analysis Failed: {err_msg}")
            else:
                st.session_state.analysis_result = analysis_res
                # Generate draft email
                draft = EmailService.generate_email_draft(student_info, analysis_res)
                st.session_state.draft_email = draft
                st.session_state.dispatch_status = None
                st.success("✅ Complaint successfully analyzed!")

# -----------------------------------------------------------------------------
# Analysis Results & Email Generation Column
# -----------------------------------------------------------------------------
with col_output:
    st.subheader("📊 AI Analysis & Grievance Escalation")

    analysis = st.session_state.get("analysis_result")
    
    if not analysis:
        st.info("👈 Fill out the submission form and click **Analyze Complaint with AI** to view structured results.")
    else:
        # Safety / Critical Warning Banner
        if analysis.urgency.value == "Critical":
            st.markdown(
                """
                <div class="critical-banner">
                    <h4 style="color: #B91C1C; margin:0;">🚨 Immediate Critical Hazard Detected</h4>
                    <p style="margin:5px 0 0 0; color: #7F1D1D;">
                        <b>Emergency Notice:</b> This portal is an administrative reporting system. If this situation involves immediate physical danger, active fire, or live electrical hazards, please contact <b>Campus Security / Emergency Services</b> immediately!
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )

        if analysis.human_review_required:
            st.markdown(
                f"""
                <div class="review-banner">
                    <h5 style="color: #B45309; margin:0;">⚠️ Human Review Recommended</h5>
                    <p style="margin:5px 0 0 0; color: #92400E;">
                        <b>Missing Info / Ambiguity:</b> {', '.join(analysis.missing_information) if analysis.missing_information else 'Vague or ambiguous details detected.'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Overview Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Category", analysis.category.value)
        m2.metric("Assessed Urgency", analysis.urgency.value)
        m3.metric("Review Needed", "Yes" if analysis.human_review_required else "No")

        with st.expander("📌 Analysis Breakdown & Extracted Metadata", expanded=True):
            st.write(f"**Summary:** {analysis.summary}")
            st.write(f"**Urgency Justification:** {analysis.urgency_reason}")
            st.write(f"**Recommended Authority:** {analysis.recommended_department}")
            st.write(f"**Recommended Next Step:** {analysis.recommended_action}")

            # Extracted Entities Display
            entities = analysis.extracted_entities
            extracted_dict = {
                "Rooms": entities.room_numbers,
                "Blocks": entities.hostel_blocks,
                "Labs": entities.lab_numbers,
                "Wi-Fi Nodes": entities.node_ids,
                "Equipment IDs": entities.equipment_ids,
                "Floors": entities.floors,
                "Other Locations": entities.other_locations
            }
            active_entities = {k: v for k, v in extracted_dict.items() if v}
            st.write("**Extracted Identifiers:**")
            if active_entities:
                st.json(active_entities)
            else:
                st.caption("No specific structural room, node, or lab identifiers detected in complaint.")

        # Editable Email Preview
        st.subheader("✉️ Formal Grievance Email Draft")
        st.caption("You can review and edit any part of the generated email before taking action.")

        draft = st.session_state.draft_email
        if draft:
            recipient_input = st.text_input("Recipient Email Address", value=draft["recipient"])
            subject_input = st.text_input("Subject Line", value=draft["subject"])
            body_input = st.text_area("Email Body", value=draft["body"], height=280)

            # Action Buttons: Download, Mailto Client, SMTP Direct Send
            col_act1, col_act2, col_act3 = st.columns(3)

            with col_act1:
                st.download_button(
                    label="📥 Download (.txt)",
                    data=f"To: {recipient_input}\nSubject: {subject_input}\n\n{body_input}",
                    file_name="grievance_email_draft.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col_act2:
                mailto_link = EmailService.create_mailto_link(recipient_input, subject_input, body_input)
                st.markdown(
                    f'<a href="{mailto_link}" target="_blank" style="text-decoration:none;">'
                    f'<button style="width:100%; height:38px; border-radius:4px; background-color:#2563EB; color:white; border:none; cursor:pointer;">'
                    f'↗ Open Email App</button></a>',
                    unsafe_allow_html=True
                )

            with col_act3:
                send_smtp = st.button("🚀 Send via SMTP", use_container_width=True)

            if send_smtp:
                with st.spinner("Transmitting email via SMTP server..."):
                    success, msg = EmailService.send_smtp_email(recipient_input, subject_input, body_input)
                    if success:
                        st.session_state.dispatch_status = ("success", msg)
                    else:
                        st.session_state.dispatch_status = ("error", msg)

            if st.session_state.dispatch_status:
                status_type, status_msg = st.session_state.dispatch_status
                if status_type == "success":
                    st.success(status_msg)
                else:
                    st.error(status_msg)