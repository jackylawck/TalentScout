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

# 💡 匯入動態計分引擎
from utils import get_scored_industries, build_dynamic_industry_context

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
# 2. Localization Dictionaries (雙語完全支援)
# ==========================================
UI_ZH = {
    "sys_config": "⚙️ 系統設定",
    "key_mode": "選擇 AI 金鑰模式：",
    "default_key": "使用開源公共免費額度 (單次 1 份 CV)",
    "byok_key": "使用自備 AI API Key (支援多 CV 批量)",
    "loaded_default": "🌱 **開源公共資源已載入 (10次/Session)**。免費模式下**每次限上傳 1 份 CV**。",
    "quota_exceeded": "🤝 **本 Session 試用額度已達上限。** 請切換至『使用自備 AI API Key』！",
    "single_cv_notice": "💡 **免費試用提示：** 開源免費額度每次限解析 **1 份 CV**。如需批量解析，請切換自備 Key。",
    "select_provider": "選擇 AI 供應商：",
    "enter_key": "輸入你的 {} Key",
    "framework_title": "🛡️ 數據安全與中西 HR 理論管治",
    "framework_body": """
    **🔐 企業隱私防護:** 運算僅存於本地 Session 記憶體。
    **🎯 動態知識注入 (RAG):** 基於 Log-TF 權重過濾 Top-N 產業生態。
    **🧠 冰山模型與 MECE 審計:** 消除邏輯矛盾，精算年資。
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)",
    "subtitle": "🚀 **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**",
    "col1_title": "📄 1. 職位描述 (JD)",
    "input_modes": ["貼上文字", "上傳文件"],
    "jd_ph": "請貼上 JD 內容...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX)",
    "col2_title": "👤 2. 求職者履歷 (CV)",
    "upload_cv_lbl": "上傳 CV 檔案",
    "col3_title": "🎯 3. 招聘情境與設定",
    "referral_lbl": "🎖️ 此批次包含內部員工推薦",
    "urgency_lbl": "⏳ 職位招聘急迫性",
    "urgency_opts": ["標準 (Standard)", "緊急 (Urgent)"],
    "special_req_lbl": "其他特殊要求 (JD 補充)",
    "run_btn": "🚀 啟動多維度 ATS 解析與結構化評估",
    "status_analyzing": "🚀 正在獨立解析候選人：{}",
    "err_json": "❌ AI 回傳格式解析失敗。請嘗試重新執行。",
    "err_api": "❌ API 呼叫失敗。請檢查 API Key 或網路連線。",
    "sec1_title": "📊 1. 漏斗決策與 ATS 匹配度",
    "m_score": "綜合勝任力得分",
    "m_ats": "ATS 關鍵字匹配率",
    "m_rec": "💡 高階主管決策建議 (Executive Summary)",
    "m_time": "⏳ 到職時效與離職風險評估",
    "ats_matched": "✅ 命中關鍵字:",
    "ats_missing": "❌ 缺失關鍵字:",
    "sec2_title": "📈 2. 核心勝任力維度拆解 (冰山模型)",
    "sec3_title": "🛡️ 3. DEI 防偏誤審查與風險管治",
    "dei_check": "⚖️ DEI 潛在偏見詞彙與防偏誤措施:",
    "hard_risks": "🚨 絕對風險/合規死線:",
    "soft_risks": "⚠️ 軟性風險/面試觀察點:",
    "sec4_title": "🎯 4. 結構化面試量表 (STAR & BARS 法則)",
    "sec4_sub": "💡 *基於勝任力模型生成之標準化評分題庫，確保面試官評分一致性。*",
    "probe_q": "🗣️ 面試題 (STAR):",
    "rubric_5": "🟢 5分 (優秀 - BARS):",
    "rubric_3": "🟡 3分 (合格 - BARS):",
    "rubric_1": "🔴 1分 (需關注 - BARS):",
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
    "loaded_default": "🌱 **Public Quota Loaded (10 uses/session).** Free mode max 1 CV per run.",
    "quota_exceeded": "🤝 **Quota Reached!** Switch to 'Custom Key' to continue.",
    "single_cv_notice": "💡 **Free Quota Notice:** Max 1 CV per run. Use Custom Key for batch processing.",
    "select_provider": "Select AI Provider:",
    "enter_key": "Enter your {} Key",
    "framework_title": "🛡️ Privacy & HR Science Governance",
    "framework_body": """
    **🔐 Enterprise Privacy:** Processed strictly in-memory.
    **🎯 Dynamic RAG Injection:** Top-N industry filtering via Log-TF scoring.
    **🧠 Iceberg & MECE:** Resolves contradictions & ensures accurate tenure math.
    """,
    "title": "🎯 TalentScout AI",
    "subtitle": "🚀 **Enterprise ATS Screening & Competency Assessment**",
    "col1_title": "📄 1. Job Description (JD)",
    "input_modes": ["Paste Text", "Upload Files"],
    "jd_ph": "Paste JD content...",
    "upload_jd_lbl": "Upload JD (PDF, DOCX)",
    "col2_title": "👤 2. Candidate Resumes (CV)",
    "upload_cv_lbl": "Upload CV Files",
    "col3_title": "🎯 3. Hiring Context",
    "referral_lbl": "🎖️ Internal Referral",
    "urgency_lbl": "⏳ Urgency",
    "urgency_opts": ["Standard", "Urgent"],
    "special_req_lbl": "Special Requirements (JD Add-on)",
    "run_btn": "🚀 Run ATS & Competency Audit",
    "status_analyzing": "🚀 Analyzing candidate: {}",
    "err_json": "❌ JSON Parse Error.",
    "err_api": "❌ API Connection Error.",
    "sec1_title": "📊 1. Funnel Verdict & ATS Match",
    "m_score": "Competency Score",
    "m_ats": "ATS Keyword Match",
    "m_rec": "💡 Executive Summary",
    "m_time": "⏳ Time-to-Fill & Risk Assessment",
    "ats_matched": "✅ Matched Keywords:",
    "ats_missing": "❌ Missing Keywords:",
    "sec2_title": "📈 2. Core Competency Breakdown",
    "sec3_title": "🛡️ 3. DEI Safeguards & Risk Governance",
    "dei_check": "⚖️ DEI Bias Mitigation:",
    "hard_risks": "🚨 Hard Risks / Blocks:",
    "soft_risks": "⚠️ Soft Risks / Focus:",
    "sec4_title": "🎯 4. Structured Interview Rubric",
    "sec4_sub": "💡 *Standardized scoring rubrics based on competency.*",
    "probe_q": "🗣️ Behavioral Question (STAR):",
    "rubric_5": "🟢 5 pts (Excellent):",
    "rubric_3": "🟡 3 pts (Acceptable):",
    "rubric_1": "🔴 1 pt (Poor):",
    "sec5_title": "🤝 5. Human-in-the-Loop Re-eval",
    "feedback_ph": "Enter HR screening notes...",
    "re_eval_btn": "🔄 Update Evaluation",
    "download_btn": "📥 Download Report (MD)"
}

with st.sidebar:
    output_lang = st.selectbox("🌐 界面與報告語言 (UI & Output Language):", ["繁體中文 (Traditional Chinese)", "English (Full)"], index=0)
    # 🧪 新增除錯模式 Toggle
    debug_mode = st.toggle("🧪 啟動 AI 決策除錯模式 (Explainability Log)", value=False)
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"
def get_ui(key, default=""): return (UI_ZH if is_zh else UI_EN).get(key, default)

# ==========================================
# 3. Sidebar Config
# ==========================================
AI_PROVIDERS = {
    "GitHub Models": {"url": "https://models.inference.ai.azure.com", "model": "gpt-4o-mini"},
    "OpenAI": {"url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "DeepSeek": {"url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "Google Gemini": {"url": "N/A", "model": "gemini-2.5-flash"}
}

with st.sidebar:
    st.header(get_ui("sys_config"))
    if token_github or token_gemini:
        key_mode = st.radio(get_ui("key_mode"), [get_ui("default_key"), get_ui("byok_key")], index=0)
    else:
        key_mode = get_ui("byok_key")

    if key_mode == get_ui("default_key"):
        provider = "GitHub Models" if token_github else "Google Gemini"
        api_key = token_github or token_gemini
        st.info(get_ui("loaded_default") + f"\n\n*(Engine: **{provider}**)*")
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
# 4. Core Functions
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
    except: pass
    return text.strip()

def extract_text_from_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    return "\n".join([extract_single_file(f) for f in uploaded_files])

def format_tab_name(filename):
    # 僅移除副檔名
    base = re.sub(r'(?i)\.(pdf|docx|doc)$', '', filename)
    # 移除常見的履歷後綴，保留姓名前綴
    clean = re.sub(r'(?i)[-_\s]*(resume|cv|profile|履歷).*', '', base).strip()
    if not clean:
        return "Candidate"
    # 若名稱過長強制縮略
    if len(clean) > 20:
        return clean[:15] + "..."
    return clean

def robust_json_parse(raw_text):
    try:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
        if match: return json.loads(match.group(1).strip())
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match: return json.loads(match.group(0).strip())
        return json.loads(raw_text.strip())
    except Exception as e:
        raise ValueError("JSON Parsing Failed")

def build_evaluation_prompt(lang, is_ref, urgency, special, jd, cv, dynamic_industry_injection, feedback=""):
    lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文)..." if lang else "Provide the ENTIRE analysis strictly in Professional Executive English..."
    ref_inst = "This candidate is an INTERNAL REFERRAL. Apply referral weighting." if is_ref else ""
    fb_prompt = f"\n\n### HR Human-in-the-Loop Feedback:\n{feedback}" if feedback.strip() else ""
    
    return f"""
You are an Elite Executive Search Consultant applying Global HR Science Frameworks.

CRITICAL HR ADVISORY RULES:
1. DYNAMIC INDUSTRY MAPPING (RAG INJECTION):
{dynamic_industry_injection}

2. FULL-TEXT SCAN (EDUCATION & CERTIFICATIONS):
   - Scan the ENTIRE CV including Education, Licenses, and Training. Acknowledge academic/certified fit!

3. TENURE & REASON FOR LEAVING AUDIT (MECE Calculation):
   - Accurately calculate total years of experience across ALL employment history.

4. HIGH-DENSITY EXECUTIVE SUMMARY & BARS RUBRICS:
   - "funnel_recommendation" MUST be a comprehensive Board-level Executive Summary.
   - STAR questions and BARS rubrics (1-3-5) MUST explicitly reference REAL ACCOMPLISHMENTS found in the CV.

Language Requirement: {lang_instruction}
Context: {ref_inst} {urgency} {special} {fb_prompt}

Format your output STRICTLY in valid JSON matching this schema:
{{
  "funnel_and_ats": {{
    "competency_overall_score": 85,
    "ats_match_percentage": 75,
    "matched_keywords": ["..."],
    "missing_keywords": ["..."],
    "funnel_recommendation": "Board-Level Summary...",
    "time_to_fill_assessment": "Availability and retention risk assessment..."
  }},
  "competency_breakdown": [
    {{ "dimension": "Surface Competencies", "score": "85/100", "justification": "...", "evidence": "..." }},
    {{ "dimension": "Core Leadership", "score": "90/100", "justification": "...", "evidence": "..." }}
  ],
  "dei_and_risks": {{
    "dei_safeguard_applied": "...",
    "hard_risks": ["..."],
    "soft_risks": ["..."]
  }},
  "structured_interview_rubric": [
    {{
      "competency_tested": "...",
      "star_question": "...",
      "rubric_5_excellent": "...",
      "rubric_3_acceptable": "...",
      "rubric_1_poor": "..."
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
                    model=cfg["model"], contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
                )
                return response.text
            else:
                client = OpenAI(base_url=cfg["url"], api_key=api_key)
                response = client.chat.completions.create(
                    model=cfg["model"], messages=[{"role": "system", "content": "You are a Board-Level HR Advisor."}, {"role": "user", "content": prompt}],
                    temperature=0.1, response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1: time.sleep(3)
            else: raise e

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
    jd_input_type = st.radio("輸入方式", get_ui("input_modes"), horizontal=True, label_visibility="collapsed")
    if jd_input_type in ["貼上文字", "Paste Text"]:
        jd_text = st.text_area("JD 內容", height=200, placeholder=get_ui("jd_ph"), label_visibility="collapsed")
    else:
        jd_files = st.file_uploader(get_ui("upload_jd_lbl"), type=["pdf", "docx"], accept_multiple_files=True)
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(get_ui("col2_title"))
    cv_files = st.file_uploader(get_ui("upload_cv_lbl"), type=["pdf", "docx"], accept_multiple_files=True)

with col3:
    st.subheader(get_ui("col3_title"))
    is_referral = st.checkbox(get_ui("referral_lbl"), value=False)
    urgency_val = st.selectbox(get_ui("urgency_lbl"), get_ui("urgency_opts"))
    special_reqs = st.text_area(get_ui("special_req_lbl"), height=90)

st.markdown("---")

# ==========================================
# 6. Execution Engine
# ==========================================
def process_single_candidate(cand_name, cv_content, hr_feedback=""):
    MAX_CHARS = 40000 
    curr_jd, curr_cv = jd_text[:MAX_CHARS//2], cv_content[:MAX_CHARS//2]
    
    with st.status(get_ui("status_analyzing").format(format_tab_name(cand_name)), expanded=True) as status:
        try:
            # 💡 獨立匹配：為每位候選人單獨計算結合 JD 與 CV 的產業關聯分數
            combined_text = curr_jd + "\n" + curr_cv
            scored_industries = get_scored_industries(combined_text)
            dynamic_injection = build_dynamic_industry_context(scored_industries)
            
            prompt = build_evaluation_prompt(is_zh, is_referral, urgency_val, special_reqs, curr_jd, curr_cv, dynamic_injection, hr_feedback)
            raw_response = run_ai_analysis(provider, api_key, prompt)
            parsed_data = robust_json_parse(raw_response)
            
            # 存入 data 供 Explainability UI 使用
            parsed_data["_debug_industries"] = scored_industries
            
            status.update(label=f"✅ {format_tab_name(cand_name)} 分析完成", state="complete", expanded=False)
            return parsed_data
        except Exception as e:
            status.update(label=f"❌ {format_tab_name(cand_name)} 分析失敗", state="error")
            print(f"[DEBUG - {cand_name}] {traceback.format_exc()}")
            raise e # 拋出異常供外部迴圈捕捉

if st.button(get_ui("run_btn"), type="primary", use_container_width=True):
    if not api_key or not jd_text.strip() or not cv_files:
        st.warning("⚠️ 請確認已輸入 API Key、JD 並上傳至少一份 CV。")
    elif key_mode == get_ui("default_key") and len(cv_files) > 1:
        st.warning(get_ui("single_cv_notice"))
    else:
        check_quota()
        st.session_state.analysis_results = {}
        st.session_state.hr_feedback_history = {}
        st.session_state.failed_cvs = [] # 追蹤失敗名單
        
        files_to_process = [cv_files[0]] if key_mode == get_ui("default_key") else cv_files
        
        for idx, cv_file in enumerate(files_to_process):
            if idx > 0: time.sleep(3.0) 
            cand_name = cv_file.name
            try:
                cv_content = extract_single_file(cv_file)
                if not cv_content.strip():
                    raise ValueError("文件無法提取文字(可能為純圖片或加密)")
                
                result = process_single_candidate(cand_name, cv_content)
                if result:
                    st.session_state.analysis_results[cand_name] = result
                    st.session_state.hr_feedback_history[cand_name] = []
            except Exception as e:
                st.session_state.failed_cvs.append(f"{cand_name} ({str(e)})")
                
        # 統一報錯展示
        if st.session_state.failed_cvs:
            st.error(f"⚠️ 以下候選人解析失敗：\n" + "\n".join([f"- {f}" for f in st.session_state.failed_cvs]))

# ==========================================
# 7. Render Multi-CV Tabs & Debug UI
# ==========================================
if st.session_state.analysis_results:
    cand_names = list(st.session_state.analysis_results.keys())
    tabs = st.tabs([f"👤 {format_tab_name(name)}" for name in cand_names])
    
    for i, cand_name in enumerate(cand_names):
        with tabs[i]:
            data = st.session_state.analysis_results[cand_name]
            
            # 🧪 顯示 ISO 42001 可解釋性除錯日誌
            if debug_mode and "_debug_industries" in data:
                with st.expander("🛡️ ISO 42001 可解釋性除錯日誌 (Explainability Debug Log)", expanded=True):
                    st.caption("展示 AI 如何使用 Log-TF 權重動態對齊產業板塊 (Top 2 Scoring):")
                    for ind in data["_debug_industries"]:
                        st.markdown(f"**{ind['industry']}** (Score: `{ind['score']}`)")
                        st.caption(f"命中關鍵字: `{', '.join(ind['matched_terms'])}`")
            
            funnel = data.get('funnel_and_ats', {})
            dei = data.get('dei_and_risks', {})
            
            st.markdown(f"### {get_ui('sec1_title')}")
            c1, c2 = st.columns(2)
            c1.metric(get_ui("m_score"), f"{funnel.get('competency_overall_score', 'N/A')} / 100")
            c2.metric(get_ui("m_ats"), f"{funnel.get('ats_match_percentage', 'N/A')} %")
            st.info(f"**{get_ui('m_rec')}**\n\n{funnel.get('funnel_recommendation', 'N/A')}")
            st.warning(f"**{get_ui('m_time')}**\n\n{funnel.get('time_to_fill_assessment', 'N/A')}")
            st.success(f"**{get_ui('ats_matched')}** " + ", ".join(funnel.get('matched_keywords', [])))
            st.error(f"**{get_ui('ats_missing')}** " + ", ".join(funnel.get('missing_keywords', [])))
            
            st.markdown("---")
            st.markdown(f"### {get_ui('sec2_title')}")
            comp_data = data.get('competency_breakdown', [])
            if comp_data:
                sb_cols = st.columns(min(len(comp_data), 2))
                for idx, item in enumerate(comp_data):
                    with sb_cols[idx % 2]:
                        st.markdown(f"**{item.get('dimension', 'N/A')}**")
                        st.markdown(f"#### {item.get('score', 'N/A')}")
                        st.caption(f"{item.get('justification', '')}")
            
            st.markdown("---")
            st.markdown(f"### {get_ui('sec3_title')}")
            st.info(f"**{get_ui('dei_check')}**\n{dei.get('dei_safeguard_applied', 'N/A')}")
            r1, r2 = st.columns(2)
            with r1: st.error(f"**{get_ui('hard_risks')}**\n" + "\n".join([f"- {x}" for x in dei.get('hard_risks', ["None"])]))
            with r2: st.warning(f"**{get_ui('soft_risks')}**\n" + "\n".join([f"- {x}" for x in dei.get('soft_risks', ["None"])]))
            
            st.markdown("---")
            with st.expander(get_ui('sec4_title')):
                st.caption(get_ui("sec4_sub"))
                for q in data.get('structured_interview_rubric', []):
                    st.markdown(f"**{get_ui('probe_q')}** {q.get('star_question', '')}")
                    st.success(f"**{get_ui('rubric_5')}** {q.get('rubric_5_excellent', '')}")
                    st.warning(f"**{get_ui('rubric_3')}** {q.get('rubric_3_acceptable', '')}")
                    st.error(f"**{get_ui('rubric_1')}** {q.get('rubric_1_poor', '')}")
                    st.markdown("---")

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
                    file_name=f"TalentScout_{format_tab_name(cand_name)}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_{cand_name}"
                )
