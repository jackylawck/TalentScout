# 🎯 慧聘 · 智析官 (TalentScout AI)
> **Enterprise Talent Advisory & ISO 42001 AI Governance Audit System**  
> **企業級人才決策與 ISO 42001 人工智能管治合規審計系統**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://talentscout-open.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Governance](https://img.shields.io/badge/AI_Governance-ISO_42001-orange)

---

## 🌐 網頁版即時體驗 (Live Demo)
👉 **[點此啟動 TalentScout AI 部署系統](https://talentscout-open.streamlit.app)**

---

## 📖 專案簡介 (Overview)

### 🇭🇰 繁體中文
**慧聘 · 智析官 (TalentScout AI)** 是一個專為高階 HR 負責人、董事局顧問與用人主管（Line Managers）打造的企業級人才評估與 AI 管治合規系統。

不同於傳統僅給出黑盒評分的招募工具，TalentScout AI 結合了**高階人才科學 (Talent Science)**、**香港 PDPO 私隱規範**，以及 **ISO 42001 高風險 AI 系統管理標準**。系統提供可追溯的履歷證據鏈 (Evidence Table)、反證機制 (Counter-Evidence Checks)、硬/軟風險分層，以及具備 Strong Answer 與 Red Flag 辨識力的結構化 STAR 行為面試指南。

### 🇬🇧 English
**TalentScout AI** is an enterprise-grade Talent Advisory and AI Governance Audit platform designed for Senior HR Executives, Managing Directors, and Line Managers.

Unlike conventional recruitment AI that produces black-box scores, TalentScout AI strictly embeds **ISO 42001 Risk Management Principles** and **Hong Kong PDPO Privacy Standards**. It provides transparent evidence traceability, counter-evidence checks, hard vs. soft risk isolation, and role-tailored STAR interview probes featuring Strong and Red Flag response indicators.

---

## 🛡️ 數據安全與隱私防護 (Data Privacy & Security)

* **🔐 零數據留存 (Zero Data Retention):** 本系統採用全 Session 記憶體運算，不儲存任何上傳之 CV、JD 或分析數據，瀏覽器頁面重新整理即完全清空。
* **🔑 BYOK 直連架構 (Bring Your Own Key):** 支援使用者輸入個人 API Key (OpenAI, DeepSeek, Google Gemini, Groq, GitHub Models)，數據直接與官方 API 端點加密通信，不經過任何第三方中轉伺服器。
* **⚖️ 高風險 AI 管治 (EU AI Act & ISO 42001):** 將招募 AI 定位為「高風險 AI 系統」，落實決策可追溯性 (Traceability) 與人類監督 (Human-in-the-Loop, HITL) 防護網。

---

## 🌟 核心特色 (Key Features)

| 核心模組 (Module) | 說明 (Traditional Chinese) | Description (English) |
| :--- | :--- | :--- |
| **📊 五維分數拆解** | 拒絕黑盒分數，拆解硬條件、核心能力、行業匹配、風格與風險扣分。 | 5-subscore analytics breaking down Hard Req, Competency, Industry Fit, Culture, & Risk Deductions. |
| **📜 可追溯證據鏈** | 每項評價皆附帶履歷原文精確引用 (CV Quotes) 與來源段落，符合 ISO 42001 Audit Trail。 | Verbatim CV quotes & source mapping ensuring 100% traceability under ISO 42001. |
| **🔍 反證與去偏見** | 引入 Counter-Evidence 檢查機制，防範「光環效應」或單一訊號先入為主的偏見。 | Counter-evidence checks to prevent Halo Effect, prestige bias, or premature rejection. |
| **🚨 硬/軟風險分層** | 隔離簽證 (ASMTP)、語言等「硬死線」，與文化、適應力等「面試觀察點」。 | Separates hard blockers (visa/languages) from soft interview observation points. |
| **🎯 結構化面試指南** | 根據崗位屬性，自動生成 STAR 面試問題，並標註優秀特徵與危險警號 (Red Flags)。 | Generates targeted STAR probes with clear Strong and Red Flag answer patterns. |
| **🌐 全中文/全英切換** | 支援 UI 介面與 AI 分析報告一鍵切換純正繁體中文或 Executive 英文版面。 | Seamless one-click dynamic UI & report switching between Traditional Chinese & English. |

---

## 🛠️ 技術堆疊 (Tech Stack)

* **Frontend & UI:** [Streamlit](https://streamlit.io/)
* **Document Parsing:** `pypdf`, `python-docx` (Supports PDF, DOCX, DOC up to 200MB)
* **AI Multi-Engine:** OpenAI GPT-4o, DeepSeek-Chat, Google Gemini 2.5 Flash, Groq Llama-3.3, GitHub Models
* **Governance Framework:** ISO/IEC 42001 (AIMS), EU AI Act High-Risk AI System Guidance, HK PDPO Guidelines

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
