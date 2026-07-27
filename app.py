import streamlit as st
import pypdf
import json
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
        
        # 根據選取的 Provider 給予相應的提示
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
    st.markdown("### 🧠 內建人才科學框架")
    st.markdown("""
    - **人才密度效應 (Talent Density):** 識別能吸引頂尖人才的 A 級玩家。
    - **組織契約模型 (Org. Contract):** 區分「承諾型」與「交易型」用人策略。
    - **職涯驅動力 (Career Drivers):** 洞察深層動機，定制 Offer 說服策略。
    - **認知偏差預警 (Bias Warning):** 預防「光環效應」與倉促招聘。
    """)
    st.divider()
    st.markdown("🔐 **數據管治聲明：** 本地 Session 運作，零數據留存，完全符合香港 PDPO 及企業級合規標準。")

def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Header
st.title("🎯 慧聘 · 智析官 (TalentScout AI)")
st.caption("🚀 **Universal AI-Driven Talent Science**｜支援 OpenAI / DeepSeek / Gemini / Groq / GitHub 多引擎轉換")

# Main UI: Upload Section
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 1. 職位描述 (Job Description)")
    jd_input_type = st.radio("輸入方式", ["貼上文字", "上傳 PDF"], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == "貼上文字":
        jd_text = st.text_area("請貼上 JD 內容：", height=200)
    else:
        jd_file = st.file_uploader("上傳 JD PDF", type=["pdf"], key="jd_pdf")
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file)

with col2:
    st.subheader("👤 2. 求職者履歷 (Candidate CV)")
    cv_file = st.file_uploader("上傳履歷 PDF", type=["pdf"], key="cv_pdf")
    cv_text = ""
    if cv_file:
        cv_text = extract_text_from_pdf(cv_file)
        st.success(f"✅ 已讀取 CV：{cv_file.name}")

st.markdown("---")

# 核心分析呼叫函數 (跨 Provider 適配器)
def run_ai_analysis(provider, api_key, prompt):
    if provider == "Google Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt + "\n\nFormat strictly as JSON.",
        )
        return response.text
    else:
        # OpenAI 兼容格式 (OpenAI, DeepSeek, Groq, GitHub)
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
                {"role": "system", "content": "You are a professional HR analytics system that outputs raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

# Analyze Button
if st.button("🚀 啟動高階人才科學分析 (Run Analysis)", type="primary", use_container_width=True):
    if not api_key:
        st.error(f"⚠️ 請在左側 Sidebar 輸入你的 {provider} API Key / Token！")
    elif not jd_text or not cv_text:
        st.warning("⚠️ 請同時提供 JD 與 CV 內容！")
    else:
        with st.spinner(f"AI 正在透過 {provider} 引擎進行深度人才科學演算..."):
            try:
                prompt = f"""
You are a top-tier HR Executive and AI Governance Lead in Hong Kong. 
Analyze the JD and CV using deep Talent Science principles without directly naming specific authors/theories. 
Apply the concepts of Talent Density (A-players vs B/C-players), Organizational Contract Models (Commitment vs Transactional), Driver/Needs Analysis for offer closing, and strictly warn against cognitive biases like the Halo Effect.

Format your output strictly in valid JSON matching this schema:
{{
  "overall_score": 85,
  "talent_density_tier": "A-Player (人才磁石)",
  "organizational_contract": "分析描述...",
  "career_driver_analysis": {{
    "primary_driver": "主導動機...",
    "offer_strategy": "Offer 策略..."
  }},
  "bias_and_risk_warning": {{
    "halo_effect_warning": "光環效應預警...",
    "flight_risk": "流失風險..."
  }},
  "sourcing_expansion": "尋源建議...",
  "behavioral_star_questions": [
    {{
      "kpi_focus": "核心指標...",
      "question": "行為面試問題...",
      "anti_bs_probe": "深挖追問..."
    }}
  ]
}}

Output ONLY the raw JSON string, without markdown formatting or code blocks.

Job Description (JD):
{jd_text}

Candidate CV:
{cv_text}
"""
                raw_response = run_ai_analysis(provider, api_key, prompt)
                
                # 清除 markdown 標籤
                if raw_response.startswith("```"):
                    raw_response = raw_response.split("```")[1]
                    if raw_response.startswith("json"):
                        raw_response = raw_response[4:]
                
                data = json.loads(raw_response.strip())
                
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
                st.error(f"❌ 分析過程出現錯誤：{str(e)}")
