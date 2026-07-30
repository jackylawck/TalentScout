import streamlit as st
import pypdf
import docx
import json
import re
import time
from openai import OpenAI
from google import genai
from google.genai import types
import traceback

# ==========================================
# 1. Page Config & State Initialization
# ==========================================
st.set_page_config(
    page_title="慧聘 · 智析官 | TalentScout AI",
    page_icon="🎯",
    layout="wide"
)

if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}  
if 'hr_feedback_history' not in st.session_state:
    st.session_state.hr_feedback_history = {} 

token_github = st.secrets.get("GITHUB_TOKEN", "")
token_gemini = st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. Localization Dictionaries (語系解耦)
# ==========================================
UI_ZH = {
    "sys_config": "⚙️ 系統設定",
    "key_mode": "選擇 AI 金鑰模式：",
    "default_key": "使用開源公共免費額度 (單次 1 份 CV)",
    "byok_key": "使用自備 AI API Key (支援多 CV 批量)",
    "loaded_default": "🌱 **開源公共資源已載入 (10次/Session)**。免費模式下**每次限上傳 1 份 CV** 以確保順暢體驗。若需批量評估多份履歷，歡迎切換為自備 Key！",
    "quota_exceeded": "🤝 **本 Session 試用額度已達上限。** 請刷新網頁（F5）或切換至『使用自備 AI API Key』繼續使用！",
    "single_cv_notice": "💡 **免費試用提示：** 開源免費額度每次限解析 **1 份 CV**。如需一次批量解析多份履歷，請於左側切換為「使用自備 AI API Key」。",
    "select_provider": "選擇 AI 供應商：",
    "enter_key": "輸入你的 {} Key",
    "framework_title": "🛡️ 數據安全與進階 HR 管治特色",
    "framework_body": """
    **🔐 企業隱私防護:**
    - **零數據留存:** 運算僅存於本地 Session 記憶體，重整即刻物理銷毀。
    **🎯 進階 HR Tech 引擎:**
    - **多 CV 獨立解析 (BYOK 模式):** 批量上傳，獨立分頁精準生成決策報告。
    - **深度 DEI 詞彙偵測:** 具體揪出潛在偏見字眼並提供修正。
    - **決策報告一鍵匯出:** 支援將分析結果匯出為 Markdown。
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)",
    "subtitle": "🚀 **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**",
    "col1_title": "📄 1. 職位描述 (JD)",
    "input_mode_lbl": "輸入方式",
    "input_modes": ["貼上文字", "上傳文件"],
    "jd_ph": "請貼上 JD 內容，包含職責與資格等...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX, 限 15MB 內)",
    "col2_title": "👤 2. 求職者履歷 (CV)",
    "upload_cv_lbl": "上傳 CV 檔案 (免費額度限 1 檔，BYOK 可多選)",
    "col3_title": "🎯 3. 招聘情境與設定",
    "referral_lbl": "🎖️ 此批次包含內部員工推薦",
    "urgency_lbl": "⏳ 職位招聘急迫性",
    "urgency_opts": ["標準 (Standard)", "緊急 (Urgent)"],
    "special_req_lbl": "其他特殊要求 (JD 補充)",
    "special_req_ph": "例如：必須精通廣東話、具備 ISO 審計經驗",
    "run_btn": "🚀 啟動多維度 ATS 解析與結構化評估",
    "status_analyzing": "🚀 正在獨立解析候選人：{}",
    "err_json": "❌ AI 回傳格式解析失敗。請嘗試重新執行。",
    "err_api": "❌ API 呼叫失敗。請檢查 API Key 或網路連線。",
    "sec1_title": "📊 1. 漏斗決策與 ATS 匹配度",
    "m_score": "綜合勝任力得分",
    "m_ats": "ATS 關鍵字匹配率",
    "m_rec": "漏斗轉換建議",
    "m_time": "到職時效評估",
    "ats_matched": "✅ 命中關鍵字:",
    "ats_missing": "❌ 缺失關鍵字:",
    "sec2_title": "📈 2. 核心勝任力維度拆解",
    "evidence_source": "證據來源",
    "sec3_title": "🛡️ 3. DEI 防偏誤審查與風險管治",
    "dei_check": "⚖️ DEI 潛在偏見詞彙與防偏誤措施:",
    "hard_risks": "🚨 絕對風險/合規死線:",
    "soft_risks": "⚠️ 軟性風險/面試觀察點:",
    "sec4_title": "🎯 4. 結構化面試量表 (STAR)",
    "sec4_sub": "💡 *基於勝任力模型生成之標準化評分題庫，確保面試官評分一致性。*",
    "probe_q": "🗣️ 面試題:",
    "rubric_5": "🟢 5分 (優秀):",
    "rubric_3": "🟡 3分 (合格):",
    "rubric_1": "🔴 1分 (需關注):",
    "sec5_title": "🤝 5. HR 漏斗覆核與動態校正 (HITL)",
    "feedback_ph": "輸入針對此候選人的初篩結果或補充觀察...",
    "re_eval_btn": "🔄 結合 HR 反饋重新校正此候選人模型",
    "download_btn": "📥 下載評估報告 (Markdown)"
}

UI_EN = {
    "sys_config": "⚙️ System Config",
    "key_mode": "Select AI Key Mode:",
    "default_key": "Use Open-Source Public Quota (1 CV max)",
    "byok_key": "Use Custom API Key (Batch CVs enabled)",
    "loaded_default": "🌱 **Public Quota Loaded (10 uses/session).** Free mode is limited to **1 CV per run**. Switch to BYOK for unlimited batch evaluation!",
    "quota_exceeded": "🤝 **Quota Reached!** Please refresh page or switch to 'Custom Key' to continue.",
    "single_cv_notice": "💡 **Free Quota Notice:** Public quota processes **1 CV per run**. Switch to 'Custom Key' in sidebar for multi-CV batch processing.",
    "select_provider": "Select AI Provider:",
    "enter_key": "Enter your {} Key",
    "framework_title": "🛡️ Privacy & AI Governance",
    "framework_body": """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Retention:** Processed strictly in-memory per session.
    **🎯 Advanced HR Tech Engine:**
    - **Isolated Multi-CV Tabs (BYOK Mode):** Process batch uploads with independent tabs.
    - **Deep DEI Auditing:** Explicitly flags biased terminology.
    - **One-Click Export:** Download full assessment reports in Markdown.
    """,
    "title": "🎯 TalentScout AI",
    "subtitle": "🚀 **Enterprise ATS Screening, Competency Assessment & DEI Governance System**",
    "col1_title": "📄 1. Job Description (JD)",
    "input_mode_lbl": "Input Method",
    "input_modes": ["Paste Text", "Upload Files"],
    "jd_ph": "Paste JD content here including duties, requirements...",
    "upload_jd_lbl": "Upload JD Files (PDF, DOCX, Max 15MB)",
    "col2_title": "👤 2. Candidate Resumes (CV)",
    "upload_cv_lbl": "Upload CV Files (Max 1 in Free Mode, Batch in BYOK)",
    "col3_title": "🎯 3. Hiring Context",
    "referral_lbl": "🎖️ Internal Referral Batch",
    "urgency_lbl": "⏳ Time-to-Fill Urgency",
    "urgency_opts": ["Standard", "Urgent"],
    "special_req_lbl": "Special Requirements (JD Add-on)",
    "special_req_ph": "E.g., Fluent Cantonese, ISO Audit experience required",
    "run_btn": "🚀 Run Full ATS & Competency Audit",
    "status_analyzing": "🚀 Independently analyzing candidate: {}",
    "err_json": "❌ JSON Parse Error. The AI output was malformed.",
    "err_api": "❌ API Connection Error. Please check your network or API Key.",
    "sec1_title": "📊 1. Funnel Verdict & ATS Match",
    "m_score": "Competency Score",
    "m_ats": "ATS Keyword Match",
    "m_rec": "Funnel Recommendation",
    "m_time": "Time-to-Fill Assessment",
    "ats_matched": "✅ Matched Keywords:",
    "ats_missing": "❌ Missing Keywords:",
    "sec2_title": "📈 2. Core Competency Breakdown",
    "evidence_source": "Evidence Source",
    "sec3_title": "🛡️ 3. DEI Safeguards & Risk Governance",
    "dei_check": "⚖️ DEI Biased Keywords Flagged & Mitigation:",
    "hard_risks": "🚨 Hard Risks / Compliance Blocks:",
    "soft_risks": "⚠️ Soft Risks / Interview Focus:",
    "sec4_title": "🎯 4. Structured Interview Rubric (STAR)",
    "sec4_sub": "💡 *Standardized scoring rubrics generated based on competency models for consistency.*",
    "probe_q": "🗣️ Question:",
    "rubric_5": "🟢 5 pts (Excellent):",
    "rubric_3": "🟡 3 pts (Acceptable):",
    "rubric_1": "🔴 1 pt (Poor):",
    "sec5_title": "🤝 5. Human-in-the-Loop Re-eval",
    "feedback_ph": "Enter HR screening notes for this specific candidate...",
    "re_eval_btn": "🔄 Update Evaluation for this Candidate",
    "download_btn": "📥 Download Assessment Report (Markdown)"
}

with st.sidebar:
    output_lang = st.selectbox("🌐 界面與報告語言 (UI & Output Language):", ["繁體中文 (Traditional Chinese)", "English (Full)"], index=0)
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"
def get_ui(key, default=""):
    return (UI_ZH if is_zh else UI_EN).get(key, default)

# ==========================================
# 3. Sidebar Config (Smart Provider Routing)
# ==========================================
AI_PROVIDERS = {
    "GitHub Models": {"url": "https://models.inference.ai.azure.com", "model": "gpt-4o-mini"},
    "OpenAI": {"url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "DeepSeek": {"url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "Groq": {"url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
    "Google Gemini": {"url": "N/A", "model": "gemini-2.5-flash"}
}

with st.sidebar:
    st.header(get_ui("sys_config"))
    if token_github or token_gemini:
        key_mode = st.radio(get_ui("key_mode"), [get_ui("default_key"), get_ui("byok_key")], index=0)
    else:
        key_mode = get_ui("byok_key")

    if key_mode == get_ui("default_key"):
        if token_github:
            provider = "GitHub Models"
            api_key = token_github
        else:
            provider = "Google Gemini"
            api_key = token_gemini
        st.info(get_ui("loaded_default") + f"\n\n*(Current Engine: **{provider}**)*")
    else:
        provider = st.selectbox(get_ui("select_provider"), list(AI_PROVIDERS.keys()))
        api_key = st.text_input(get_ui("enter_key").format(provider), type="password")
    
    st.divider()
    st.markdown(get_ui("framework_title"))
    st.markdown(get_ui("framework_body"))

def check_quota():
    if key_mode == get_ui("default_key"):
        if st.session_state.usage_count >= 10:
            st.error(get_ui("quota_exceeded"))
            st.stop()
        st.session_state.usage_count += 1

# ==========================================
# 4. Core Functions & UI Helpers
# ==========================================
def extract_single_file(file):
    if not file: return ""
    text = ""
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == "pdf":
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages: text += (page.extract_text() or "") + "\n"
        elif file_type in ["docx", "doc"]:
            doc = docx.Document(file)
            for para in doc.paragraphs: text += para.text + "\n"
    except Exception:
        pass
    return text.strip()

def extract_text_from_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    return "\n".join([extract_single_file(f) for f in uploaded_files])

def format_tab_name(filename):
    clean = re.sub(r'(?i)(\.pdf|\.docx|\.doc)', '', filename)
    clean = re.sub(r'(?i)(resume|cv|profile|履歷).*', '', clean).strip()
    words = clean.split()
    if len(words) > 2:
        cut_idx = len(words)
        for i, w in enumerate(words):
            if w.lower() in ['executive', 'assistant', 'manager', 'director', 'senior', 'head', 'lead']:
                cut_idx = i
                break
        if 0 < cut_idx < len(words):
            return " ".join(words[:cut_idx])
        return " ".join(words[:4]) + "..." if len(words) > 4 else clean
    return clean

def robust_json_parse(raw_text):
    try:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
        if match: return json.loads(match.group(1).strip())
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match: return json.loads(match.group(0).strip())
        return json.loads(raw_text.strip())
    except Exception as e:
        raise ValueError("JSON Parsing Failed") from e

def build_evaluation_prompt(lang, is_ref, urgency, special, jd, cv, feedback=""):
    lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文), using senior executive HR terminology." if lang else "Provide the ENTIRE analysis strictly in Professional Executive English."
    referral_instruction = "This candidate is an INTERNAL REFERRAL. Apply referral weighting." if is_ref else ""
    feedback_prompt = f"\n\n### HR Human-in-the-Loop Feedback for this candidate:\n{feedback}\n(Integrate this human insight into your strategic assessment.)" if feedback.strip() else ""
    
    return f"""
You are a Senior Executive HR Consultant and Board-Level Talent Advisor. Evaluate this SINGLE candidate against the JD using advanced Competency Modeling, ATS Extraction, DEI Safeguards, and Structured Interview Rubrics. 
Your tone MUST be highly professional, analytical, and strategic.

Language Requirement:
{lang_instruction}

Context Parameters:
- Internal Referral: {is_ref} ({referral_instruction})
- Urgency: {urgency}
- Special Req: {special}
{feedback_prompt}

Format your output STRICTLY in valid JSON matching this schema:
{{
  "funnel_and_ats": {{
    "competency_overall_score": 85,
    "ats_match_percentage": 75,
    "matched_keywords": ["Strategic Planning", "Stakeholder Management"],
    "missing_keywords": ["P&L Management"],
    "funnel_recommendation": "Executive summary of next steps.",
    "time_to_fill_assessment": "Strategic risk assessment of onboarding timeline."
  }},
  "competency_breakdown": [
    {{
      "dimension": "e.g., Strategic Execution & Leadership",
      "score": "80/100",
      "justification": "Deep analytical justification using executive HR terminology, explicitly citing evidence.",
      "evidence": "Direct quote or specific metric from CV"
    }}
  ],
  "dei_and_risks": {{
    "dei_safeguard_applied": "Specific executive audit note on how bias was actively mitigated.",
    "hard_risks": ["Critical compliance or hard-skill blockers"],
    "soft_risks": ["Nuanced behavioral or cultural fit observation points"]
  }},
  "structured_interview_rubric": [
    {{
      "competency_tested": "Specific executive competency",
      "star_question": "Challenging, senior-level behavioral question",
      "rubric_5_excellent": "Strategic, outcome-driven response pattern",
      "rubric_3_acceptable": "Tactical but functional response pattern",
      "rubric_1_poor": "Red flag response indicating poor judgment or lack of scale"
    }}
  ]
}}

Output ONLY raw JSON.

Job Description (JD):
{jd}

Candidate CV:
{cv}
"""

def run_ai_analysis(provider, api_key, prompt):
    cfg = AI_PROVIDERS[provider]
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            if provider == "Google Gemini":
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=cfg["model"], 
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
                )
                return response.text
            else:
                client = OpenAI(base_url=cfg["url"], api_key=api_key)
                response = client.chat.completions.create(
                    model=cfg["model"],
                    messages=[{"role": "system", "content": "You are a Senior Executive HR Consultant outputting raw JSON."}, {"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                raise e

def generate_markdown_report(cand_name, data):
    funnel = data.get('funnel_and_ats', {})
    dei = data.get('dei_and_risks', {})
    md = f"# TalentScout Assessment Report: {cand_name}\n\n"
    md += f"## {get_ui('sec1_title')}\n"
    md += f"- **{get_ui('m_score')}:** {funnel.get('competency_overall_score', 'N/A')}/100\n"
    md += f"- **{get_ui('m_ats')}:** {funnel.get('ats_match_percentage', 'N/A')}%\n"
    md += f"- **{get_ui('m_rec')}:** {funnel.get('funnel_recommendation', 'N/A')}\n"
    md += f"- **{get_ui('ats_matched')}** {', '.join(funnel.get('matched_keywords', []))}\n"
    md += f"- **{get_ui('ats_missing')}** {', '.join(funnel.get('missing_keywords', []))}\n\n"
    
    md += f"## {get_ui('sec2_title')}\n"
    for item in data.get('competency_breakdown', []):
        md += f"### {item.get('dimension', 'N/A')} - Score: {item.get('score', 'N/A')}\n"
        md += f"> {item.get('justification', '')} *(Evidence: {item.get('evidence', '')})*\n\n"
        
    md += f"## {get_ui('sec3_title')}\n"
    md += f"- **{get_ui('dei_check')}** {dei.get('dei_safeguard_applied', 'N/A')}\n"
    md += f"- **{get_ui('hard_risks')}** {', '.join(dei.get('hard_risks', []))}\n"
    md += f"- **{get_ui('soft_risks')}** {', '.join(dei.get('soft_risks', []))}\n\n"
    return md

# ==========================================
# 5. Main UI Layout
# ==========================================
st.title(get_ui("title"))
st.caption(get_ui("subtitle"))

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader(get_ui("col1_title"))
    jd_input_type = st.radio(get_ui("input_mode_lbl"), get_ui("input_modes"), horizontal=True, key="jd_mode")
    if jd_input_type in ["貼上文字", "Paste Text"]:
        jd_text = st.text_area("JD 內容", height=200, placeholder=get_ui("jd_ph"), label_visibility="collapsed")
    else:
        jd_files = st.file_uploader(get_ui("upload_jd_lbl"), type=["pdf", "docx", "doc"], accept_multiple_files=True, key="jd_uploader")
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(get_ui("col2_title"))
    cv_files = st.file_uploader(get_ui("upload_cv_lbl"), type=["pdf", "docx", "doc"], accept_multiple_files=True, key="cv_uploader")

with col3:
    st.subheader(get_ui("col3_title"))
    is_referral = st.checkbox(get_ui("referral_lbl"), value=False)
    urgency_val = st.selectbox(get_ui("urgency_lbl"), get_ui("urgency_opts"))
    special_reqs = st.text_area(get_ui("special_req_lbl"), height=90, placeholder=get_ui("special_req_ph"))

st.markdown("---")

# ==========================================
# 6. Execution Engine (Tabbed Processing)
# ==========================================
def process_single_candidate(cand_name, cv_content, hr_feedback=""):
    MAX_CHARS = 40000 
    curr_jd, curr_cv = jd_text[:MAX_CHARS//2], cv_content[:MAX_CHARS//2]
    
    with st.status(get_ui("status_analyzing").format(format_tab_name(cand_name)), expanded=True) as status:
        try:
            prompt = build_evaluation_prompt(is_zh, is_referral, urgency_val, special_reqs, curr_jd, curr_cv, hr_feedback)
            raw_response = run_ai_analysis(provider, api_key, prompt)
            parsed_data = robust_json_parse(raw_response)
            status.update(label=f"✅ {format_tab_name(cand_name)} 分析完成", state="complete", expanded=False)
            return parsed_data
        except Exception as e:
            status.update(label=f"❌ {format_tab_name(cand_name)} 分析失敗", state="error")
            st.error(f"**除錯訊息:**\n`{str(e)}`")
            print(f"[DEBUG - {cand_name}] {traceback.format_exc()}")
            return None

# Initial Batch Run
if st.button(get_ui("run_btn"), type="primary", use_container_width=True):
    if not api_key or not jd_text.strip() or not cv_files:
        st.warning("⚠️ 請確認已輸入 API Key、JD 並上傳至少一份 CV。")
    elif key_mode == get_ui("default_key") and len(cv_files) > 1:
        # 💡 核心優化：免費模式下若上傳多於 1 份 CV，彈出明確提示
        st.warning(get_ui("single_cv_notice"))
    else:
        check_quota()
        st.session_state.analysis_results = {}
        st.session_state.hr_feedback_history = {}
        
        # 免費模式強制唯一下標 0，BYOK 模式支援完整迴圈
        files_to_process = [cv_files[0]] if key_mode == get_ui("default_key") else cv_files
        
        for idx, cv_file in enumerate(files_to_process):
            if idx > 0:
                time.sleep(3.0) 
                
            cand_name = cv_file.name
            cv_content = extract_single_file(cv_file)
            result = process_single_candidate(cand_name, cv_content)
            if result:
                st.session_state.analysis_results[cand_name] = result
                st.session_state.hr_feedback_history[cand_name] = []

# ==========================================
# 7. Render Multi-CV Tabs & Results
# ==========================================
if st.session_state.analysis_results:
    cand_names = list(st.session_state.analysis_results.keys())
    tabs = st.tabs([f"👤 {format_tab_name(name)}" for name in cand_names])
    
    for i, cand_name in enumerate(cand_names):
        with tabs[i]:
            data = st.session_state.analysis_results[cand_name]
            funnel = data.get('funnel_and_ats', {})
            dei = data.get('dei_and_risks', {})
            
            # Sec 1: Funnel
            st.markdown(f"### {get_ui('sec1_title')}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(get_ui("m_score"), f"{funnel.get('competency_overall_score', 'N/A')} / 100")
            c2.metric(get_ui("m_ats"), f"{funnel.get('ats_match_percentage', 'N/A')} %")
            c3.metric(get_ui("m_rec"), funnel.get('funnel_recommendation', 'N/A'))
            c4.metric(get_ui("m_time"), funnel.get('time_to_fill_assessment', 'N/A'))
            
            st.success(f"**{get_ui('ats_matched')}** " + ", ".join(funnel.get('matched_keywords', [])))
            st.error(f"**{get_ui('ats_missing')}** " + ", ".join(funnel.get('missing_keywords', [])))
            
            # Sec 2: Competency
            st.markdown("---")
            st.markdown(f"### {get_ui('sec2_title')}")
            comp_data = data.get('competency_breakdown', [])
            if comp_data:
                sb_cols = st.columns(min(len(comp_data), 3))
                for idx, item in enumerate(comp_data):
                    with sb_cols[idx % 3]:
                        st.markdown(f"**{item.get('dimension', 'N/A')}**")
                        st.markdown(f"#### {item.get('score', 'N/A')}")
                        st.caption(f"{item.get('justification', '')}")
            
            # Sec 3: DEI
            st.markdown("---")
            st.markdown(f"### {get_ui('sec3_title')}")
            st.info(f"**{get_ui('dei_check')}**\n{dei.get('dei_safeguard_applied', 'N/A')}")
            r1, r2 = st.columns(2)
            with r1:
                st.error(f"**{get_ui('hard_risks')}**\n" + "\n".join([f"- {x}" for x in dei.get('hard_risks', ["None"])]))
            with r2:
                st.warning(f"**{get_ui('soft_risks')}**\n" + "\n".join([f"- {x}" for x in dei.get('soft_risks', ["None"])]))
            
            # Sec 4: Rubric
            st.markdown("---")
            with st.expander(get_ui('sec4_title')):
                st.caption(get_ui("sec4_sub"))
                for q in data.get('structured_interview_rubric', []):
                    st.markdown(f"**{get_ui('probe_q')}** {q.get('star_question', '')}")
                    st.success(f"**{get_ui('rubric_5')}** {q.get('rubric_5_excellent', '')}")
                    st.error(f"**{get_ui('rubric_1')}** {q.get('rubric_1_poor', '')}")
                    st.markdown("---")

            # Sec 5: HITL Feedback & Export
            st.markdown("---")
            st.markdown(f"### {get_ui('sec5_title')}")
            for past_fb in st.session_state.hr_feedback_history.get(cand_name, []):
                st.info(f"👤 **HR Notes:** {past_fb}")
            
            fb_key = f"fb_{cand_name}"
            new_fb = st.text_area("HR Notes", placeholder=get_ui("feedback_ph"), key=fb_key, label_visibility="collapsed")
            
            col_eval, col_dl = st.columns([1, 1])
            with col_eval:
                if st.button(get_ui("re_eval_btn"), key=f"btn_{cand_name}", use_container_width=True):
                    if new_fb.strip():
                        check_quota()
                        
                        target_cv_text = ""
                        for f in cv_files:
                            if f.name == cand_name:
                                target_cv_text = extract_single_file(f)
                                break
                        
                        full_fb = "\n".join(st.session_state.hr_feedback_history.get(cand_name, []) + [new_fb])
                        updated_data = process_single_candidate(cand_name, target_cv_text, hr_feedback=full_fb)
                        if updated_data:
                            st.session_state.hr_feedback_history[cand_name].append(new_fb)
                            st.session_state.analysis_results[cand_name] = updated_data
                            st.rerun()
            
            with col_dl:
                md_report = generate_markdown_report(cand_name, data)
                st.download_button(
                    label=get_ui("download_btn"),
                    data=md_report,
                    file_name=f"TalentScout_Report_{format_tab_name(cand_name)}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_{cand_name}"
                )
