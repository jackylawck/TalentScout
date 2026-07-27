import streamlit as st
import pypdf
import json
from google import genai
from google.genai import types

# 頁面標題與配置
st.set_page_config(
    page_title="慧聘 · 智析官 (TalentScout AI - HK)",
    page_icon="🎯",
    layout="wide"
)

# 系統標題
st.title("🎯 慧聘 · 智析官 (TalentScout AI) - 戰略總監版")
st.caption("🚀 **自備 Key・零風險**｜融合 4B 戰略、ASA 理論、冰山模型與高階 STAR 提問")

# Sidebar: 設定 API Key
with st.sidebar:
    st.header("⚙️ 系統設定 (BYOK)")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    st.markdown("[👉 點此免費申請 Gemini API Key](https://aistudio.google.com/)")
    st.divider()
    st.markdown("### 🧠 內建 TA 戰略分析引擎")
    st.markdown("""
    - **4B 獲取戰略：** Buy (挖角) / Build (培養) / Borrow (合約) / Bridge (轉型)
    - **ASA 留存預測：** 評估 P-J Fit (人崗) 與 P-O Fit (文化)，預測流失風險。
    - **科學測評建議：** GMA、工作樣本或結構化面試建議。
    - **冰山與 ABC：** 深挖內驅力與阿里式分級。
    """)
    st.divider()
    st.markdown("🔐 **私隱聲明：** 數據僅存於本地 Session，零上傳，符合 PDPO 指引。")

def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# 主介面：上傳與輸入區
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 1. 輸入職位描述 (JD)")
    jd_input_type = st.radio("JD 輸入方式", ["直接貼上文字", "上傳 PDF"], key="jd_type", horizontal=True)
    jd_text = ""
    if jd_input_type == "直接貼上文字":
        jd_text = st.text_area("請貼上 JD 內容：", height=200)
    else:
        jd_file = st.file_uploader("上傳 JD PDF", type=["pdf"], key="jd_pdf")
        if jd_file:
            jd_text = extract_text_from_pdf(jd_file)

with col2:
    st.subheader("👤 2. 輸入求職者履歷 (CV)")
    cv_file = st.file_uploader("上傳求職者 CV (PDF 格式)", type=["pdf"], key="cv_pdf")
    cv_text = ""
    if cv_file:
        cv_text = extract_text_from_pdf(cv_file)
        st.success(f"已讀取 CV：{cv_file.name}")

st.markdown("---")

# 升級版 JSON Schema (注入 TA 戰略架構)
analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "overall_score": {"type": "INTEGER", "description": "0-100 的整體匹配分數"},
        "abc_classification": {"type": "STRING", "description": "A類(堅決拿下) / B類(符合預期) / C類(堅決淘汰)"},
        "strategy_4b": {
            "type": "STRING", 
            "description": "基於 4B 模型給予招聘戰略建議：Buy (直接高薪買斷經驗)、Build (具潛力可內部培養)、Borrow (建議以外包/合約形式合作) 或 Bridge (建議跨崗位轉型)。請說明原因。"
        },
        "asa_retention_analysis": {
            "type": "OBJECT",
            "properties": {
                "fit_analysis": {"type": "STRING", "description": "Person-Job Fit (人崗匹配) 與 Person-Organization Fit (人企文化匹配) 綜合分析。"},
                "attrition_risk": {"type": "STRING", "description": "預測該候選人的流失/離職風險 (Attrition Risk) 高低及潛在原因。"}
            }
        },
        "iceberg_analysis": {
            "type": "OBJECT",
            "properties": {
                "surface_skills": {"type": "STRING", "description": "冰山之上 (Skills-based)：具體核心技能與量化業績。"},
                "deep_potential": {"type": "STRING", "description": "冰山之下：價值觀、內驅力、抗壓力。"}
            }
        },
        "core_strengths": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "red_flags": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "selection_recommendation": {
            "type": "STRING",
            "description": "建議的下一步科學測評方法 (如：GMA 認知測試、Work Sample 工作樣本測試、Case Study 等) 及其原因。"
        },
        "star_questions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "scenario": {"type": "STRING", "description": "針對的 CV 經歷"},
                    "question": {"type": "STRING", "description": "STAR 面試題 (必須包含詢問遇到的困難/挫折)"},
                    "what_to_look_for": {"type": "STRING", "description": "觀察重點 (評估底層態度與邏輯)"}
                }
            }
        }
    },
    "required": ["overall_score", "abc_classification", "strategy_4b", "asa_retention_analysis", "iceberg_analysis", "core_strengths", "red_flags", "selection_recommendation", "star_questions"]
}

# 分析按鈕
if st.button("🚀 啟動「TA 戰略總監級」透視分析", type="primary", use_container_width=True):
    if not api_key:
        st.error("請在左側 Sidebar 輸入 Gemini API Key！")
    elif not jd_text or not cv_text:
        st.warning("請確保已同時提供 JD 與 CV 內容！")
    else:
        with st.spinner("AI 正在使用 4B 戰略、ASA 理論與冰山模型進行多維度運算..."):
            try:
                client = genai.Client(api_key=api_key)
                
                # 注入 TA 戰略大師的 Prompt
                prompt = f"""
你是一位精通「4B 人才戰略」、「ASA 吸引-選擇-流失理論」、「冰山理論」及「阿里人才邏輯」的跨國企業 TA 總監 (Head of Talent Acquisition)。
請對以下 JD 與 CV 進行深度戰略分析，並以「香港職場常用之繁體中文（可夾雜專業英文 HR 術語）」輸出。

重點指令：
1. 運用 4B 模型 (Buy/Build/Borrow/Bridge) 建議最適合的聘用戰略。
2. 運用 ASA 理論，嚴格評估 P-O Fit (企業文化匹配) 及潛在的流失風險 (Attrition Risk)。
3. 以 Skills-based hiring 視角拆解冰山模型。
4. 建議最適合此崗位的科學甄選方法 (Selection Methods, 如 GMA, Work Sample)。

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
                
                # ================= 視覺化渲染 Dashboard =================
                st.markdown("## 📊 1. 戰略定位與綜合匹配")
                colA, colB, colC = st.columns([1, 1, 2])
                with colA:
                    st.metric(label="綜合匹配得分", value=f"{data['overall_score']} / 100")
                    st.progress(data['overall_score'] / 100)
                with colB:
                    abc_class = data['abc_classification']
                    if "A類" in abc_class:
                        st.success(f"🏆 {abc_class}")
                    elif "B類" in abc_class:
                        st.info(f"👍 {abc_class}")
                    else:
                        st.error(f"⚠️ {abc_class}")
                with colC:
                    st.info(f"🧭 **4B 人才戰略建議：**\n{data['strategy_4b']}")

                st.markdown("---")
                st.markdown("## 🧬 2. ASA 理論：匹配度與流失風險預測")
                asa1, asa2 = st.columns(2)
                with asa1:
                    st.markdown("**🤝 人崗與文化匹配 (P-J & P-O Fit)：**")
                    st.write(data['asa_retention_analysis']['fit_analysis'])
                with asa2:
                    st.markdown("**🚨 離職/流失風險 (Attrition Risk)：**")
                    st.write(data['asa_retention_analysis']['attrition_risk'])

                st.markdown("---")
                st.markdown("## 🏔️ 3. 冰山模型深度透視 (Skills-based Analysis)")
                ice1, ice2 = st.columns(2)
                with ice1:
                    st.markdown("**🌊 冰山之上 (核心技能與量化業績)：**")
                    st.write(data['iceberg_analysis']['surface_skills'])
                with ice2:
                    st.markdown("**🧊 冰山之下 (潛在內驅力與底層素養)：**")
                    st.write(data['iceberg_analysis']['deep_potential'])

                st.markdown("---")
                st.markdown("## ⚖️ 4. 核心優勢 vs. 潛在風險")
                adv_col, risk_col = st.columns(2)
                with adv_col:
                    st.success("### ✅ 核心優勢 (Results/Impact)")
                    for s in data['core_strengths']:
                        st.markdown(f"- {s}")
                with risk_col:
                    st.error("### 🚩 潛在風險 (Red Flags)")
                    for r in data['red_flags']:
                        st.markdown(f"- {r}")

                st.markdown("---")
                st.markdown("## 🧪 5. 科學測評建議 (Selection Method)")
                st.info(f"**建議的下一步測評工具：** {data['selection_recommendation']}")

                st.markdown("## 🎯 6. 高階 STAR 面試攻防題庫")
                st.caption("💡 *總監心法：不問結論，問過程；問挫折，看底層態度與靈活性。*")
                for idx, q in enumerate(data['star_questions'], 1):
                    with st.expander(f"📌 題目 {idx}：針對【{q['scenario']}】"):
                        st.markdown(f"**🗣️ 靈魂拷問：** {q['question']}")
                        st.markdown(f"**👁️ 考官觀察重點：** {q['what_to_look_for']}")
                        
            except Exception as e:
                st.error(f"分析過程出現錯誤：{str(e)}")
