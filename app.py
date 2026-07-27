import streamlit as st
import pypdf
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

# 讀取後台預設 Secrets (如果有設定的話)
default_token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GEMINI_API_KEY", "")

# Sidebar: 設定與 Multi-Provider 選擇
with st.sidebar:
    st.header("⚙️ 系統設定 (System Config)")
    
    # 模式選擇
    if default_token:
        key_mode = st.radio(
            "選擇 AI 金鑰模式：",
            ["使用系統預設免費 Key", "使用自己 AI API Key (自由選擇供應商)"],
            index=0
        )
    else:
        key_mode = "使用自己 AI API Key (自由選擇供應商)"

    # 引擎與 Key 處理邏輯
    if key_mode == "使用系統預設免費 Key":
        provider = "GitHub Models"
        api_key = default_token
        st.success("✅ 已載入系統預設免費 Key (保護中，不顯示)")
    else:
        provider = st.selectbox(
            "選擇你的 AI 供應商 (Provider)：",
            ["OpenAI", "DeepSeek", "Google Gemini", "Groq", "GitHub Models"]
        )
        
        help_texts = {
            "OpenAI": "輸入 OpenAI API Key (sk-...)",
            "DeepSeek": "輸入 DeepSeek API Key (sk-...)",
            "Google Gemini": "輸入 Google Gemini API Key (AIzaSy...)",
            "Groq": "輸入 Groq API Key (gsk_...)",
            "GitHub Models": "輸入 GitHub Personal Access Token (ghp_...)"
        }
        
        api_key = st.text_input(
            f"輸入你的 {provider} Key", 
            type="password",
            placeholder=help_texts[provider]
        )

    st.divider()
    st.markdown("### 🧠 人才科學與管治框架")
    st.markdown("""
    - **人才密度 (Talent Density):** 識別 A 級玩家。
    - **組織契約 (Org. Contract):** 區分承諾型與交易型。
    - **ISO 42001 管治:** 落實高風險 AI 系統風險管控。
    - **AIGP 合規:** 確保 HITL (人類監督) 與去偏見 (Bias Mitigation)。
    """)
    st.divider()
    st.markdown("🔐 **數據管治聲明：** 本地 Session 運作，零數據留存。符合 PDPO 及歐盟 AI 法案 (EU AI Act) 高風險系統合規指引。")

def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Header
st.title("🎯 慧聘 · 智析官 (TalentScout AI)")
st.caption("🚀 **Universal AI-Driven Talent Science & Governance**｜內建 ISO 42001 與 AIGP 合規審查機制")

# Main UI: 三欄式上傳與輸入區
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("📄 1. 職位描述 (JD)")
    jd_input_type = st.radio("輸入方式", ["貼上文字", "上傳 PDF"], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == "貼上文字":
        jd_text = st.text_area("請貼上 JD 內容：", height=200, placeholder="包含職責、必備條件等...")
    else:
        jd_file = st.file_uploader("上傳 JD PDF", type=["pdf"], key="jd_pdf")
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file)

with col2:
    st.subheader("👤 2. 求職者履歷 (CV)")
    cv_file = st.file_uploader("上傳履歷 PDF", type=["pdf"], key="cv_pdf")
    cv_text = ""
    if cv_file:
        cv_text = extract_text_from_pdf(cv_file)
        st.success(f"✅ 已讀取 CV：{cv_file.name}")

with col3:
    st.subheader("🎯 3. 特殊要求 (Preferences)")
    special_reqs = st.text_area(
        "輸入額外篩選條件（可留空）：", 
        height=200, 
        placeholder="例如：\n- 必須精通廣東話/英語\n- 必須接受每週 5 天到現場工作\n- 優先考慮具備金融背景者\n- 期望薪酬不能超過 HKD 40K"
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
                {"role": "system", "content": "You are a professional HR and AI Governance system that outputs raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

# Analyze Button
if st.button("🚀 啟動高階人才科學與合規審查 (Run Audit & Analysis)", type="primary", use_container_width=True):
    if not api_key:
        st.error(f"⚠️ 請在左側 Sidebar 輸入你的 {provider} API Key / Token！")
    elif not jd_text or not cv_text:
        st.warning("⚠️ 請同時提供 JD 與 CV 內容！")
    else:
        with st.spinner(f"AI 正在結合 ISO 42001 標準與 {provider} 引擎進行深度演算..."):
            try:
                # 組合 Prompt，加入頂級 AIGP 與 ISO 42001 指令
                prompt = f"""
You are a top-tier HR Executive and Certified AI Governance Professional (AIGP) operating at the board level in Hong Kong.
Your task is to analyze the provided JD and CV. Because AI recruitment is considered a "High-Risk AI System" under global frameworks (e.g., EU AI Act), your analysis MUST strictly adhere to ISO 42001 risk management principles.

Apply Talent Science (Talent Density, Organizational Contract, Career Drivers) AND conduct a rigorous AI Governance Audit (HITL, Bias Mitigation, Transparency).

Special Requirements:
{special_reqs if special_reqs.strip() else "None specified."}

Format your output STRICTLY in valid JSON matching this schema:
{{
  "overall_score": 85,
  "talent_density_tier": "A-Player (人才磁石)",
  "special_req_compliance": "Pass/Partial/Fail analysis on special requirements.",
  "organizational_contract": "Analysis of Commitment vs Transactional fit.",
  "career_driver_analysis": {{
    "primary_driver": "Candidate's core motivation...",
    "offer_strategy": "Tailored pitch strategy..."
  }},
  "aigp_governance_audit": {{
    "transparency_explainability": "Explainability: Briefly state the exact core algorithmic weights/factors that drove this score (Why this score?).",
    "human_in_the_loop_flag": "HITL requirement: Specify which impressive claims in the CV MUST be verified by a human (Reference Check) to prevent Automation Bias.",
    "bias_and_fairness": "Fairness Assessment: Identify any potential disparate impact, age proxies, gendered language, or prestige bias (Halo effect) in this evaluation.",
    "iso42001_risk_control": "Risk Control: Recommend one specific action for the hiring manager to mitigate the deployment risk of relying on this AI output."
  }},
  "sourcing_expansion": "Unconventional sourcing suggestions.",
  "behavioral_star_questions": [
    {{
      "kpi_focus": "Core competency...",
      "question": "Behavioral question...",
      "anti_bs_probe": "Anti-BS follow-up..."
    }}
  ]
}}

Output ONLY the raw JSON string, without markdown formatting or code blocks. Bilingual format (Traditional Chinese + English HR/Risk terms).

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                # 採用正則表達式強健抓取 JSON 區塊，預防語法截斷或 Markdown 引號干擾
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    clean_json = json_match.group(0)
                else:
                    clean_json = raw_response.strip()

                data = json.loads(clean_json)
                
                # Dashboard Visualization
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

                if special_reqs.strip():
                    st.info(f"🎯 **特殊要求合規審查 (Special Requirements Audit):**\n\n{data.get('special_req_compliance', '已納入評估')}")

                st.markdown("---")
                st.markdown("## ⚖️ 2. AI 治理與合規審查 (AIGP & ISO 42001 Audit)")
                st.caption("⚠️ *依據高風險 AI 系統管理框架，本系統提供以下決策輔助與風險緩解建議。*")
                
                gov1, gov2 = st.columns(2)
                with gov1:
                    st.markdown("**🔍 決策透明度與可解釋性 (Transparency & Explainability):**")
                    st.write(data['aigp_governance_audit']['transparency_explainability'])
                    
                    st.markdown("**⚖️ 公平性與偏見緩解 (Bias & Fairness Assessment):**")
                    st.write(data['aigp_governance_audit']['bias_and_fairness'])
                
                with gov2:
                    st.error(f"**👨‍⚖️ 人類監督介入點 (Human-in-the-Loop, HITL):**\n\n{data['aigp_governance_audit']['human_in_the_loop_flag']}")
                    st.warning(f"**🛡️ ISO 42001 風險管控行動 (Risk Controls):**\n\n{data['aigp_governance_audit']['iso42001_risk_control']}")

                st.markdown("---")
                st.markdown("## 🏢 3. 組織契約與深層動機 (Org. Contract & Career Drivers)")
                strat1, strat2 = st.columns(2)
                with strat1:
                    st.markdown("**🤝 組織用人模型 (Organizational Contract Fit):**")
                    st.write(data['organizational_contract'])
                with strat2:
                    st.markdown(f"**🔥 核心驅動力 (Primary Driver):** {data['career_driver_analysis']['primary_driver']}")
                    st.markdown("**💡 專屬 Offer 說服策略 (Tailored Pitch Strategy):**")
                    st.write(data['career_driver_analysis']['offer_strategy'])

                st.markdown("---")
                st.markdown("## 🎯 4. 實戰行為面試指南 (Behavioral STAR Interview)")
                st.caption("💡 *管治原則：嚴禁使用「假設性問題」，只探究真實歷史行為以預測未來表現。*")
                for idx, q in enumerate(data['behavioral_star_questions'], 1):
                    with st.expander(f"📌 核心指標 (KPI Focus)：{q['kpi_focus']}"):
                        st.markdown(f"**🗣️ 歷史行為提問 (Behavioral Question)：** {q['question']}")
                        st.markdown(f"**🕵️ 測謊與深挖追問 (Anti-BS Probe)：** {q['anti_bs_probe']}")
                        
            except Exception as e:
                st.error(f"❌ 分析過程出現錯誤 (請檢查 API Key 或網路狀態)：{str(e)}")
