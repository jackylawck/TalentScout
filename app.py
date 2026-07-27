import streamlit as st
import pypdf
import docx
import json
import re
from openai import OpenAI
from google import genai
from google.genai import types

# Page Config
st.set_page_config(
    page_title="慧聘 · 智析官 | TalentScout AI",
    page_icon="🎯",
    layout="wide"
)

# 讀取後台預設 Secrets
default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# 語言選擇 (Sidebar 最頂層)
with st.sidebar:
    output_lang = st.selectbox(
        "🌐 界面與報告語言 (UI & Output Language):",
        ["繁體中文 (Traditional Chinese)", "English (Full)"],
        index=0
    )
    st.divider()

# UI 文字字典 (UI i18n Dictionary)
is_zh = output_lang == "繁體中文 (Traditional Chinese)"

ui_labels = {
    "sys_config": "⚙️ 系統設定 (System Config)" if is_zh else "⚙️ System Config",
    "key_mode": "選擇 AI 金鑰模式：" if is_zh else "Select AI Key Mode:",
    "default_key": "使用系統預設免費 Key" if is_zh else "Use System Default Free Key",
    "byok_key": "使用自備 AI API Key (自由選擇)" if is_zh else "Use Custom AI API Key (BYOK)",
    "loaded_default": "✅ 已載入系統預設免費 Key (保護中)" if is_zh else "✅ Loaded system default key (Protected)",
    "select_provider": "選擇你的 AI 供應商 (Provider)：" if is_zh else "Select AI Provider:",
    "enter_key": "輸入你的 {} Key" if is_zh else "Enter your {} Key",
    "framework_title": "🧠 人才科學與管治框架" if is_zh else "🧠 Talent Science & Governance",
    "framework_body": """
    - **人才密度 (Talent Density):** 識別 A 級玩家。
    - **組織契約 (Org. Contract):** 區分承諾型與交易型。
    - **ISO 42001 管治:** 落實高風險 AI 系統風險管控。
    - **AIGP 合規:** 確保 HITL (人類監督) 與去偏見 (Bias Mitigation)。
    """ if is_zh else """
    - **Talent Density:** Identify A-Players.
    - **Org. Contract:** Commitment vs. Transactional fit.
    - **ISO 42001:** High-risk AI risk management.
    - **AIGP Compliance:** Ensure HITL & Bias Mitigation.
    """,
    "governance_notice": "🔐 **數據管治聲明：** 本地 Session 運作，零數據留存。符合 PDPO 及歐盟 AI 法案 (EU AI Act) 合規指引。" if is_zh else "🔐 **Data Governance Notice:** Session-only operation with zero retention. Compliant with PDPO & EU AI Act guidance.",
    
    # Header & Sections
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)" if is_zh else "🎯 TalentScout AI",
    "subtitle": "🚀 **Universal AI-Driven Talent Science & Governance**｜內建 ISO 42001 與 AIGP 合規審查機制" if is_zh else "🚀 **Universal AI-Driven Talent Science & Governance**｜Embedded ISO 42001 & AIGP Audit Framework",
    "col1_title": "📄 1. 職位描述 (JD)" if is_zh else "📄 1. Job Description (JD)",
    "col1_caption": "📦 *支援多檔案上傳｜單檔上限 200 MB*" if is_zh else "📦 *Supports multiple files | Max 200 MB/file*",
    "input_mode": "輸入方式" if is_zh else "Input Method",
    "paste_text": "貼上文字" if is_zh else "Paste Text",
    "upload_files": "上傳文件 (可多選)" if is_zh else "Upload Files",
    "paste_jd_ph": "請貼上 JD 內容，包含職責與資格等..." if is_zh else "Paste JD content here including duties, requirements...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX, DOC)" if is_zh else "Upload JD Files (PDF, DOCX, DOC)",
    "jd_read_success": "✅ 已順利讀取 {} 個 JD 檔案" if is_zh else "✅ Successfully read {} JD file(s)",
    
    "col2_title": "👤 2. 求職者履歷 (CV)" if is_zh else "👤 2. Candidate Resume (CV)",
    "col2_caption": "📦 *支援多檔案上傳｜單檔上限 200 MB*" if is_zh else "📦 *Supports multiple files | Max 200 MB/file*",
    "upload_cv_lbl": "上傳 CV 檔案 (PDF, DOCX, DOC)" if is_zh else "Upload CV Files (PDF, DOCX, DOC)",
    "cv_read_success": "✅ 已順利讀取 {} 個 CV 檔案" if is_zh else "✅ Successfully read {} CV file(s)",
    
    "col3_title": "🎯 3. 特殊要求 (Preferences)" if is_zh else "🎯 3. Special Requirements",
    "col3_caption": "💡 *補充說明與團隊特定要求*" if is_zh else "💡 *Custom hiring criteria & preferences*",
    "special_req_ph": "例如：\n- 必須精通廣東話/英語\n- 必須接受每週 5 天到現場工作\n- 優先考慮具備金融背景者" if is_zh else "E.g.,\n- Must be fluent in Cantonese/English\n- 5 days on-site required\n- Prior banking background preferred",
    
    "run_btn": "🚀 啟動高階人才科學與合規審查 (Run Audit & Analysis)" if is_zh else "🚀 Run High-Level Talent Science & Compliance Audit",
    "spinner_msg": "資深 HR 顧問正結合人才科學與 ISO 42001 合規標準進行深度演算..." if is_zh else "Senior HR Advisory AI is executing deep Talent Science & ISO 42001 risk audit...",
    
    # Dashboard Titles
    "dash_sec1": "📊 1. 戰略匹配與人才密度 (Strategic Match & Talent Density)" if is_zh else "📊 1. Strategic Match & Talent Density",
    "overall_score": "綜合匹配得分 (Overall Score)" if is_zh else "Overall Score",
    "tier_label": "評級 (Tier)：{}" if is_zh else "Tier Rating: {}",
    "special_audit_title": "🎯 **特殊要求合規審查 (Special Requirements Audit):**" if is_zh else "🎯 **Special Requirements Audit:**",
    
    "dash_sec2": "⚖️ 2. AI 治理與合規審查 (AIGP & ISO 42001 Audit)" if is_zh else "⚖️ 2. AI Governance & Compliance Audit (AIGP & ISO 42001)",
    "dash_sec2_sub": "⚠️ *依據高風險 AI 系統管理框架，本系統提供以下決策輔助與風險緩解建議。*" if is_zh else "⚠️ *Under High-Risk AI System Frameworks, the system provides decision support and risk controls.*",
    "explainability": "🔍 **決策透明度與可解釋性 (Transparency & Explainability):**" if is_zh else "🔍 **Transparency & Explainability:**",
    "fairness": "⚖️ **公平性與偏見緩解 (Bias & Fairness Assessment):**" if is_zh else "⚖️ **Bias & Fairness Assessment:**",
    "hitl": "👨‍⚖️ **人類監督介入點 (Human-in-the-Loop, HITL):**" if is_zh else "👨‍⚖️ **Human-in-the-Loop (HITL) Triggers:**",
    "risk_control": "🛡️ **ISO 42001 風險管控行動 (Risk Controls):**" if is_zh else "🛡️ **ISO 42001 Risk Controls:**",
    
    "dash_sec3": "🏢 3. 組織契約與深層動機 (Org. Contract & Career Drivers)" if is_zh else "🏢 3. Organizational Contract & Career Drivers",
    "org_contract": "🤝 **組織用人模型 (Organizational Contract Fit):**" if is_zh else "🤝 **Organizational Contract Fit:**",
    "primary_driver": "🔥 **核心驅動力 (Primary Driver):** {}" if is_zh else "🔥 **Primary Driver:** {}",
    "offer_strategy": "💡 **專屬 Offer 說服策略 (Tailored Pitch Strategy):**" if is_zh else "💡 **Tailored Offer Pitch Strategy:**",
    
    "dash_sec4": "🎯 4. 實戰行為面試指南 (Behavioral STAR Interview)" if is_zh else "🎯 4. Behavioral STAR Interview Guide",
    "star_sub": "💡 *管治原則：嚴禁使用「假設性問題」，只探究真實歷史行為以預測未來表現。*" if is_zh else "💡 *Governance Rule: No hypothetical questions. Evaluate past behaviors to predict future performance.*",
    "kpi_focus": "📌 核心指標 (KPI Focus)：{}" if is_zh else "📌 KPI Focus: {}",
    "star_q": "🗣️ **歷史行為提問 (Behavioral Question)：** {}" if is_zh else "🗣️ **Behavioral Question:** {}",
    "star_probe": "🕵️ **測謊與深挖追問 (Anti-BS Probe)：** {}" if is_zh else "🕵️ **Anti-BS Probe:** {}"
}

# Sidebar: 設定與 Provider 處理
with st.sidebar:
    st.header(ui_labels["sys_config"])
    
    if default_token:
        key_mode = st.radio(
            ui_labels["key_mode"],
            [ui_labels["default_key"], ui_labels["byok_key"]],
            index=0
        )
    else:
        key_mode = ui_labels["byok_key"]

    if key_mode == ui_labels["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.success(ui_labels["loaded_default"])
    else:
        provider = st.selectbox(
            ui_labels["select_provider"],
            ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"]
        )
        
        help_texts = {
            "OpenAI": "OpenAI API Key (sk-...)",
            "DeepSeek": "DeepSeek API Key (sk-...)",
            "Google Gemini": "Google Gemini API Key (AIzaSy...)",
            "Groq": "Groq API Key (gsk_...)",
            "GitHub Models": "GitHub Personal Access Token (ghp_...)"
        }
        
        api_key = st.text_input(
            ui_labels["enter_key"].format(provider), 
            type="password",
            placeholder=help_texts[provider]
        )

    st.divider()
    st.markdown(ui_labels["framework_title"])
    st.markdown(ui_labels["framework_body"])
    st.divider()
    st.markdown(ui_labels["governance_notice"])

# 強健的文件文字提取函數
def extract_text_from_files(uploaded_files):
    if not uploaded_files:
        return ""
    
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
        
    combined_text = ""
    
    for file in uploaded_files:
        file_type = file.name.split('.')[-1].lower()
        file_text = ""
        try:
            if file_type == "pdf":
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    file_text += (page.extract_text() or "") + "\n"
            elif file_type in ["docx", "doc"]:
                doc = docx.Document(file)
                for para in doc.paragraphs:
                    file_text += para.text + "\n"
            
            if file_text.strip():
                combined_text += f"\n--- [Source: {file.name}] ---\n" + file_text
            else:
                st.warning(f"⚠️ `{file.name}` empty or unsupported binary `.doc`. Please 'Save As' `.docx` or `.pdf`.")
        except Exception as e:
            st.error(f"❌ Read failed for `{file.name}`. Please 'Save As' `.docx` or `.pdf`.")
            
    return combined_text

# Header
st.title(ui_labels["title"])
st.caption(ui_labels["subtitle"])

# Main UI: 三欄式上傳區
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader(ui_labels["col1_title"])
    st.caption(ui_labels["col1_caption"])
    jd_input_type = st.radio(ui_labels["input_mode"], [ui_labels["paste_text"], ui_labels["upload_files"]], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == ui_labels["paste_text"]:
        jd_text = st.text_area(ui_labels["paste_text"] + ":", height=200, placeholder=ui_labels["paste_jd_ph"])
    else:
        jd_files = st.file_uploader(
            ui_labels["upload_jd_lbl"], 
            type=["pdf", "docx", "doc"], 
            accept_multiple_files=True, 
            key="jd_files"
        )
        if jd_files:
            jd_text = extract_text_from_files(jd_files)
            if jd_text:
                st.success(ui_labels["jd_read_success"].format(len(jd_files)))

with col2:
    st.subheader(ui_labels["col2_title"])
    st.caption(ui_labels["col2_caption"])
    cv_files = st.file_uploader(
        ui_labels["upload_cv_lbl"], 
        type=["pdf", "docx", "doc"], 
        accept_multiple_files=True, 
        key="cv_files"
    )
    cv_text = ""
    if cv_files:
        cv_text = extract_text_from_files(cv_files)
        if cv_text:
            st.success(ui_labels["cv_read_success"].format(len(cv_files)))

with col3:
    st.subheader(ui_labels["col3_title"])
    st.caption(ui_labels["col3_caption"])
    special_reqs = st.text_area(
        ui_labels["col3_title"] + ":", 
        height=200, 
        placeholder=ui_labels["special_req_ph"]
    )

st.markdown("---")

# 核心分析呼叫函數
def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt + "\n\nFormat strictly as raw JSON without markdown.",
        )
        return response.text
    else:
        base_urls = {
            "OpenAI": "https://api.openai.com/v1",
            "DeepSeek": "https://api.deepseek.com",
            "Groq": "https://api.groq.com/openai/v1",
            "GitHub Models": "https://models.inference.ai.azure.com"
        }
        models = {
            "OpenAI": "gpt-4o-mini",
            "DeepSeek": "deepseek-chat",
            "Groq": "llama-3.3-70b-versatile",
            "GitHub Models": "gpt-4o-mini"
        }
        
        client = OpenAI(base_url=base_urls[provider], api_key=api_key)
        response = client.chat.completions.create(
            model=models[provider],
            messages=[
                {"role": "system", "content": "You are a professional HR Director and AI Governance Advisory system that outputs raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

# Analyze Button
if st.button(ui_labels["run_btn"], type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter API Key / Token!")
    elif not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ Please provide both valid JD and CV content!")
    else:
        with st.spinner(ui_labels["spinner_msg"]):
            try:
                lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文). Only keep standard industry abbreviations (e.g. JD, CV, AIGP, STAR, IT) if necessary." if is_zh else "Provide the ENTIRE analysis strictly in Professional Executive English."
                
                # 資深 HR Director 賦能 Prompt
                prompt = f"""
You are an exceptionally experienced Senior HR Director and Talent Advisory Consultant operating at the board/executive level in Hong Kong.
Analyze the provided Job Description (JD) and Candidate CV with deep HR acumen, strategic foresight, and rigid ISO 42001 / AIGP compliance awareness.

Language Requirement:
{lang_instruction}

Special Requirements:
{special_reqs if special_reqs.strip() else "None specified."}

### HR Evaluation Guidelines:
1. **Avoid Rigid Assumptions:** Do NOT conflate a lack of domain knowledge (e.g., construction) with a lack of soft skills (e.g., predicting boss's needs). Distinguish clearly between "Hard Industry Experience Gaps" and "Transferable Soft Skills".
2. **Be Specific & Actionable:** Quote exact, concrete details from the CV (e.g., flight attendant experience, computer science degree, ASMTP visa status, Cantonese fluency level, salary expectations) rather than generic boilerplate feedback.
3. **Professional HR Tone:** Write as a strategic HR partner advising a Managing Director (MD) or Line Manager. Balance risk warnings with talent potential.

Format your output STRICTLY in valid JSON matching this schema:
{{
  "overall_score": 75,
  "talent_density_tier": "B-Player (高可塑性跨界人才)",
  "special_req_compliance": "Provide a nuanced, professional HR assessment of how the candidate aligns with the special preferences. Distinguish clearly between Hard Industry Experience (e.g., Construction) and Transferable Attributes (e.g., Independence, Proactivity). Avoid lazy 'Fail' labels if soft skills are strong.",
  "organizational_contract": "In-depth HR analysis on whether this is a Transactional Fit (e.g., short-term visa need/stepping stone) or Commitment Fit (long-term career growth), referencing specific career transitions in the CV.",
  "career_driver_analysis": {{
    "primary_driver": "Identify the candidate's genuine career driver based on their actual background (e.g., transitioning from technical/cabin roles to executive support).",
    "offer_strategy": "Concrete, strategic pitch advice for the MD/HR to close this candidate (e.g., emphasizing mentorship, technology integration, or clear progression)."
  }},
  "aigp_governance_audit": {{
    "transparency_explainability": "State clearly the key weighting factors driving this score (e.g., high score for analytical/crisis skills vs penalty for industry/language gaps).",
    "human_in_the_loop_flag": "Highlight specific high-risk claims, gap areas, or administrative hurdles (e.g., ASMTP visa sponsorship, Cantonese fluency, career jumpiness) that MUST be validated human-to-human by HR/MD.",
    "bias_and_fairness": "Fairness assessment: Warn against potential 'Prestige Bias' or 'Non-traditional Background Bias' that might cause the line manager to prematurely reject a high-potential candidate.",
    "iso42001_risk_control": "Give 1-2 actionable risk mitigation steps for the Hiring Manager before making a final decision (e.g., phone screen for visa/language first, structured case study)."
  }},
  "sourcing_expansion": "Unconventional sourcing advice for this role.",
  "behavioral_star_questions": [
    {{
      "kpi_focus": "Specific competency matching the JD & Special Reqs (e.g., Free-hand Proactivity / Crisis Stakeholder Mgt)",
      "question": "A sharp, highly realistic past-behavioral STAR question probing real historical evidence.",
      "anti_bs_probe": "A sharp follow-up probe specifically designed to verify authenticity and prevent rehearsed/generic answers."
    }}
  ]
}}

Output ONLY raw JSON.

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                clean_json = json_match.group(0) if json_match else raw_response.strip()
                data = json.loads(clean_json)
                
                # Dashboard Visualization
                st.markdown(f"## {ui_labels['dash_sec1']}")
                colA, colB = st.columns(2)
                with colA:
                    st.metric(label=ui_labels["overall_score"], value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with colB:
                    tier = data['talent_density_tier']
                    tier_str = ui_labels["tier_label"].format(tier)
                    if any(x in tier for x in ["A", "磁石"]):
                        st.success(f"🏆 {tier_str}")
                    elif any(x in tier for x in ["B", "中流", "潛力", "可塑"]):
                        st.info(f"👍 {tier_str}")
                    else:
                        st.error(f"⚠️ {tier_str}")

                if special_reqs.strip():
                    st.info(f"{ui_labels['special_audit_title']}\n\n{data.get('special_req_compliance', '')}")

                st.markdown("---")
                st.markdown(f"## {ui_labels['dash_sec2']}")
                st.caption(ui_labels["dash_sec2_sub"])
                
                gov1, gov2 = st.columns(2)
                with gov1:
                    st.markdown(ui_labels["explainability"])
                    st.write(data['aigp_governance_audit']['transparency_explainability'])
                    
                    st.markdown(ui_labels["fairness"])
                    st.write(data['aigp_governance_audit']['bias_and_fairness'])
                
                with gov2:
                    st.error(f"{ui_labels['hitl']}\n\n{data['aigp_governance_audit']['human_in_the_loop_flag']}")
                    st.warning(f"{ui_labels['risk_control']}\n\n{data['aigp_governance_audit']['iso42001_risk_control']}")

                st.markdown("---")
                st.markdown(f"## {ui_labels['dash_sec3']}")
                strat1, strat2 = st.columns(2)
                with strat1:
                    st.markdown(ui_labels["org_contract"])
                    st.write(data['organizational_contract'])
                with strat2:
                    st.markdown(ui_labels["primary_driver"].format(data['career_driver_analysis']['primary_driver']))
                    st.markdown(ui_labels["offer_strategy"])
                    st.write(data['career_driver_analysis']['offer_strategy'])

                st.markdown("---")
                st.markdown(f"## {ui_labels['dash_sec4']}")
                st.caption(ui_labels["star_sub"])
                for idx, q in enumerate(data['behavioral_star_questions'], 1):
                    with st.expander(ui_labels["kpi_focus"].format(q['kpi_focus'])):
                        st.markdown(ui_labels["star_q"].format(q['question']))
                        st.markdown(ui_labels["star_probe"].format(q['anti_bs_probe']))
                        
            except Exception as e:
                st.error(f"❌ Analysis Error / 分析過程出現錯誤: {str(e)}")
