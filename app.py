import streamlit as st
import pypdf
import json
from google import genai
from google.genai import types

# Page Config
st.set_page_config(
    page_title="慧聘 · 智析官 | TalentScout AI",
    page_icon="🎯",
    layout="wide"
)

# Header
st.title("🎯 慧聘 · 智析官 (TalentScout AI) - 5.0 雙語全能版")
st.caption("🚀 **AI-First TA Transformation** | 融合精準科學 (Precision Science)、人才預測與 AI 管治 (AI Governance)")

# Sidebar: Config & Theories
with st.sidebar:
    st.header("⚙️ 系統設定 (System Config)")
    api_key = st.text_input("輸入 Gemini API Key (Enter Key)", type="password")
    st.markdown("[👉 申請免費 API Key (Get Free Key)](https://aistudio.google.com/)")
    st.divider()
    
    st.markdown("### 🧠 內建頂層 TA 戰略 (Embedded TA Strategies)")
    st.markdown("""
    - **TA vs. Recruitment:** 長遠人才管道預測 (Pipeline Forecasting)。
    - **Internal Mobility (內部流動):** 預測跨領域發展潛力，提升留存率。
    - **Candidate Experience (CX):** 量身定制的溝通與招募培育策略 (Nurturing)。
    - **AI Governance & Trust:** 偏見風險檢測，確保招聘透明度與合規性。
    """)
    st.divider()
    st.markdown("🔐 **私隱聲明 (Privacy Policy):** 數據僅存於本地 Session，零上傳 (Zero Data Retention)，符合香港 PDPO 及企業級 AI 風險管治標準。")

def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Main UI: Upload Section
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 1. 職位描述 (Job Description)")
    jd_input_type = st.radio("輸入方式 (Input Method)", ["貼上文字 (Text)", "上傳 PDF (PDF)"], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == "貼上文字 (Text)":
        jd_text = st.text_area("請貼上 JD 內容 (Paste JD here)：", height=200)
    else:
        jd_file = st.file_uploader("上傳 JD PDF (Upload JD)", type=["pdf"], key="jd_pdf")
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file)

with col2:
    st.subheader("👤 2. 求職者履歷 (Candidate CV)")
    cv_file = st.file_uploader("上傳履歷 PDF (Upload CV)", type=["pdf"], key="cv_pdf")
    cv_text = ""
    if cv_file:
        cv_text = extract_text_from_pdf(cv_file)
        st.success(f"✅ 已讀取 CV (CV Loaded)：{cv_file.name}")

st.markdown("---")

# JSON Schema for AI Output
analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "overall_score": {"type": "INTEGER", "description": "0-100 Match Score"},
        "abc_tier": {"type": "STRING", "description": "A-Tier (堅決拿下) / B-Tier (符合預期) / C-Tier (堅決淘汰)"},
        "ta_vs_recruitment": {
            "type": "STRING", 
            "description": "Board-level perspective: Is this a short-term reactive hire (Recruitment) or a long-term strategic asset (Talent Acquisition)? Explain why."
        },
        "internal_mobility": {
            "type": "STRING",
            "description": "Forecasting: Predict the candidate's cross-skilling potential and internal mobility for future roles within the organization."
        },
        "candidate_experience_guide": {
            "type": "STRING",
            "description": "How should the recruiter nurture this candidate? Provide a strategy to ensure a positive Candidate Experience (CX) to secure offer acceptance."
        },
        "ai_governance_and_bias_check": {
            "type": "STRING",
            "description": "AI Risk Management: Are there any potential biases (age, gender, background) in how this CV might be traditionally evaluated? Provide a transparency statement for the candidate."
        },
        "kpi_star_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "kpi_focus": {"type": "STRING", "description": "The specific KPI or core competency being tested."},
                    "question": {"type": "STRING", "description": "STAR question focusing on past failures/challenges."},
                    "what_to_look_for": {"type": "STRING", "description": "What underlying attitude or skill to evaluate."}
                }
            }
        }
    },
    "required": ["overall_score", "abc_tier", "ta_vs_recruitment", "internal_mobility", "candidate_experience_guide", "ai_governance_and_bias_check", "kpi_star_questions"]
}

# Analyze Button
if st.button("🚀 啟動 AI 戰略透視 (Run AI Strategic Analysis)", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ 請在左側輸入 Gemini API Key (Please enter API Key in sidebar)！")
    elif not jd_text or not cv_text:
        st.warning("⚠️ 請提供 JD 與 CV (Please provide both JD and CV)！")
    else:
        with st.spinner("AI 正在進行企業級人才與風險管治分析 (Running Enterprise-grade TA & Risk Analysis)..."):
            try:
                client = genai.Client(api_key=api_key)
                
                # Bilingual AI Prompt with Governance & Executive perspective
                prompt = f"""
You are an elite Head of Talent Acquisition and AI Governance Expert operating in Hong Kong. 
Analyze the JD and CV using precision science. Focus on Talent Acquisition (long-term pipeline) rather than just Recruitment (short-term fix).
Incorporate Iceberg Theory, Internal Mobility forecasting, Candidate Experience (CX), and AI Risk Management.

Format your output in a highly professional Bilingual format: Traditional Chinese mixed with relevant English HR/Board-level terminology (e.g., "內部流動性 (Internal Mobility)").

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=analysis_schema,
                        temperature=0.2
                    ),
                )
                
                data = json.loads(response.text)
                
                # ================= Dashboard Visualization =================
                st.markdown("## 📊 1. 戰略定位與綜合匹配 (Strategic Positioning & Match)")
                colA, colB = st.columns(2)
                with colA:
                    st.metric(label="綜合匹配得分 (Overall Score)", value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with colB:
                    tier = data['abc_tier']
                    if "A" in tier:
                        st.success(f"🏆 評級 (Tier)：{tier}")
                    elif "B" in tier:
                        st.info(f"👍 評級 (Tier)：{tier}")
                    else:
                        st.error(f"⚠️ 評級 (Tier)：{tier}")

                st.markdown("---")
                st.markdown("## 🏢 2. 企業級人才戰略 (Enterprise Talent Strategy)")
                strat1, strat2 = st.columns(2)
                with strat1:
                    st.markdown("**🔍 長遠獲取 vs 短期招聘 (TA vs. Recruitment):**")
                    st.write(data['ta_vs_recruitment'])
                with strat2:
                    st.markdown("**🔄 內部流動與跨領域預測 (Internal Mobility Forecasting):**")
                    st.write(data['internal_mobility'])

                st.markdown("---")
                st.markdown("## 🛡️ 3. 候選人體驗與 AI 管治 (CX & AI Governance)")
                gov1, gov2 = st.columns(2)
                with gov1:
                    st.info(f"**🤝 招募培育與溝通策略 (Candidate Nurturing & CX):**\n\n{data['candidate_experience_guide']}")
                with gov2:
                    st.warning(f"**⚖️ 偏見風險與透明度審查 (Bias Check & Transparency):**\n\n{data['ai_governance_and_bias_check']}")

                st.markdown("---")
                st.markdown("## 🎯 4. KPI 導向 STAR 面試攻防 (KPI-Driven STAR Interview)")
                st.caption("💡 *Focus: Deep-dive into past challenges to evaluate core competencies.*")
                for idx, q in enumerate(data['kpi_star_questions'], 1):
                    with st.expander(f"📌 題目 {idx} | 核心指標 (KPI Focus)：{q['kpi_focus']}"):
                        st.markdown(f"**🗣️ 靈魂拷問 (Question)：** {q['question']}")
                        st.markdown(f"**👁️ 考官觀察重點 (What to look for)：** {q['what_to_look_for']}")
                        
            except Exception as e:
                st.error(f"❌ 分析過程出現錯誤 (Error during analysis)：{str(e)}")
