import streamlit as st
import os
from dotenv import load_dotenv
from backend.pipeline import process_pipeline
from backend.models import ExtractedField, RiskFlag
from backend.scoring import calculate_health_score
from backend.assistant import process_assistant_query, generate_suggested_questions

# Load environment variables
load_dotenv()

st.set_page_config(page_title="GenAI Client Intelligence", layout="wide")

@st.cache_data(show_spinner=False)
def cached_process_pipeline(conversation: str):
    return process_pipeline(conversation)

def load_sample_conversation():
    try:
        with open("sample_conversation.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def display_badge(status: str):
    colors = {
        "confirmed_fact": "#28a745", # Green
        "client_reported": "#007bff", # Blue
        "ai_inference": "#ffc107", # Yellow
        "missing": "#6c757d" # Gray
    }
    color = colors.get(status, "#6c757d")
    label = status.replace("_", " ").title()
    st.markdown(f"<span style='background-color:{color}; color:white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em;'>{label}</span>", unsafe_allow_html=True)

def render_field_card(title: str, field: ExtractedField, edit_mode: bool, key_prefix: str):
    with st.container(border=True):
        st.subheader(title)
        
        if edit_mode:
            val = st.text_input("Value", value=str(field.value) if field.value is not None else "", key=f"{key_prefix}_val")
            status_opts = ["confirmed_fact", "client_reported", "ai_inference", "missing"]
            
            # Ensure current status is valid for selectbox
            current_status = field.status if field.status in status_opts else "missing"
            
            status = st.selectbox("Status", status_opts, 
                                  index=status_opts.index(current_status),
                                  key=f"{key_prefix}_stat")
            conf = st.slider("Confidence", 0.0, 1.0, float(field.confidence), key=f"{key_prefix}_conf")
            
            # Save back to field (mutates session state object)
            field.value = val if val else None
            field.status = status
            field.confidence = conf
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                val_str = str(field.value) if field.value is not None else "N/A"
                st.markdown(f"**Value:** {val_str}")
            with col2:
                display_badge(field.status)
                
            st.caption(f"Confidence: {field.confidence:.2f}")
            
            if field.evidence:
                with st.expander("Explain AI"):
                    st.write("**Why was this generated?**")
                    st.write("**Reasoning:** Extracted based on conversation evidence.")
                    st.write(f"**Confidence:** {field.confidence:.2f}")
                    st.write("**Evidence:**")
                    for e in field.evidence:
                        st.write(f"- \"{e}\"")

def render_risk_card(risk: RiskFlag, edit_mode: bool, idx: int):
    with st.container(border=True):
        if edit_mode:
            title = st.text_input("Risk Title", risk.title, key=f"risk_title_{idx}")
            sev = st.selectbox("Severity", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(risk.severity), key=f"risk_sev_{idx}")
            reason = st.text_area("Reason", risk.reason, key=f"risk_reason_{idx}")
            conf = st.slider("Confidence", 0.0, 1.0, float(risk.confidence), key=f"risk_conf_{idx}")
            risk.title = title
            risk.severity = sev
            risk.reason = reason
            risk.confidence = conf
        else:
            st.markdown(f"**{risk.title}** ({risk.severity} Severity)")
            st.write(f"Reason: {risk.reason}")
            st.caption(f"Confidence: {risk.confidence:.2f}")
            with st.expander("Explain AI"):
                st.write("**Why was this generated?**")
                st.write(f"**Reasoning:** {risk.reason}")
                st.write(f"**Confidence:** {risk.confidence:.2f}")
                st.write("**Evidence:**")
                for e in risk.evidence:
                    st.write(f"- \"{e}\"")

def main():
    st.title("GenAI Client Intelligence Prototype")
    
    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    
    with st.sidebar:
        st.header("Input Conversation")
        default_convo = load_sample_conversation()
        manual_conversation = st.text_area("Paste conversation here...", value=default_convo, height=300)
        
        st.divider()
        st.subheader("Or Upload File")
        uploaded_file = st.file_uploader("Drag and drop or browse", type=["txt", "md", "csv"])
        
        process_btn = st.button("Process Conversation", type="primary")

    if process_btn:
        conversation = manual_conversation
        if uploaded_file is not None:
            try:
                file_content = uploaded_file.getvalue().decode("utf-8")
                if not conversation.strip():
                    conversation = file_content
                else:
                    conversation += "\n" + file_content
            except Exception as e:
                st.error(f"Error reading file: {e}")
                return

        if not conversation.strip():
            st.error("Please provide a conversation to process (via text or file).")
            return
            
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("GEMINI_API_KEY is missing. Please set it in your .env file or environment.")
            return

        with st.spinner("Processing... (Cached if identical conversation)"):
            try:
                # Use cached function to prevent identical API calls
                report = cached_process_pipeline(conversation)
                st.session_state['report'] = report
                st.session_state['conversation'] = conversation
                st.session_state['edit_mode'] = False # Reset edit mode
                st.success("Processing complete!")
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")

    if 'report' in st.session_state:
        report = st.session_state['report']
        info = report.extracted_info
        reasoning = report.reasoning
        edit_mode = st.session_state['edit_mode']
        
        # Calculate Health Score
        health_data = calculate_health_score(info)
        
        # --- Top Section ---
        st.header("Executive Summary")
        col_sum, col_health = st.columns(2)
        
        with col_sum:
            render_field_card("Weekly Summary", info.weekly_summary, edit_mode, "weekly_summary")
        
        with col_health:
            st.subheader("Health Score")
            st.metric(label="Overall Score", value=f"{health_data['overall_score']}/100")
            with st.expander("Score Breakdown"):
                for k, v in health_data['breakdown'].items():
                    st.write(f"**{k.title()}**: {v}")
                st.write("**Reasons:**")
                for r in health_data['reasons']:
                    st.write(f"- {r}")

        st.divider()

        st.header("Priority Risks")
        if not info.risk_flags:
            st.write("No priority risks identified.")
        else:
            cols = st.columns(min(len(info.risk_flags), 3) if info.risk_flags else 1)
            for idx, risk in enumerate(info.risk_flags):
                with cols[idx % 3]:
                    render_risk_card(risk, edit_mode, idx)

        st.divider()

        # --- Middle Section ---
        st.header("Health Metrics")
        
        # Group missing fields
        missing_fields = []
        present_fields = []
        
        all_metrics = {
            "Nutrition": info.nutrition,
            "Exercise": info.exercise,
            "Steps": info.steps,
            "Sleep": info.sleep,
            "Water Intake": info.water_intake,
            "Stress": info.stress,
            "Energy": info.energy,
            "Weight": info.weight,
            "Symptoms": info.symptoms,
            "Engagement Level": info.engagement_level,
            "Key Barriers": info.key_barriers,
            "Pending Actions": info.pending_actions
        }
        
        for k, v in all_metrics.items():
            if v.status == "missing" and not edit_mode:
                missing_fields.append((k, v))
            else:
                present_fields.append((k, v))
                
        # Render present fields in a grid
        if present_fields:
            cols = st.columns(3)
            for i, (title, field) in enumerate(present_fields):
                with cols[i % 3]:
                    render_field_card(title, field, edit_mode, title.replace(" ", "_").lower())
                    
        if missing_fields and not edit_mode:
            st.subheader("Missing Metrics")
            missing_cols = st.columns(4)
            for i, (title, field) in enumerate(missing_fields):
                with missing_cols[i % 4]:
                    st.markdown(f"**{title}**: N/A")

        st.divider()

        # --- Timeline Section ---
        if reasoning.timeline:
            st.header("Chronological Timeline")
            for entry in reasoning.timeline:
                with st.container(border=True):
                    st.markdown(f"**{entry.day}**")
                    for event in entry.events:
                        st.write(f"- {event}")
            st.divider()

        # --- Bottom Section ---
        st.header("Coach Intelligence")
        bot_col1, bot_col2, bot_col3 = st.columns(3)
        
        with bot_col1:
            st.subheader("Trends")
            for entry in reasoning.trends:
                st.write(f"**{entry.metric}:** {entry.trend}")
            if not reasoning.trends:
                st.write("No trends detected.")
                
            st.subheader("Missing Information")
            if info.missing_information:
                for mi in info.missing_information:
                    st.write(f"- {mi}")
            else:
                st.write("None identified.")
                
        with bot_col2:
            st.subheader("Suggested Follow-up Questions")
            if edit_mode:
                q_text = st.text_area("Questions (one per line)", "\n".join(reasoning.suggested_follow_up_questions))
                reasoning.suggested_follow_up_questions = [q.strip() for q in q_text.split('\n') if q.strip()]
            else:
                for q in reasoning.suggested_follow_up_questions:
                    st.write(f"- {q}")
                
        with bot_col3:
            st.subheader("Coach Recommendation")
            if edit_mode:
                reasoning.coach_recommendation = st.text_area("Recommendation", reasoning.coach_recommendation)
            else:
                st.write(reasoning.coach_recommendation)
            
        st.divider()
        st.header("Human Review")
        h_col1, h_col2, h_col3 = st.columns(3)
        
        if edit_mode:
            if h_col2.button("💾 Save Changes", use_container_width=True, type="primary"):
                st.session_state['edit_mode'] = False
                st.success("Changes saved successfully!")
                st.rerun()
        else:
            if h_col1.button("✅ Approve Report", use_container_width=True):
                st.success("Report approved successfully!")
            if h_col2.button("✏️ Edit Report", use_container_width=True):
                st.session_state['edit_mode'] = True
                st.rerun()
            if h_col3.button("❌ Reject Report", use_container_width=True):
                st.error("Report rejected.")
        
        st.caption("The AI never makes the final decision. The coach always reviews.")
        
        # --- Report Actions ---
        st.divider()
        st.header("Report Actions")
        
        if 'pdf_bytes' not in st.session_state:
            st.session_state['pdf_bytes'] = None

        act_col1, act_col2, act_col3 = st.columns(3)
        
        with act_col1:
            if st.button("📄 Generate Professional PDF", use_container_width=True, type="primary"):
                with st.spinner("Generating PDF..."):
                    from backend.pdf import generate_pdf_report
                    try:
                        st.session_state['pdf_bytes'] = generate_pdf_report(report, health_data)
                        st.success("PDF Generated Successfully!")
                    except Exception as e:
                        st.error(f"Failed to generate PDF: {e}")

        if st.session_state['pdf_bytes']:
            with act_col2:
                st.download_button(
                    label="📥 Download PDF",
                    file_name="Client_Report.pdf",
                    mime="application/pdf",
                    data=bytes(st.session_state['pdf_bytes']),
                    use_container_width=True
                )
            with act_col3:
                import urllib.parse
                wa_text = "📊 *Client Intelligence Report*\n"
                wa_text += f"*Health Score:* {health_data['overall_score']}/100\n\n"
                wa_text += f"*Summary:*\n{info.weekly_summary.value if info.weekly_summary.value else 'N/A'}\n\n"
                if info.risk_flags:
                    wa_text += f"⚠️ *Risks Detected:* {len(info.risk_flags)}\n"
                wa_text += "\n*(Download the full PDF for more details)*"
                
                wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}"
                st.markdown(f'<a href="{wa_url}" target="_blank" style="display: block; text-align: center; background-color: #25D366; color: white; padding: 6px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 2px;">💬 Share via WhatsApp</a>', unsafe_allow_html=True)
                
            with st.expander("👁️ Preview PDF", expanded=True):
                from backend.pdf import get_pdf_preview_html
                st.markdown(get_pdf_preview_html(st.session_state['pdf_bytes']), unsafe_allow_html=True)
        
        # --- AI Client Intelligence Assistant ---
        st.divider()
        st.header("AI Client Intelligence Assistant")
        
        if 'assistant_cache' not in st.session_state:
            st.session_state['assistant_cache'] = {}
            
        def set_query(q):
            st.session_state['user_query_input'] = q
            
        st.write("**Suggested Questions:**")
        suggested = generate_suggested_questions(report)
        
        cols = st.columns(4)
        for i, q in enumerate(suggested):
            cols[i % 4].button(q, on_click=set_query, args=(q,), key=f"sugg_{i}")
            
        user_query = st.text_input("Ask anything about this conversation...", key="user_query_input")
                                   
        if st.button("Ask", type="primary") and user_query:
            saved_conversation = st.session_state.get('conversation', '')
            cache_key = (hash(saved_conversation), hash(report.model_dump_json()), user_query)
            
            if cache_key in st.session_state['assistant_cache']:
                result = st.session_state['assistant_cache'][cache_key]
            else:
                with st.spinner("Analyzing..."):
                    try:
                        result = process_assistant_query(user_query, report, saved_conversation)
                        st.session_state['assistant_cache'][cache_key] = result
                    except Exception as e:
                        st.error(f"Error processing query: {e}")
                        result = None
            
            if result:
                with st.container(border=True):
                    st.markdown(f"**Answer:** {result.answer}")
                    st.caption(f"**Confidence:** {result.confidence:.2f} | **Status:** {result.status}")
                    st.markdown(f"**Reasoning:** {result.reasoning}")
                    
                    if result.sources:
                        with st.expander("View Evidence"):
                            for s in result.sources:
                                speaker_str = f" ({s.speaker})" if s.speaker else ""
                                day_str = f" [{s.day}]" if s.day else ""
                                st.write(f"- \"{s.quote}\"{speaker_str}{day_str}")

if __name__ == "__main__":
    main()
