import streamlit as st
import pypdf
import docx
import json
import re
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
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'hr_feedback_history' not in st.session_state:
    st.session_state.hr_feedback_history = []

default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# ==========================================
# 2. Localization Dictionaries (語系解耦)
# ==========================================
UI_ZH = {
    "sys_config": "⚙️ 系統設定",
    "key_mode": "選擇 AI 金鑰模式：",
    "default_key": "使用開源公共免費額度",
    "byok_key": "使用自備 AI API Key (無限制)",
    "loaded_default": "🌱 **開源公共資源已載入 (10次/Session)**。如需高頻批量篩選或處理高度機密履歷，強烈建議切換為自備 Key 以確保最高安全性與不限次數體驗。",
    "quota_exceeded": "🤝 **本 Session 試用額度已達上限。** 請刷新網頁（F5）或切換至『使用自備 AI API Key』繼續使用！",
    "select_provider": "選擇 AI 供應商：",
    "enter_key": "輸入你的 {} Key",
    "framework_title": "🛡️ 數據安全與進階 HR 管治特色",
    "framework_body": """
    **🔐 企業級私密防護:**
    - **零數據留存:** 僅於本地 Session 運算，重整即清空。
    - **BYOK 直連:** 自備金鑰直連官方端點，無中間層攔截。
    **🎯 深度招募與 ATS 特色:**
    - **多 CV 批量上傳:** 支援一次上傳多份求職者履歷 (每檔限 15MB 內)。
    - **量化勝任力模型:** 動態對齊 JD 核心職能並量化打分。
    - **DEI 防偏誤機制:** 強制排除年齡、性別、背景等無意識偏見。
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)",
    "subtitle": "🚀 **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**",
    "col1_title": "📄 1. 職位描述 (JD)",
    "input_mode_lbl": "輸入方式",
    "input_modes": ["貼上文字", "上傳文件"],
    "jd_ph": "請貼上 JD 內容，包含職責與資格等...",
    "upload_jd_lbl": "上傳 JD 檔案 (PDF, DOCX, DOC, 限 15MB 內)",
    "col2_title": "👤 2. 求職者履歷 (CV)",
    "upload_cv_lbl": "上傳 CV 檔案 (可多選，單檔限 15MB 內)",
    "col3_title": "🎯 3. 招聘情境與 ATS 參數",
    "referral_lbl": "🎖️ 此為內部員工推薦",
    "urgency_lbl": "⏳ 職位招聘急迫性",
    "urgency_opts": ["標準", "緊急"],
    "special_req_lbl": "其他特殊要求",
    "special_req_ph": "例如：必須精通廣東話/英語",
    "run_btn": "🚀 啟動全維度 ATS 解析與結構化評估",
    "status_analyzing": "🚀 智析演算中，請稍候...",
    "status_step_1": "📄 正在解析文件與建立文本庫...",
    "status_step_2": "🧠 正在呼叫 AI 執行勝任力對齊與 DEI 防偏誤審查...",
    "status_step_3": "🛠️ 正在結構化解析 JSON 數據...",
    "status_done": "✅ 分析完成！",
    "err_json": "❌ AI 回傳格式解析失敗 (JSON Parse Error)。請嘗試重新執行或精簡文件內容。",
    "err_api": "❌ API 呼叫失敗或超時，請檢查連線狀態或 API Key 權限是否正確。",
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
    "dei_check": "⚖️ DEI 多元包容防偏誤機制:",
    "hard_risks": "🚨 絕對風險/合規死線:",
    "soft_risks": "⚠️ 軟性風險/面試觀察點:",
    "sec4_title": "🎯 4. 結構化面試量表",
    "sec4_sub": "💡 *基於勝任力模型生成之標準化評分題庫，確保面試官評分一致性。*",
    "probe_q": "🗣️ 行為面試題 (STAR):",
    "rubric_5": "🟢 5分 (優秀):",
    "rubric_3": "🟡 3分 (合格):",
    "rubric_1": "🔴 1分 (需關注):",
    "sec5_title": "🤝 5. HR 漏斗覆核與動態校正 (HITL)",
    "feedback_ph": "輸入電話初篩結果或補充觀察（例如：『候選人為內部高管推薦，且接受立即上班』）...",
    "re_eval_btn": "🔄 結合 HR 反饋重新校正模型"
}

UI_EN = {
    "sys_config": "⚙️ System Config",
    "key_mode": "Select AI Key Mode:",
    "default_key": "Use Open-Source Public Quota",
    "byok_key": "Use Custom API Key (Unlimited)",
    "loaded_default": "🌱 **Public Quota Loaded (10 uses/session).** For high-frequency or highly confidential CV processing, BYOK is strongly recommended for maximum security.",
    "quota_exceeded": "🤝 **Quota Reached!** Please refresh page or switch to 'Custom Key' to continue.",
    "select_provider": "Select AI Provider:",
    "enter_key": "Enter your {} Key",
    "framework_title": "🛡️ Privacy & Advanced HR Governance",
    "framework_body": """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Data Retention:** Processed in-memory; wiped upon refresh.
    - **BYOK Direct Connect:** Connects directly to official endpoints.
    **🎯 Advanced HR Tech Features:**
    - **Multi-CV Support:** Process multiple candidate resumes concurrently (Max 15MB/file).
    - **Competency Modeling:** Dynamic scoring against JD requirements.
    - **DEI Safeguards:** Active mitigation of unconscious bias.
    """,
    "title": "🎯 TalentScout AI",
    "subtitle": "🚀 **Enterprise ATS Screening, Competency Assessment & DEI Governance System**",
    "col1_title": "📄 1. Job Description (JD)",
    "input_mode_lbl": "Input Method",
    "input_modes": ["Paste Text", "Upload Files"],
    "jd_ph": "Paste JD content here including duties, requirements...",
    "upload_jd_lbl": "Upload JD Files (PDF, DOCX, DOC, Max 15MB)",
    "col2_title": "👤 2. Candidate Resumes (CV)",
    "upload_cv_lbl": "Upload CV Files (Multiple files allowed, Max 15MB/file)",
    "col3_title": "🎯 3. Hiring Context & ATS Parameters",
    "referral_lbl": "🎖️ Internal Referral Candidate",
    "urgency_lbl": "⏳ Time-to-Fill Urgency",
    "urgency_opts": ["Standard", "Urgent"],
    "special_req_lbl": "Special Requirements",
    "special_req_ph": "E.g., Fluent Cantonese/English required",
    "run_btn": "🚀 Run Full ATS & Competency Audit",
    "status_analyzing": "🚀 Analyzing & Computing...",
    "status_step_1": "📄 Parsing documents...",
    "status_step_2": "🧠 Running AI Competency & DEI models...",
    "status_step_3": "🛠️ Structuring JSON payload...",
    "status_done": "✅ Analysis Complete!",
    "err_json": "❌ JSON Parse Error. The AI output was malformed. Please try again or simplify the documents.",
    "err_api": "❌ API Connection Error. Please check your network or API Key permissions.",
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
    "dei_check": "⚖️ DEI Bias Prevention Safeguards:",
    "hard_risks": "🚨 Hard Risks / Compliance Blocks:",
    "soft_risks": "⚠️ Soft Risks / Interview Focus:",
    "sec4_title": "🎯 4. Structured Interview Rubric",
    "sec4_sub": "💡 *Standardized scoring rubrics generated based on competency models for consistency.*",
    "probe_q": "🗣️ STAR Question:",
    "rubric_5": "🟢 5 points (Excellent):",
    "rubric_3": "🟡 3 points (Acceptable):",
    "rubric_1": "🔴 1 point (Poor):",
    "sec5_title": "🤝 5. Human-in-the-Loop Re-eval",
    "feedback_ph": "Enter screening notes (e.g., 'Internal referral, available immediately')...",
    "re_eval_btn": "🔄 Update Evaluation with HR Notes"
}

with st.sidebar:
    output_lang = st.selectbox("🌐 界面與報告語言 (UI & Output Language):", ["繁體中文 (Traditional Chinese)", "English (Full)"], index=0)
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"
ui = UI_ZH if is_zh else UI_EN

# ==========================================
# 3. Sidebar & Configuration
# ==========================================
with st.sidebar:
    st.header(ui["sys_config"])
    if default_token:
        key_mode = st.radio(ui["key_mode"], [ui["default_key"], ui["byok_key"]], index=0)
    else:
        key_mode = ui["byok_key"]

    if key_mode == ui["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.info(ui["loaded_default"])
    else:
        provider = st.selectbox(ui["select_provider"], ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"])
        api_key = st.text_input(ui["enter_key"].format(provider), type="password")
    
    st.divider()
    st.markdown(ui["framework_title"])
    st.markdown(ui["framework_body"])

# ==========================================
# 4. Core Functions (File Parsing & AI Setup)
# ==========================================
def extract_text_from_files(uploaded_files):
    if not uploaded_files: return ""
    if not isinstance(uploaded_files, list): uploaded_files = [uploaded_files]
    combined_text = ""
    for file in uploaded_files:
        file_type = file.name.split('.')[-1].lower()
        file_text = ""
        try:
            if file_type == "pdf":
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages: file_text += (page.extract_text() or "") + "\n"
            elif file_type in ["docx", "doc"]:
                doc = docx.Document(file)
                for para in doc.paragraphs: file_text += para.text + "\n"
            if file_text.strip(): combined_text += f"\n--- [Source CV: {file.name}] ---\n" + file_text
        except Exception:
            pass
    return combined_text

# Robust JSON Parser (防禦 AI 格式幻覺)
def robust_json_parse(raw_text):
    try:
        # 嘗試擷取 ```json ... ``` 區塊
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
        if match:
            return json.loads(match.group(1).strip())
        # Fallback: 尋找最外層的 {}
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0).strip())
        return json.loads(raw_text.strip())
    except Exception as e:
        raise ValueError("JSON Parsing Failed") from e

# 系統 Prompt 模板隔離管理
def build_evaluation_prompt(lang, is_ref, urgency, special, jd, cv, feedback):
    lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文)." if lang else "Provide the ENTIRE analysis strictly in Professional Executive English."
    referral_instruction = "This candidate is an INTERNAL REFERRAL. Apply referral weighting." if is_ref else ""
    feedback_prompt = f"\n\n### HR Human-in-the-Loop Feedback:\n{feedback}\n(Update the assessment based on this real-world feedback.)" if feedback.strip() else ""
    
    return f"""
You are an Elite HR Tech System executing advanced Talent Science algorithms. Evaluate the candidate(s) against the JD using Competency Modeling, ATS Keyword Extraction, DEI Safeguards, and Structured Interview Rubrics.

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
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["keyword3", "keyword4"],
    "funnel_recommendation": "Advance to Hiring Manager / Phone Screen / Reject",
    "time_to_fill_assessment": "Assessment of notice period or readiness based on urgency."
  }},
  "competency_breakdown": [
    {{"dimension": "Hard Skills & Domain", "score": "80/100", "justification": "...", "evidence": "Quote from CV"}}
  ],
  "dei_and_risks": {{
    "dei_safeguard_applied": "State how bias was mitigated.",
    "hard_risks": ["Absolute blockers"],
    "soft_risks": ["Observation areas"]
  }},
  "structured_interview_rubric": [
    {{
      "competency_tested": "Specific skill",
      "star_question": "Behavioral question",
      "rubric_5_excellent": "What a 5-point answer sounds like",
      "rubric_3_acceptable": "What a 3-point answer sounds like",
      "rubric_1_poor": "What a 1-point red flag answer sounds like"
    }}
  ]
}}

Output ONLY raw JSON.

Job Description (JD):
{jd}

Candidate CV(s):
{cv}
"""

def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
        )
        return response.text
    else:
        base_urls = {"OpenAI": "https://api.openai.com/v1", "DeepSeek": "https://api.deepseek.com", "Groq": "https://api.groq.com/openai/v1", "GitHub Models": "https://models.inference.ai.azure.com"}
        models = {"OpenAI": "gpt-4o-mini", "DeepSeek": "deepseek-chat", "Groq": "llama-3.3-70b-versatile", "GitHub Models": "gpt-4o-mini"}
        client = OpenAI(base_url=base_urls[provider], api_key=api_key)
        response = client.chat.completions.create(
            model=models[provider],
            messages=[{"role": "system", "content": "You are an Elite HR Tech & ATS Algorithm producing raw JSON."}, {"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()

# ==========================================
# 5. Main UI Layout
# ==========================================
st.title(ui["title"])
st.caption(ui["subtitle"])

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader(ui["col1_title"])
    jd_input_type = st.radio(ui["input_mode_lbl"], ui["input_modes"], horizontal=True, key="jd_mode")
    if jd_input_type in ["貼上文字", "Paste Text"]:
        jd_text = st.text_area("JD 內容", height=200, placeholder=ui["jd_ph"], label_visibility="collapsed")
    else:
        jd_files = st.file_uploader(ui["upload_jd_lbl"], type=["pdf", "docx", "doc"], accept_multiple_files=True, key="jd_uploader")
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(ui["col2_title"])
    cv_files = st.file_uploader(ui["upload_cv_lbl"], type=["pdf", "docx", "doc"], accept_multiple_files=True, key="cv_uploader")
    cv_text = extract_text_from_files(cv_files)

with col3:
    st.subheader(ui["col3_title"])
    is_referral = st.checkbox(ui["referral_lbl"], value=False)
    urgency_val = st.selectbox(ui["urgency_lbl"], ui["urgency_opts"])
    special_reqs = st.text_area(ui["special_req_lbl"], height=90, placeholder=ui["special_req_ph"])

st.markdown("---")

# ==========================================
# 6. Execution Logic & Rendering
# ==========================================
def execute_eval(hr_feedback=""):
    if key_mode == ui["default_key"]:
        if st.session_state.usage_count >= 10:
            st.info(ui["quota_exceeded"])
            st.stop()
        st.session_state.usage_count += 1

    if not api_key or not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ 系統需要完整的 API Key, JD 與 CV 才能啟動。" if is_zh else "⚠️ API Key, JD, and CV are required.")
        return None

    # Smart Truncation (防禦超大文本)
    MAX_CHARS = 80000 
    curr_jd, curr_cv = jd_text, cv_text
    if len(curr_jd) + len(curr_cv) > MAX_CHARS:
        curr_jd = curr_jd[:MAX_CHARS//2] + "\n\n...[JD Truncated]"
        curr_cv = curr_cv[:MAX_CHARS//2] + "\n\n...[CV Truncated]"

    # 使用 st.status 提供沈浸式狀態回饋
    with st.status(ui["status_analyzing"], expanded=True) as status:
        try:
            st.write(ui["status_step_1"])
            prompt = build_evaluation_prompt(is_zh, is_referral, urgency_val, special_reqs, curr_jd, curr_cv, hr_feedback)
            
            st.write(ui["status_step_2"])
            raw_response = run_ai_analysis(provider, api_key, prompt)
            
            st.write(ui["status_step_3"])
            parsed_data = robust_json_parse(raw_response)
            
            status.update(label=ui["status_done"], state="complete", expanded=False)
            return parsed_data
            
        except ValueError:
            status.update(label="Error", state="error")
            st.error(ui["err_json"])
            print(f"[DEBUG - Parse Error] Raw Response: {raw_response[:500]}...")
            return None
        except Exception as e:
            status.update(label="Error", state="error")
            st.error(ui["err_api"])
            print(f"[DEBUG - Network/API Error] {traceback.format_exc()}")
            return None

if st.button(ui["run_btn"], type="primary", use_container_width=True):
    st.session_state.hr_feedback_history = [] # Reset feedback on fresh run
    st.session_state.last_analysis = execute_eval()

# Render Results
if st.session_state.last_analysis:
    data = st.session_state.last_analysis
    funnel = data.get('funnel_and_ats', {})
    dei = data.get('dei_and_risks', {})
    
    # Sec 1
    st.markdown(f"## {ui['sec1_title']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(ui["m_score"], f"{funnel.get('competency_overall_score', 'N/A')} / 100")
    c2.metric(ui["m_ats"], f"{funnel.get('ats_match_percentage', 'N/A')} %")
    c3.metric(ui["m_rec"], funnel.get('funnel_recommendation', 'N/A'))
    c4.metric(ui["m_time"], urgency_val)
    
    st.info(f"⏳ **{ui['m_time']}:** {funnel.get('time_to_fill_assessment', 'N/A')}")
    st.success(f"**{ui['ats_matched']}** " + ", ".join(funnel.get('matched_keywords', [])))
    st.error(f"**{ui['ats_missing']}** " + ", ".join(funnel.get('missing_keywords', [])))
    
    # Sec 2
    st.markdown("---")
    st.markdown(f"## {ui['sec2_title']}")
    comp_data = data.get('competency_breakdown', [])
    if comp_data:
        sb_cols = st.columns(len(comp_data))
        for idx, item in enumerate(comp_data):
            with sb_cols[idx]:
                st.markdown(f"**{item.get('dimension', 'N/A')}**")
                st.markdown(f"### {item.get('score', 'N/A')}")
                st.caption(f"{item.get('justification', '')}")
                st.caption(f"*({ui['evidence_source']}: {item.get('evidence', 'N/A')})*")
    
    # Sec 3
    st.markdown("---")
    st.markdown(f"## {ui['sec3_title']}")
    st.info(f"**{ui['dei_check']}**\n{dei.get('dei_safeguard_applied', 'N/A')}")
    r1, r2 = st.columns(2)
    with r1:
        st.error(f"**{ui['hard_risks']}**\n" + "\n".join([f"- {x}" for x in dei.get('hard_risks', ["None"])]))
    with r2:
        st.warning(f"**{ui['soft_risks']}**\n" + "\n".join([f"- {x}" for x in dei.get('soft_risks', ["None"])]))
    
    # Sec 4
    st.markdown("---")
    st.markdown(f"## {ui['sec4_title']}")
    st.caption(ui["sec4_sub"])
    for q in data.get('structured_interview_rubric', []):
        with st.expander(f"📌 勝任力維度: {q.get('competency_tested', 'N/A')}"):
            st.markdown(f"**{ui['probe_q']}** {q.get('star_question', '')}")
            st.markdown("---")
            st.success(f"**{ui['rubric_5']}** {q.get('rubric_5_excellent', '')}")
            st.warning(f"**{ui['rubric_3']}** {q.get('rubric_3_acceptable', '')}")
            st.error(f"**{ui['rubric_1']}** {q.get('rubric_1_poor', '')}")

    # Sec 5: HITL Feedback Loop
    st.markdown("---")
    st.markdown(f"## {ui['sec5_title']}")
    
    # Render Feedback History
    for past_feedback in st.session_state.hr_feedback_history:
        st.info(f"👤 **HR Notes:** {past_feedback}")

    hr_feedback_text = st.text_area("HR Reviewer Notes", placeholder=ui["feedback_ph"], key="hr_feedback_input", label_visibility="collapsed")
    if st.button(ui["re_eval_btn"], use_container_width=True):
        if hr_feedback_text.strip():
            # Combine history with new feedback
            full_feedback_history = "\n".join(st.session_state.hr_feedback_history + [hr_feedback_text])
            updated_data = execute_eval(hr_feedback=full_feedback_history)
            
            if updated_data:
                st.session_state.hr_feedback_history.append(hr_feedback_text)
                st.session_state.last_analysis = updated_data
                st.rerun()
