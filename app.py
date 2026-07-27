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
st.title("🎯 慧聘 · 智析官 (TalentScout AI) - 6.0 終極大師版")
st.caption("🚀 **AI-Driven Talent Science** | 融合人才密度效應、組織契約模型、職涯驅動力與 AI 管治")

# Sidebar: Config
with st.sidebar:
    st.header("⚙️ 系統設定 (System Config)")
    api_key = st.text_input("輸入 Gemini API Key (Enter Key)", type="password")
    st.markdown("[👉 申請免費 API Key (Get Free Key)](https://aistudio.google.com/)")
    st.divider()
    
    st.markdown("### 🧠 內建人才科學框架 (Talent Science Framework)")
    st.markdown("""
    - **人才密度效應 (Talent Density):** 識別能吸引頂尖人才的 A 級玩家。
    - **組織契約模型 (Organizational Contract):** 區分「長期承諾型」與「短期交易型」用人策略。
    - **職涯驅動力 (Career Drivers):** 洞察深層動機，定制 Offer 談判策略。
    - **認知偏差預警 (Bias Warning):** 預防「光環效應 (Halo Effect)」與倉促招聘。
    """)
    st.divider()
    st.markdown("🔐 **數據管治聲明 (Data Governance):** 採用 BYOK 架構，零數據留存 (Zero Data Retention)，完全符合企業級合規與隱私標準。")

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

# JSON Schema (Enhanced with advanced recruitment theories)
analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "overall_score": {"type": "INTEGER", "description": "0-100 Match Score"},
        "talent_density_tier": {"type": "STRING", "description": "A-Player (人才磁石) / B-Player (中流砥柱) / C-Player (平庸擴散風險)"},
        "organizational_contract": {
            "type": "STRING", 
            "description": "Assess if JD needs a 'Commitment Model' (cultural fit, long-term) or 'Transactional Model' (immediate skills, short-term). State how the CV aligns with this."
        },
        "career_driver_analysis": {
            "type": "OBJECT",
            "properties": {
                "primary_driver": {"type": "STRING", "description": "Identify the candidate's core need (e.g., Financial/Survival, Security/Stability, Social/Belonging, Esteem/Recognition, or Self-Actualization)."},
                "offer_strategy": {"type": "STRING", "description": "How to tailor the recruitment pitch and offer based on their primary driver."}
            }
        },
        "bias_and_risk_warning": {
            "type": "OBJECT",
            "properties": {
                "halo_effect_warning": {"type": "STRING", "description": "Identify any 'Halo Effect' risks (e.g., being blinded by a famous past employer or education) that require objective verification."},
                "flight_risk": {"type": "STRING", "description": "Assess overqualification or mismatched pacing that could lead to early departure."}
            }
        },
        "sourcing_expansion": {
            "type": "STRING",
            "description": "If we want to clone this candidate profile, suggest 2 unconventional sourcing channels (e.g., specific hackathons, niche communities, employee referral angles)."
        },
        "behavioral_star_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "kpi_focus": {"type": "STRING", "description": "Core competency being tested."},
                    "question": {"type": "STRING", "description": "Strictly behavioral question (past actions only, ZERO hypothetical 'what would you do' questions)."},
                    "anti_bs_probe": {"type": "STRING", "description": "Follow-up question to dig into the details and prevent scripted/fake answers."}
                }
            }
        }
    },
    "required": ["overall_score", "talent_density_tier", "organizational_contract", "career_driver_analysis", "bias_and_risk_warning", "sourcing_expansion", "behavioral_star_questions"]
}

# Analyze Button
if st.button("🚀 啟動高階人才科學分析 (Run Advanced Talent Science Analysis)", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ 請在左側輸入 Gemini API Key (Please enter API Key in sidebar)！")
    elif not jd_text or not cv_text:
        st.warning("⚠️ 請提供 JD 與 CV (Please provide both JD and CV)！")
    else:
        with st.spinner("AI 正在執行組織契約與人才密度綜合演算 (Computing Talent Density & Organizational Fit)..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
You are a top-tier HR Executive and AI Governance Lead in Hong Kong. 
Analyze the JD and CV using deep Talent Science principles without directly naming specific authors/theories. 
Apply the concepts of Talent Density (A-players vs B/C-players), Organizational Contract Models (Commitment vs Transactional), Driver/Needs Analysis for offer closing, and strictly warn against cognitive biases like the Halo Effect.

Format your output in professional Bilingual format: Traditional Chinese mixed with standard English HR terminology. 

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
                st.markdown("## 📊 1. 戰略匹配與人才密度 (Strategic Match & Talent Density)")
                colA, colB = st.columns(2)
                with colA:
                    st.metric(label="綜合匹配得分 (Overall Score)", value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with colB:
                    tier = data['talent_density_tier']
                    if "A" in tier or "磁石" in tier:
                        st.success(f"🏆 評級 (Tier)：{tier}")
                    elif "B" in tier or "中流" in tier:
                        st.info(f"👍 評級 (Tier)：{tier}")
                    else:
                        st.error(f"⚠️ 評級 (Tier)：{tier}")

                st.markdown("---")
                st.markdown("## 🏢 2. 組織契約與深層動機 (Org. Contract & Career Drivers)")
                strat1, strat2 = st.columns(2)
                with strat1:
                    st.markdown("**🤝 組織用人模型 (Organizational Contract Fit):**")
                    st.write(data['organizational_contract'])
                with strat2:
                    st.markdown(f"**🔥 核心驅動力 (Primary Driver):** {data['career_driver_analysis']['primary_driver']}")
                    st.markdown("**💡 專屬 Offer 說服策略 (Tailored Pitch Strategy):**")
                    st.write(data['career_driver_analysis']['offer_strategy'])

                st.markdown("---")
                st.markdown("## 🛡️ 3. 認知偏差預警與風險管治 (Bias Warning & Risk Mgt)")
                gov1, gov2 = st.columns(2)
                with gov1:
                    st.warning(f"**👁️ 光環效應預警 (Halo Effect Warning):**\n\n{data['bias_and_risk_warning']['halo_effect_warning']}")
                with gov2:
                    st.error(f"**🛫 流失與錯配風險 (Flight Risk):**\n\n{data['bias_and_risk_warning']['flight_risk']}")

                st.markdown("---")
                st.markdown("## 🌐 4. 尋源與雇主品牌擴展 (Sourcing & Talent Pipeline)")
                st.info(f"**💡 尋源拓展建議 (Unconventional Sourcing):**\n{data['sourcing_expansion']}")

                st.markdown("---")
                st.markdown("## 🎯 5. 實戰行為面試指南 (Behavioral STAR Interview)")
                st.caption("💡 *管治原則：嚴禁使用「假設性問題」，只探究真實歷史行為以預測未來表現。*")
                for idx, q in enumerate(data['behavioral_star_questions'], 1):
                    with st.expander(f"📌 核心指標 (KPI Focus)：{q['kpi_focus']}"):
                        st.markdown(f"**🗣️ 歷史行為提問 (Behavioral Question)：** {q['question']}")
                        st.markdown(f"**🕵️ 測謊與深挖追問 (Anti-BS Probe)：** {q['anti_bs_probe']}")
                        
            except Exception as e:
                st.error(f"❌ 分析過程出現錯誤 (Error during analysis)：{str(e)}")
