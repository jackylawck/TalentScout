# domain_map.py
# 🇭🇰 香港本土產業生態與集團關聯動態矩陣 (Hong Kong Talent Domain Knowledge Matrix)
# Version: 6.0.0 (Dynamic Fingerprint Edition)

__version__ = "6.0.0"

ALIAS_MAP = {
    "SHKP": "Sun Hung Kai Properties", "新鴻基": "Sun Hung Kai Properties", "新地": "Sun Hung Kai Properties",
    "Vanke": "Vanke", "萬科": "Vanke",
    "NWD": "New World Development", "新世界": "New World Development",
    "CK Asset": "Cheung Kong", "長實": "Cheung Kong",
    "MTR": "MTR Corporation", "港鐵": "MTR Corporation",
    "HKSTP": "Hong Kong Science Park", "科技園": "Hong Kong Science Park",
    "HKIC": "Hong Kong Institute of Construction", "建造學院": "Hong Kong Institute of Construction",
    "HKTDC": "Trade Development Council", "貿發局": "Trade Development Council",
    "Computime": "Computime", "金寶通": "Computime",
    "Big 4": "Big Four Accounting Firms", "四大": "Big Four Accounting Firms",
    "FMCG": "Fast-Moving Consumer Goods"
}

# 動態產業指紋矩陣 (Industry Fingerprint Matrix)
INDUSTRY_DOMAIN_MAP = {
    "Real Estate, Property & Construction (地產、物業、建築與基建)": {
        "core_skills": ["Real Estate", "Property Development", "Property Management", "Construction", "Civil Engineering", "Facilities Management", "BIM", "Quantity Surveying"],
        "major_employers": ["Sun Hung Kai Properties", "Vanke", "Henderson Land", "New World Development", "Sino Group", "Swire Properties", "Meinhardt", "Arup", "Gammon"],
        "public_bodies": ["Urban Renewal Authority", "Housing Authority", "Buildings Department", "Construction Industry Council"],
        "upstream_downstream": ["Conglomerates & Public Utilities (綜合企業與公用事業)"],
        "common_pathways": {
            "inbound": ["Professional Services (專業服務-測量/工程顧問)"],
            "outbound": ["Conglomerates & Public Utilities (綜合企業)"]
        }
    },
    "Financial Services & FinTech (金融服務與金融科技)": {
        "core_skills": ["Investment Banking", "Wealth Management", "Asset Management", "Insurance", "FinTech", "Web3", "Crypto", "Risk Management", "Compliance"],
        "major_employers": ["HSBC", "Bank of China", "Standard Chartered", "J.P. Morgan", "Goldman Sachs", "AIA", "Prudential", "HashKey", "OSL", "Bowtie"],
        "public_bodies": ["HKEX", "SFC", "HKMA", "Insurance Authority"],
        "upstream_downstream": ["Professional Services (專業服務-審計/諮詢)", "Tech, E-Commerce & Logistics (科技)"],
        "common_pathways": {
            "inbound": ["Big Four Accounting Firms", "Professional Services (專業服務)"],
            "outbound": ["Tech, E-Commerce & Logistics (金融科技新創)"]
        }
    },
    "Tech, E-Commerce & Logistics (科技、跨境電商與供應鏈)": {
        "core_skills": ["IT Operations", "Cloud Infrastructure", "E-Commerce", "Supply Chain", "Logistics", "Cross-border Operations", "SaaS", "Data Analytics"],
        "major_employers": ["Tencent HK", "Alibaba HK", "Huawei HK", "ByteDance HK", "HKTVMall", "Shopify", "Cainiao", "SF Express", "Lalamove", "Computime"],
        "public_bodies": ["Hong Kong Science Park", "Cyberport", "ASTRI"],
        "upstream_downstream": ["Retail & FMCG (零售與消費品)", "Financial Services & FinTech (金融科技)"],
        "common_pathways": {
            "inbound": ["Retail & FMCG (傳統零售轉型)"],
            "outbound": ["Financial Services & FinTech (數位金融)"]
        }
    },
    "Conglomerates & Public Utilities (綜合企業、新能源與公用事業)": {
        "core_skills": ["Conglomerate", "Public Utilities", "Aviation", "Transport", "ESG", "Sustainability", "Corporate Governance", "Fleet Management"],
        "major_employers": ["Hutchison Whampoa", "Jardine Matheson", "MTR Corporation", "Cathay Pacific", "CLP", "HK Electric", "Towngas"],
        "public_bodies": ["Airport Authority", "Environmental Protection Department"],
        "upstream_downstream": ["Real Estate, Property & Construction (地產基建)"],
        "common_pathways": {
            "inbound": ["Real Estate, Property & Construction", "Professional Services (企業戰略)"],
            "outbound": ["Media, Public Affairs & PR (公共事務)"]
        }
    },
    "Professional Services & Consulting (專業服務、法律與諮詢)": {
        "core_skills": ["Audit", "Tax", "Advisory", "Management Consulting", "Legal Support", "Corporate Governance", "Due Diligence"],
        "major_employers": ["Big Four Accounting Firms", "McKinsey", "BCG", "Bain", "Deacons", "Korn Ferry"],
        "public_bodies": ["HKICS", "CPA", "Law Society of Hong Kong"],
        "upstream_downstream": ["Financial Services & FinTech (金融服務)"],
        "common_pathways": {
            "inbound": ["Financial Services & FinTech (合規/法務)"],
            "outbound": ["Financial Services & FinTech (In-house Audit/Compliance)", "Conglomerates & Public Utilities (內部戰略)"]
        }
    },
    "Retail, FMCG & Hospitality (零售、消費品與餐飲酒店)": {
        "core_skills": ["Fast-Moving Consumer Goods", "Retail Operations", "Merchandising", "Sourcing", "Hotel Management", "Hospitality", "Customer Service"],
        "major_employers": ["Dairy Farm", "AS Watson", "Lane Crawford", "Shangri-La", "Marriott", "Maxim's", "Cafe de Coral"],
        "public_bodies": ["Tourism Board"],
        "upstream_downstream": ["Tech, E-Commerce & Logistics (電商物流)"],
        "common_pathways": {
            "inbound": ["Media, Public Affairs & PR (品牌行銷)"],
            "outbound": ["Tech, E-Commerce & Logistics (電商供應鏈)"]
        }
    }
}
