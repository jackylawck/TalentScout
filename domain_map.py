# domain_map.py
# 🇭🇰 香港本土產業生態與集團關聯語意圖譜 (Hong Kong Talent Domain Knowledge Base)
# Version: 3.0.0

__version__ = "3.0.0"

# 1. 雙向別名與中英俗稱映射 (支援中文免分詞匹配)
ALIAS_MAP = {
    "SHKP": "Sun Hung Kai Properties",
    "新鴻基": "Sun Hung Kai Properties",
    "新地": "Sun Hung Kai Properties",
    "Vanke": "Vanke",
    "萬科": "Vanke",
    "NWD": "New World Development",
    "新世界": "New World Development",
    "CK Asset": "Cheung Kong",
    "長實": "Cheung Kong",
    "MTR": "MTR Corporation",
    "港鐵": "MTR Corporation",
    "HKSTP": "Hong Kong Science Park",
    "科技園": "Hong Kong Science Park",
    "HKIC": "Hong Kong Institute of Construction",
    "建造學院": "Hong Kong Institute of Construction",
    "HKTDC": "Trade Development Council",
    "貿發局": "Trade Development Council",
    "Computime": "Computime",
    "金寶通": "Computime",
    "Big 4": "Big Four Accounting Firms",
    "四大": "Big Four Accounting Firms"
}

# 2. 多維度產業生態標籤系統
INDUSTRY_DOMAIN_MAP = {
    "Real Estate, Property & Construction (地產、物業、建築與基建)": {
        "core_keywords": ["Real Estate", "Property Development", "Property Management", "Construction", "Civil Engineering", "Facilities Management"],
        "skill_tags": ["BIM", "AutoCAD", "Quantity Surveying", "Tenancy", "Leasing", "Urban Planning"],
        "major_employers": ["Sun Hung Kai Properties", "Vanke", "Henderson Land", "New World Development", "Sino Group", "Swire Properties", "Meinhardt", "Arup", "Gammon"],
        "public_bodies": ["Urban Renewal Authority", "Housing Authority", "Buildings Department", "Construction Industry Council"]
    },
    "Banking, Finance, Insurance & Web3 (銀行、金融、保險與虛擬資產)": {
        "core_keywords": ["Investment Banking", "Corporate Banking", "Wealth Management", "Private Banking", "Asset Management", "Insurance", "FinTech", "Web3", "Crypto"],
        "skill_tags": ["Risk Management", "Compliance", "Actuarial", "Trade Finance", "Blockchain"],
        "major_employers": ["HSBC", "Bank of China", "Standard Chartered", "J.P. Morgan", "Goldman Sachs", "AIA", "Prudential", "HashKey", "OSL", "Bowtie"],
        "public_bodies": ["HKEX", "SFC", "HKMA", "Insurance Authority"]
    },
    "Tech, E-Commerce & Supply Chain (科技、跨境電商與供應鏈)": {
        "core_keywords": ["IT Operations", "Cloud Infrastructure", "E-Commerce", "Supply Chain", "Logistics", "Cross-border Operations", "SaaS"],
        "skill_tags": ["AWS", "Azure", "GCP", "SAP", "ERP", "Procurement", "Data Analytics"],
        "major_employers": ["Tencent HK", "Alibaba HK", "Huawei HK", "ByteDance HK", "HKTVMall", "Shopify", "Cainiao", "SF Express", "Lalamove", "Computime"],
        "public_bodies": ["Hong Kong Science Park", "Cyberport", "ASTRI"]
    },
    "Conglomerates, ESG & Public Utilities (綜合企業、新能源與公用事業)": {
        "core_keywords": ["Conglomerate", "Public Utilities", "Aviation", "Transport", "ESG", "Sustainability", "Renewable Energy"],
        "skill_tags": ["Carbon Auditing", "Environmental Engineering", "Corporate Governance", "Fleet Management"],
        "major_employers": ["Hutchison Whampoa", "Jardine Matheson", "MTR Corporation", "Cathay Pacific", "CLP", "HK Electric", "Towngas"],
        "public_bodies": ["Airport Authority", "Environmental Protection Department"]
    },
    "Media, Public Affairs, PR & Marketing (傳媒、公共事務、公關與行銷)": {
        "core_keywords": ["Public Relations", "Corporate Communications", "Event Management", "Crisis Management", "Digital Marketing", "Public Affairs"],
        "skill_tags": ["Branding", "Media Liaison", "Government Relations", "Copywriting", "SEO"],
        "major_employers": ["Ruder Finn", "RICE Communications", "Ogilvy", "Executive Counsel", "SCMP", "TVB"],
        "public_bodies": ["Trade Development Council", "Tourism Board", "InvestHK"]
    }
}
