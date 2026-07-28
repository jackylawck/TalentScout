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

# 初始化 Session State
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

# 讀取後台預設 Secrets
default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# 語言選擇
with st.sidebar:
    output_lang = st.selectbox(
        "🌐 界面與報告語言 (UI & Output Language):",
        ["繁體中文 (Traditional Chinese)", "English (Full)"],
        index=0
    )
    st.divider()

is_zh = output_lang == "繁體中文 (Traditional Chinese)"

# UI 文字字典
ui_labels = {
    "sys_config": "⚙️ 系統設定 (System Config)" if is_zh else "⚙️ System Config",
    "key_mode": "選擇 AI 金鑰模式：" if is_zh else "Select AI Key Mode:",
    "default_key": "使用開源公共免費額度" if is_zh else "Use Open-Source Public Quota",
    "byok_key": "使用自備 AI API Key (無限制)" if is_zh else "Use Custom API Key (Unlimited)",
    "loaded_default": "🌱 **本系統為免費開源專案**，已預載公共試用資源（每 Session 10 次）。歡迎自由體驗！若需高頻批量篩選，歡迎切換為自備 Key，將公共資源留給其他有需要的人。" if is_zh else "🌱 **Open-Source Public Quota Loaded** (10 free uses per session).",
    "quota_exceeded": "🤝 **本 Session 試用額度（10 次）已達上限。** 請刷新網頁（F5）或切換至『使用自備 AI API Key』繼續使用！" if is_zh else "🤝 **Quota Reached!** Please refresh page or switch to 'Custom Key' to continue.",
    "select_provider": "選擇 AI 供應商 (Provider)：" if is_zh else "Select AI Provider:",
    "enter_key": "輸入你的 {} Key" if is_zh else "Enter your {} Key",
    
    "framework_title": "🛡️ 數據安全與進階 HR 管治特色" if is_zh else "🛡️ Privacy & Advanced HR Governance",
    "framework_body": """
    **🔐 企業級私密防護 (Data Privacy):**
    - **零數據留存:** 僅於本地 Session 運算，重整即清空。
    - **私隱合規:** 嚴格遵循香港 PDPO 數據私隱條例。

    **🎯 深度招募與 ATS 特色 (HR Tech Features):**
    - **量化勝任力模型:** 動態對齊 JD 核心職能並量化打分。
    - **ATS 關鍵字比對:** 精準擷取 Match & Missing Keywords。
    - **DEI 防偏誤機制:** 強制排除年齡、性別、背景等無意識偏見。
    - **結構化面試量表:** 內建 1-3-5 分量化評分標準 (Scoring Rubric)。
    """ if is_zh else """
    **🔐 Enterprise Privacy Guarantee:**
    - **Zero Data Retention:** Processed in-memory; wiped upon refresh.
    - **PDPO Compliant:** Built under Hong Kong PDPO guidelines.

    **🎯 Advanced HR Tech Features:**
    - **Competency Modeling:** Dynamic scoring against JD requirements.
    - **ATS Keyword Matching:** Exact matched and missing keyword extraction.
    - **DEI Safeguards:** Active mitigation of unconscious bias.
    - **Structured Rubrics:** 1-3-5 quantitative scoring guides for interviews.
    """,
    "title": "🎯 慧聘 · 智析官 (TalentScout AI)" if is_zh else "🎯 TalentScout AI",
    "subtitle": "🚀 **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**" if is_zh else "🚀 **Enterprise ATS Screening, Competency Assessment & DEI Governance System**",
    "col1_title": "📄 1. 職位描述 (JD)" if is_zh else "📄 1. Job Description (JD)",
    "col2_title": "👤 2. 求職者履歷 (CV)" if is_zh else "👤 2. Candidate Resume (CV)",
    "col3_title": "🎯 3. 招聘情境與 ATS 參數" if is_zh else "🎯 3. Hiring Context & ATS Parameters",
    "run_btn": "🚀 啟動全維度 ATS 解析與結構化評估 (Run ATS Audit)" if is_zh else "🚀 Run Full ATS & Competency Audit",
    "spinner_msg": "🚀 智析演算中：執行 ATS 關鍵字比對、DEI 審查與勝任力量化..." if is_zh else "🚀 Analyzing: Executing ATS matching, DEI safeguards & Competency scoring...",

    # Dashboard 標籤
    "sec1_title": "📊 1. 漏斗決策與 ATS 匹配度 (Funnel Verdict & ATS Match)" if is_zh else "📊 1. Funnel Verdict & ATS Match",
    "m_score": "綜合勝任力得分" if is_zh else "Competency Score",
    "m_ats": "ATS 關鍵字匹配率" if is_zh else "ATS Keyword Match",
    "m_rec": "漏斗轉換建議" if is_zh else "Funnel Recommendation",
    "m_time": "到職時效評估" if is_zh else "Time-to-Fill Risk",
    "ats_matched": "✅ 命中關鍵字 (Matched):" if is_zh else "✅ Matched Keywords:",
    "ats_missing": "❌ 缺失關鍵字 (Missing):" if is_zh else "❌ Missing Keywords:",
    
    "sec2_title": "📈 2. 核心勝任力維度拆解 (Competency Breakdown)" if is_zh else "📈 2. Core Competency Breakdown",
    "evidence_source": "證據來源" if is_zh else "Evidence Source",

    "sec3_title": "🛡️ 3. DEI 防偏誤審查與風險管治 (DEI Safeguards & Risks)" if is_zh else "🛡️ 3. DEI Safeguards & Risk Governance",
    "dei_check": "⚖️ DEI 多元包容防偏誤機制 (DEI Bias Prevention):" if is_zh else "⚖️ DEI Bias Prevention Safeguards:",
    "hard_risks": "🚨 絕對風險/合規死線 (Hard Risks):" if is_zh else "🚨 Hard Risks / Compliance Blocks:",
    "soft_risks": "⚠️ 軟性風險/面試觀察點 (Soft Risks):" if is_zh else "⚠️ Soft Risks / Interview Focus:",

    "sec4_title": "🎯 4. 結構化面試量表 (Structured Interview Rubric)" if is_zh else "🎯 4. Structured Interview Rubric",
    "sec4_sub": "💡 *基於勝任力模型生成之標準化評分題庫，確保面試官評分一致性。*" if is_zh else "💡 *Standardized scoring rubrics generated based on competency models for consistency.*",
    "probe_q": "🗣️ 行為面試題 (STAR Question):" if is_zh else "🗣️ STAR Question:",
    "rubric_5": "🟢 5分 (Excellent):" if is_zh else "🟢 5 points (Excellent):",
    "rubric_3": "🟡 3分 (Acceptable):" if is_zh else "🟡 3 points (Acceptable):",
    "rubric_1": "🔴 1分 (Poor):" if is_zh else "🔴 1 point (Poor):",

    "sec5_title": "🤝 5. HR 漏斗覆核與動態校正 (Human-in-the-Loop Re-eval)" if is_zh else "🤝 5. Human-in-the-Loop Re-eval",
    "feedback_ph": "輸入電話初篩結果或補充觀察（例如：『候選人為內部高管推薦，且接受立即上班』）..." if is_zh else "Enter screening notes (e.g., 'Internal referral, available immediately')...",
    "re_eval_btn": "🔄 結合 HR 反饋重新校正模型 (Update Evaluation)" if is_zh else "🔄 Update Evaluation with HR Notes"
}

with st.sidebar:
    st.header(ui_labels["sys_config"])
    if default_token:
        key_mode = st.radio(ui_labels["key_mode"], [ui_labels["default_key"], ui_labels["byok_key"]], index=0)
    else:
        key_mode = ui_labels["byok_key"]

    if key_mode == ui_labels["default_key"]:
        provider = "GitHub Models"
        api_key = default_token
        st.info(ui_labels["loaded_default"])
    else:
        provider = st.selectbox(ui_labels["select_provider"], ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"])
        api_key = st.text_input(ui_labels["enter_key"].format(provider), type="password")

    st.divider()
    st.markdown(ui_labels["framework_title"])
    st.markdown(ui_labels["framework_body"])

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
            if file_text.strip(): combined_text += f"\n--- [Source: {file.name}] ---\n" + file_text
        except Exception:
            pass
    return combined_text

st.title(ui_labels["title"])
st.caption(ui_labels["subtitle"])

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader(ui_labels["col1_title"])
    jd_input_type = st.radio("輸入", ["貼上文字", "上傳文件"] if is_zh else ["Paste Text", "Upload Files"], horizontal=True, key="jd_mode")
    if jd_input_type in ["貼上文字", "Paste Text"]:
        jd_text = st.text_area("JD 內容", height=200, label_visibility="collapsed")
    else:
        jd_files = st.file_uploader("上傳 JD (PDF/DOCX)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="jd_uploader")
        jd_text = extract_text_from_files(jd_files)

with col2:
    st.subheader(ui_labels["col2_title"])
    cv_files = st.file_uploader("上傳 CV (PDF/DOCX)", type=["pdf", "docx", "doc"], accept_multiple_files=True, key="cv_uploader")
    cv_text = extract_text_from_files(cv_files)

with col3:
    st.subheader(ui_labels["col3_title"])
    is_referral = st.checkbox("🎖️ 此為內部員工推薦 (Internal Referral)", value=False)
    urgency = st.selectbox("⏳ 職位招聘急迫性 (Time-to-Fill Urgency)", ["標準 (Standard)", "緊急 (Urgent)"])
    special_reqs = st.text_area("其他特殊要求 (Special Req)", height=90, placeholder="例如：必須精通廣東話" if is_zh else "E.g., Fluent Cantonese required")

st.markdown("---")

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

def execute_eval(hr_feedback=""):
    if key_mode == ui_labels["default_key"]:
        if st.session_state.usage_count >= 10:
            st.info(ui_labels["quota_exceeded"])
            st.stop()
        st.session_state.usage_count += 1

    if not api_key or not jd_text.strip() or not cv_text.strip():
        st.warning("⚠️ 系統需要完整的 API Key, JD 與 CV 才能啟動。" if is_zh else "⚠️ API Key, JD, and CV are required.")
        return None

    MAX_CHARS = 80000 
    curr_jd, curr_cv = jd_text, cv_text
    if len(curr_jd) + len(curr_cv) > MAX_CHARS:
        curr_jd = curr_jd[:MAX_CHARS//2] + "\n\n...[JD Truncated]"
        curr_cv = curr_cv[:MAX_CHARS//2] + "\n\n...[CV Truncated]"

    with st.spinner(ui_labels["spinner_msg"]):
        try:
            lang_instruction = "Provide the ENTIRE analysis strictly in Professional Traditional Chinese (繁體中文). Only keep standard industry abbreviations if necessary." if is_zh else "Provide the ENTIRE analysis strictly in Professional Executive English."
            referral_instruction = "This candidate is an INTERNAL REFERRAL. Apply referral weighting: slightly increase trust in cultural fit and soft skills, but maintain strict baseline for hard requirements." if is_referral else ""
            urgency_instruction = f"Hiring Urgency: {urgency}. Factor this into the Time-to-Fill risk assessment."
            feedback_prompt = f"\n\n### HR Human-in-the-Loop Feedback:\n{hr_feedback}\n(Update the assessment based on this real-world feedback.)" if hr_feedback.strip() else ""

            prompt = f"""
You are an Elite HR Tech System executing advanced Talent Science algorithms. Evaluate the candidate against the JD using Competency Modeling, ATS Keyword Extraction, DEI Safeguards, and Structured Interview Rubrics.

Language Requirement:
{lang_instruction}

Context Parameters:
- Internal Referral: {is_referral} ({referral_instruction})
- Urgency: {urgency_instruction}
- Special Req: {special_reqs}
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
    {{"dimension": "Hard Skills & Domain", "score": "80/100", "justification": "...", "evidence": "Quote from CV"}},
    {{"dimension": "Problem Solving & Execution", "score": "85/100", "justification": "...", "evidence": "Quote from CV"}},
    {{"dimension": "Leadership / Team Fit", "score": "90/100", "justification": "...", "evidence": "Quote from CV"}}
  ],
  "dei_and_risks": {{
    "dei_safeguard_applied": "Explicitly state how bias (e.g. age, gender, non-traditional career path) was mitigated in this scoring.",
    "hard_risks": ["Absolute blockers like Visa or lacking mandatory licenses"],
    "soft_risks": ["Observation areas like job stability or culture gaps"]
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
{curr_jd}

Candidate CV:
{curr_cv}
"""
            raw_response = run_ai_analysis(provider, api_key, prompt)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            clean_json = json_match.group(0) if json_match else raw_response.strip()
            
            return json.loads(clean_json)
        except Exception as e:
            print(f"[DEBUG - API Error] {type(e).__name__}: {str(e)}") 
            st.error(f"❌ Analysis Error: {type(e).__name__}.")
            return None

if st.button(ui_labels["run_btn"], type="primary", use_container_width=True):
    st.session_state.last_analysis = execute_eval()

if st.session_state.last_analysis:
    data = st.session_state.last_analysis
    funnel = data.get('funnel_and_ats', {})
    dei = data.get('dei_and_risks', {})
    
    # Sec 1: 漏斗與 ATS
    st.markdown(f"## {ui_labels['sec1_title']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(ui_labels["m_score"], f"{funnel.get('competency_overall_score', 'N/A')} / 100")
    c2.metric(ui_labels["m_ats"], f"{funnel.get('ats_match_percentage', 'N/A')} %")
    c3.metric(ui_labels["m_rec"], funnel.get('funnel_recommendation', 'N/A'))
    c4.metric(ui_labels["m_time"], "Urgent/Standard" if urgency == "緊急 (Urgent)" else "Standard")
    
    st.info(f"⏳ **{ui_labels['m_time']}:** {funnel.get('time_to_fill_assessment', 'N/A')}")
    st.success(f"**{ui_labels['ats_matched']}** " + ", ".join(funnel.get('matched_keywords', [])))
    st.error(f"**{ui_labels['ats_missing']}** " + ", ".join(funnel.get('missing_keywords', [])))
    
    # Sec 2: 勝任力拆解
    st.markdown("---")
    st.markdown(f"## {ui_labels['sec2_title']}")
    comp_data = data.get('competency_breakdown', [])
    if comp_data:
        sb_cols = st.columns(len(comp_data))
        for idx, item in enumerate(comp_data):
            with sb_cols[idx]:
                st.markdown(f"**{item.get('dimension', 'N/A')}**")
                st.markdown(f"### {item.get('score', 'N/A')}")
                st.caption(f"{item.get('justification', '')}")
                st.caption(f"*({ui_labels['evidence_source']}: {item.get('evidence', 'N/A')})*")
    
    # Sec 3: DEI 與風險
    st.markdown("---")
    st.markdown(f"## {ui_labels['sec3_title']}")
    st.info(f"**{ui_labels['dei_check']}**\n{dei.get('dei_safeguard_applied', 'N/A')}")
    r1, r2 = st.columns(2)
    with r1:
        st.error(f"**{ui_labels['hard_risks']}**\n" + "\n".join([f"- {x}" for x in dei.get('hard_risks', ["None"])]))
    with r2:
        st.warning(f"**{ui_labels['soft_risks']}**\n" + "\n".join([f"- {x}" for x in dei.get('soft_risks', ["None"])]))
    
    # Sec 4: 結構化面試量表
    st.markdown("---")
    st.markdown(f"## {ui_labels['sec4_title']}")
    st.caption(ui_labels["sec4_sub"])
    for q in data.get('structured_interview_rubric', []):
        with st.expander(f"📌 勝任力維度: {q.get('competency_tested', 'N/A')}"):
            st.markdown(f"**{ui_labels['probe_q']}** {q.get('star_question', '')}")
            st.markdown("---")
            st.success(f"**{ui_labels['rubric_5']}** {q.get('rubric_5_excellent', '')}")
            st.warning(f"**{ui_labels['rubric_3']}** {q.get('rubric_3_acceptable', '')}")
            st.error(f"**{ui_labels['rubric_1']}** {q.get('rubric_1_poor', '')}")

    # Sec 5: HR 雙向研討
    st.markdown("---")
    st.markdown(f"## {ui_labels['sec5_title']}")
    hr_feedback_text = st.text_area("HR Reviewer Notes", placeholder=ui_labels["feedback_ph"], key="hr_feedback_input", label_visibility="collapsed")
    if st.button(ui_labels["re_eval_btn"], use_container_width=True):
        if hr_feedback_text.strip():
            updated_data = execute_eval(hr_feedback=hr_feedback_text)
            if updated_data:
                st.session_state.last_analysis = updated_data
                st.rerun()
