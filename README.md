# 🎯 慧聘 · 智析官 (TalentScout AI)
> **Enterprise ATS Screening, Competency Assessment & DEI Governance System**  
> **企業級 ATS 智慧初篩、勝任力評估與多元包容 (DEI) 管治系統**

[![TalentScout CI & Security Audit](https://github.com/jackylawck/TalentScout/actions/workflows/ci.yml/badge.svg)](https://github.com/jackylawck/TalentScout/actions/workflows/ci.yml)
[![CodeQL Advanced](https://github.com/jackylawck/TalentScout/actions/workflows/codeql.yml/badge.svg)](https://github.com/jackylawck/TalentScout/actions/workflows/codeql.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://talentscout-open.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![HR Tech](https://img.shields.io/badge/HR_Tech-ATS_%7C_DEI_%7C_ISO_42001-orange)

---

## 🌐 網頁版即時體驗 (Live Demo)
👉 **[點此啟動 TalentScout AI 部署系統](https://talentscout-open.streamlit.app)**

---

## 📖 專案簡介 (Overview)

### 🇭🇰 繁體中文
**慧聘 · 智析官 (TalentScout AI)** 是一個專為高階 HR 負責人、招聘主管與企業決策者打造的全方位 ATS 智慧初篩與 AI 管治系統。

本系統深度融合了**人才科學 (Talent Science)**、**勝任力模型 (Competency Modeling)**、**DEI (多元、公平與包容) 防偏誤機制**，以及 **ISO 42001 人工智能管治標準**。系統能自動精準比對 ATS 關鍵字、隔離無意識偏見、進行 5 維勝任力量化打分，並自動生成 1-3-5 分制的結構化行為面試評估量表 (Interview Rubric)。

### 🇬🇧 English
**TalentScout AI** is an enterprise-grade ATS screening and AI Governance platform designed for Senior HR Executives, Talent Acquisition Leads, and Hiring Managers.

By integrating **Talent Science**, **Competency-Based Modeling**, **DEI (Diversity, Equity & Inclusion) Safeguards**, and **ISO 42001 Governance Standards**, TalentScout AI provides automated ATS keyword matching, active bias mitigation, quantitative competency scoring, and standardized 1-3-5 point structured interview scoring rubrics.

---

## 🌟 核心特色模組 (Key Features)

| 模組 (Module) | 說明 (Traditional Chinese) | Description (English) |
| :--- | :--- | :--- |
| **🔍 ATS 關鍵字比對** | 自動提取 JD 核心硬技能，精準分析 CV 之「命中 (Matched)」與「缺失 (Missing)」關鍵字。 | Extracts core hard skills from JDs to pinpoint exact matched and missing CV keywords. |
| **📈 量化勝任力模型** | 動態對齊職位核心職能（硬實力、解決問題、團隊領導），進行 0-100 分量化評估。 | Evaluates candidates across role-specific competency dimensions with 0-100 scoring. |
| **⚖️ DEI 防偏誤機制** | 建立主動防護網，強制排除年齡、性別、院校光環等無意識偏見，落實包容性招聘。 | Active safeguards against age, gender, or brand prestige biases to foster inclusive hiring. |
| **🎯 結構化面試量表** | 基於勝任力生成 STAR 行為面試問題，並提供 1 分 (需關注)、3 分 (合格)、5 分 (優秀) 之明確評判標準。 | Generates STAR behavioral probes paired with clear 1-3-5 point scoring rubrics. |
| **⏳ 招聘時效與漏斗** | 評估候選人到職準備期 (Time-to-Fill Risk)，並提供明確的招聘漏斗推進建議 (Funnel Action)。 | Assesses readiness and Time-to-Fill risks, recommending explicit funnel next-steps. |
| **🎖️ 內部推薦加權** | 內建員工推薦 (Internal Referral) 加權邏輯，在維持硬性條件死線的同時優化文化契合度評估。 | Applies referral weighting to optimize cultural fit evaluations without compromising baseline qualifications. |
| **🤝 人類監督與校正** | 支援 Human-in-the-Loop (HITL) 機制，HR 可輸入電話初篩洞察，驅動 AI 進行二次動態校正。 | Enables HR to input screening feedback for dynamic real-time model re-evaluation. |

---

## 🛡️ 數據安全與隱私防護 (Data Privacy & Security)

* **🔐 零數據留存 (Zero Data Retention):** 全 Session 記憶體運算，不儲存任何上傳之 CV、JD 或分析數據，頁面重整即完全清空。
* **📁 檔案安全限制 (15MB Limit):** 內建 `.streamlit/config.toml` 安全配額限制，單檔上傳上限為 15MB，兼顧大型作品集與系統性能。
* **🔑 BYOK 直連加密 (Bring Your Own Key):** 支援使用者輸入個人 API Key (OpenAI, DeepSeek, Google Gemini, Groq, GitHub Models)，數據直連官方端點。
* **⚖️ 私隱條例合規 (HK PDPO Compliant):** 嚴格遵循香港《個人資料（私隱）條例》及國際高風險 AI 管治指引。

---

## 🛠️ 技術堆疊 (Tech Stack)

* **Frontend & UI:** [Streamlit](https://streamlit.io/) (100% Dynamic Bilingual UI & Responsive Layout)
* **Document Parsing:** `pypdf`, `python-docx` (Supports PDF, DOCX, DOC with Multi-CV upload)
* **AI Multi-Engine:** OpenAI GPT-4o, DeepSeek-Chat, Google Gemini 2.5 Flash, Groq Llama-3.3, GitHub Models
* **CI/CD & Security:** GitHub Actions (Automated Syntax Compile Check, Bandit Security Audit, CodeQL Scan)
* **Governance & HR Framework:** ISO/IEC 42001 (AIMS), DEI Recruitment Guidelines, Structured Interview Rubric Methodology

---

## 🚀 本地開發與部署 (Local Setup)

```bash
# 1. Clone 本專案
git clone [https://github.com/jackylawck/TalentScout.git](https://github.com/jackylawck/TalentScout.git)
cd TalentScout

# 2. 安裝必要套件
pip install -r requirements.txt

# 3. 啟動 Streamlit 本地伺服器
streamlit run app.py
