from datetime import datetime, time
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup
import json
import urllib.parse
import base64  # 🌟 確保加咗呢行，解碼圖片必備

# ==========================================
# 🛠️ 核心工具：將本地圖片轉成網頁睇得明嘅 Base64 格式
# （必須擺喺最頂，等下面呼叫佢嗰陣 Python 已經認得佢）
# ==========================================
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# ==========================================
# 🗺️ 圖片物資載入
# ==========================================
# 1. 🎯 主地圖底圖
# （提示：如果你想用啱啱上傳嗰張超靚手繪地圖，請將下面改為 "image_456467.jpg"）
MAP_IMAGE_NAME = "mapries地圖.png" 
map_base64 = get_base64_encoded_image(MAP_IMAGE_NAME)

# 2. 🛡️ 副圖預留位置（加了 try-except 保護，暫時冇副圖都唔會死機）
SUB_IMAGE_NAME = "sub_layer.png" 
try:
    sub_base64 = get_base64_encoded_image(SUB_IMAGE_NAME)
except Exception:
    sub_base64 = "" # 暫時未有副圖時，網頁會安全跳過中層


# ==================== 頁面基本設定 ====================
st.set_page_config(page_title="Un-Tourist 地道窮遊導航平台", page_icon="🌏", layout="wide")
st.title("🌏 Un-Tourist 地道窮遊導航平台 - Demo")
st.subheader("CCMF Funding Demo | 2026")

# ==================== 全局 Session State 初始化 ====================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = {"Day 1": []}
if "stamp_collection" not in st.session_state:
    st.session_state.stamp_collection = []
if "packing_list" not in st.session_state:
    st.session_state.packing_list = ["護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡", "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）", "洗漱用品", "藥物（常備藥）", "雨傘 / 摺傘"]
if "daily_list" not in st.session_state:
    st.session_state.daily_list = ["手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡", "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"]

# 用戶虛擬人仔與定位狀態初始化
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "nickname": "未命名窮遊俠",
        "avatar_style": "adventurer",  # 可選: adventurer, bottts, pixel-art
        "lat": 22.3193,
        "lng": 114.1694,
        "is_sharing": False
    }

# 模擬其他在線用戶（Demo 展現社交地圖用）
if "mock_users" not in st.session_state:
    st.session_state.mock_users = [
        {"nickname": "深水埗車仔麵神", "avatar": "https://api.dicebear.com/7.x/adventurer/svg?seed=Tommy", "coords": [22.3305, 114.1624]},
        {"nickname": "旺角文青小編", "avatar": "https://api.dicebear.com/7.x/adventurer/svg?seed=Mandy", "coords": [22.3195, 114.1698]},
        {"nickname": "西貢露營大師", "avatar": "https://api.dicebear.com/7.x/adventurer/svg?seed=Kevin", "coords": [22.3812, 114.2724]}
    ]

# 嘗試載入定位組件（如無安裝則跳過）
try:
    from streamlit_geolocation import streamlit_geolocation
    location = streamlit_geolocation()
except:
    location = None

# 建立 5 大核心功能 Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 實時社交地圖", "✈️ 智能行程", "👥 窮遊社群", "🧾 清單小貼士", "ℹ️ 關於平台"])

# ==========================================
# 🗺️ Tab 1: 實時尋寶地圖 (純JS零閃爍、原地彈窗、全功能保留版)
# ==========================================
with tab1:
    st.header("🗺️ 手繪風動態尋寶地圖")
    st.write("直接點擊地圖上的自訂圖標，即可在原地彈出詳細攻略卡片，與行程、打卡功能完美連動！")

    # ----------------------------------------
    # 📌 1. 擴充核心數據庫：精準對應正方形地圖百分比坐標 (x, y)
    # ----------------------------------------
    LANDMARKS = {
        "大澳漁村": {
            "x": 13, "y": 66, "category": "自然", "icon": "🛶", "eng": "Tai O Fishing Village",
            "time": "全天開放 (店舖多營業 10:00-18:00)", "transport": "🚌 於東涌站乘搭 11 號巴士",
            "tips": "建議坐舢舨小艇尋找白海豚，回程試試大澳沙翁！",
            "desc": "參觀香港獨特的水上棚屋，感受遠離繁囂的傳統漁村風情。"
        },
        "天壇大佛": {
            "x": 24, "y": 50, "category": "文化", "icon": "⛰️", "eng": "Big Buddha",
            "time": "10:00-17:30", "transport": "🚡 昂坪360纜車 / 23號巴士",
            "tips": "需要挑戰 268 級石階，參觀前記得準備好腳力！",
            "desc": "全球最高的戶外青銅坐佛，巍峨肅穆，是洗滌心靈的文化勝地。"
        },
        "海洋公園": {
            "x": 68, "y": 78, "category": "美食", "icon": "🐼", "eng": "Ocean Park · 香港島",
            "time": "10:00-19:00 (週末至20:00)", "transport": "🚇 地鐵海洋公園站",
            "tips": "建議購買網上優惠票，避開週末人潮",
            "desc": "世界級主題公園，擁有大熊貓、海洋生物及機動遊戲。"
        },
        "西貢市中心": {
            "x": 84, "y": 25, "category": "自然", "icon": "⚓", "eng": "Sai Kung Town",
            "time": "全天開放 (海鮮街多營業至 22:00)", "transport": "🚌 彩虹站乘 1A 綠色小巴",
            "tips": "可以在碼頭直接租街渡前往半月灣或橋咀島玩水！",
            "desc": "香港後花園，擁有風光如畫的海景與新鮮生猛的避風塘海鮮街。"
        },
        "黃大仙廟": {
            "x": 68, "y": 29, "category": "文化", "icon": "🙏", "eng": "Wong Tai Sin Temple",
            "time": "07:30-16:30", "transport": "🚇 觀塘綫 · 黃大仙站 B2 出口",
            "tips": "廟宇內香火鼎盛，求籤非常靈驗，記得保持誠心。",
            "desc": "香港著名祠廟，建築金碧輝煌，崇奉儒、釋、道三教，有求伴應。"
        },
        "九龍半島": {
            "x": 67, "y": 55, "category": "購物", "icon": "🛍️", "eng": "Kowloon Peninsula",
            "time": "11:00-23:00", "transport": "🚇 荃灣綫/觀塘綫 · 旺角站 E2 出口",
            "tips": "漫步女人街與波鞋街，感受地道香港霓虹夜景。",
            "desc": "香港最熱鬧的街區之一，充滿地道霓虹氣息與各式特色小攤檔。"
        },
        "長洲": {
            "x": 30, "y": 80, "category": "美食", "icon": "🍢", "eng": "Cheung Chau Island",
            "time": "渡輪全天候運營", "transport": "🚢 中環 5 號碼頭乘搭渡輪直達",
            "tips": "必食塊頭超大的巨型咖哩魚蛋、糯米糍與香脆炸鮮奶！",
            "desc": "充滿活力的小島，行山、睇日落、踩單車，仲可以參觀張保仔洞。"
        },
        "南丫島": {
            "x": 46, "y": 91, "category": "自然", "icon": "🐟", "eng": "Lamma Island",
            "time": "渡輪全天候運營", "transport": "🚢 中環 4 號碼頭乘搭渡輪直達",
            "tips": "感受索罟灣漁村風情，享受悠閒嘅海鮮與行山之旅。",
            "desc": "充滿異國風情與中西交融的小島，島上步伐悠閒，海鮮十分出名。"
        }
    }

    # ----------------------------------------
    # 🔍 2. 景點類別篩選 (頂部保留，數據同步過濾)
    # ----------------------------------------
    category_list = ["全部", "自然", "文化", "購物", "美食"]
    selected_cat = st.selectbox("🎯 篩選地圖景點類別", category_list)

    # 🛠️ 3. 處理來自 HTML 的隱藏交互（用來在不重整網頁下將行程和打卡數據塞回 Streamlit）
    # 建立兩個隱藏的按鈕和輸入框，供 JavaScript 在底層觸發 Python 邏輯
    if "action_trigger" not in st.session_state:
        st.session_state.action_trigger = ""
    if "action_place" not in st.session_state:
        st.session_state.action_place = ""

    # 使用 Streamlit 隱藏組件接收前端 JS 傳過來的打卡同加入行程指令
    cc1, cc2 = st.columns(2)
    with cc1:
        js_action = st.text_input("js_action", value="", key="js_act", label_visibility="collapsed")
    with cc2:
        js_place = st.text_input("js_place", value="", key="js_plc", label_visibility="collapsed")

    # 當檢測到 JS 傳值時，執行原有功能，絕不刪減！
    if js_action and js_place:
        if js_action == "add":
            if "Day 1" not in st.session_state.itinerary:
                st.session_state.itinerary["Day 1"] = []
            if not any(item["landmark"] == js_place for item in st.session_state.itinerary["Day 1"]):
                st.session_state.itinerary["Day 1"].append({
                    "time": "隨選時段",
                    "landmark": js_place,
                    "desc": LANDMARKS.get(js_place, {}).get("desc", "")
                })
                st.toast(f"📅 已將「{js_place}」同步加入 Day 1 行程表！", icon="✅")
            else:
                st.toast(f"👀 「{js_place}」已經喺行程表入面喇！")
        elif js_action == "stamp":
            if js_place not in st.session_state.stamp_collection:
                st.session_state.stamp_collection.append(js_place)
                st.balloons()
                st.toast(f"🏅 打卡成功！解鎖「{js_place}」徽章！", icon="🎉")
            else:
                st.toast(f"🐾 你之前已經收集過「{js_place}」的足跡囉！")
        
        # 執行完即時重設，防止循環觸發
        st.write("<script>window.parent.document.querySelectorAll('input[aria-label=\"js_action\"], input[aria-label=\"js_place\"]').forEach(i => {i.value = ''; i.dispatchEvent(new Event('input', {bubbles:true}))});</script>", unsafe_allow_html=True)

    # ----------------------------------------
    # 🏃‍♂️ 4. 準備人仔頭像數據
    # ----------------------------------------
    my_p = st.session_state.user_profile
    avatar_url = f"https://api.dicebear.com/7.x/{my_p.get('avatar_style', 'adventurer')}/svg?seed={urllib.parse.quote(my_p.get('nickname', '窮遊俠'))}"

    # ----------------------------------------
    # 🖼️ 5. 終極 HTML/CSS/JavaScript 一體化絲滑畫布
    # ----------------------------------------
    map_src = f"data:image/png;base64,{map_base64}" if map_base64 else ""
    sub_map_src = f"data:image/png;base64,{sub_base64}" if sub_base64 else ""

    # 將完整的 LANDMARKS 轉換成 JavaScript 字典，等前端 JS 可以完全自由操控彈窗
    import json
    js_landmarks_data = json.dumps(LANDMARKS, ensure_ascii=False)

    map_html = f"""
    <div style="position: relative; width: 100%; max-width: 800px; aspect-ratio: 1 / 1; margin: 0 auto; overflow: visible; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
        
        <img src="{map_src}" style="width: 100%; height: 100%; display: block; object-fit: contain; border-radius: 16px;" />
        
        {f'<img src="{sub_map_src}" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: contain; z-index: 2; pointer-events: none;" />' if sub_base64 else ''}

        <div id="markers-container"></div>

        <div id="popup-card" style="
            position: absolute;
            width: 320px;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 18px;
            box-shadow: 0 12px 36px rgba(15, 23, 42, 0.15);
            border: 1px solid rgba(226, 232, 240, 0.8);
            z-index: 9999;
            display: none; /* 初始隱藏 */
            opacity: 0;
            transition: opacity 0.2s ease-in-out;
        ">
            <div onclick="closePopup()" style="position: absolute; right: 16px; top: 16px; color: #94a3b8; font-size: 14px; cursor: pointer; font-weight: bold; width: 22px; height: 22px; text-align: center; line-height: 22px; border-radius: 50%; background: #f1f5f9;">✕</div>
            
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div id="pop-icon" style="font-size: 24px; background: #ffebe6; width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">🐼</div>
                <div style="padding-right: 20px;">
                    <h4 id="pop-title" style="margin: 0; font-size: 17px; color: #0f172a; font-weight: 700;">海洋公園</h4>
                    <div id="pop-eng" style="font-size: 11px; color: #64748b; margin-top: 1px;">Ocean Park · 香港島</div>
                </div>
            </div>
            
            <p id="pop-desc" style="font-size: 12px; color: #475569; line-height: 1.5; margin: 0 0 12px 0;">世界級主題公園...</p>
            
            <div style="display: flex; flex-direction: column; gap: 8px; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: flex-start; font-size: 12px; color: #334155;">
                    <span style="width: 20px;">🕒</span>
                    <div style="flex: 1;"><span style="color: #64748b;">營業時間：</span><span id="pop-time" style="color: #0f172a;">10:00-19:00</span></div>
                </div>
                <div style="display: flex; align-items: flex-start; font-size: 12px; color: #334155;">
                    <span style="width: 20px;">🚇</span>
                    <div style="flex: 1;"><span style="color: #64748b;">交通方式：</span><span id="pop-transport" style="color: #2563eb; font-weight: 500;">地鐵站</span></div>
                </div>
                <div style="display: flex; align-items: flex-start; font-size: 11px; color: #166534; background: #f0fdf4; padding: 6px 10px; border-radius: 8px; border-left: 3px solid #22c55e;">
                    <span style="width: 18px;">💡</span>
                    <div id="pop-tips" style="flex: 1;">小貼士...</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <div id="btn-add-itinerary" style="flex: 1; background: #ff4d4d; color: white; text-align: center; padding: 8px 0; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(255,77,77,0.25);">
                    📍 加入行程
                </div>
                <div id="btn-stamp" style="flex: 1; background: transparent; color: #ff4d4d; border: 1px solid #ff4d4d; text-align: center; padding: 7px 0; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer;">
                    📍 打卡
                </div>
            </div>
        </div>

        <div id="user-avatar" style="
            position: absolute; 
            left: 50%; 
            top: 50%; 
            transform: translate(-50%, -100%); 
            transition: left 1s cubic-bezier(0.25, 1, 0.5, 1), top 1s cubic-bezier(0.25, 1, 0.5, 1);
            z-index: 995;
            text-align: center;
            pointer-events: none;
        ">
            <div style="position: relative; width: 44px; height: 44px; margin: 0 auto;">
                <img src="{avatar_url}" style="width: 100%; height: 100%; border-radius: 50%; border: 3px solid #2563eb; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.25);" />
                <div style="position: absolute; top: -16px; left: 50%; transform: translateX(-50%); color: #2563eb; font-size: 14px; animation: bounce 1s infinite;">👇</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.85); color: white; font-size: 10px; padding: 2px 7px; border-radius: 10px; white-space: nowrap; margin-top: 3px; font-weight: bold;">
                {my_p.get('nickname', '未命名窮遊俠')}
            </div>
        </div>
    </div>

    <script>
        const landmarks = {js_landmarks_data};
        const selectedCategory = "{selected_cat}";
        
        // 渲染地圖上自訂設計嘅 Emoji 圖標
        const container = document.getElementById('markers-container');
        for (let name in landmarks) {{
            const data = landmarks[name];
            
            // 類別篩選過濾
            if (selectedCategory !== "全部" && data.category !== selectedCategory) continue;
            
            const marker = document.createElement('div');
            marker.className = 'map-marker';
            marker.style.position = 'absolute';
            marker.style.left = data.x + '%';
            marker.style.top = data.y + '%';
            marker.style.width = '34px';
            marker.style.height = '34px';
            marker.style.borderRadius = '50%';
            marker.style.backgroundColor = 'white';
            marker.style.border = '1px solid #cbd5e1';
            marker.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
            marker.style.display = 'flex';
            marker.style.alignItems = 'center';
            marker.style.justifyContent = 'center';
            marker.style.fontSize = '18px';
            marker.style.cursor = 'pointer';
            marker.style.transform = 'translate(-50%, -50%)';
            marker.style.transition = 'all 0.2s ease';
            marker.style.zIndex = '10';
            marker.innerHTML = data.icon;
            marker.title = name;
            
            // 點擊圖標：原地彈卡片 + 人仔跑過來
            marker.onclick = function(e) {{
                e.stopPropagation();
                openPopup(name);
            }};
            
            container.appendChild(marker);
        }}
        
        // 打開原地彈窗函數
        function openPopup(name) {{
            const data = landmarks[name];
            const card = document.getElementById('popup-card');
            const avatar = document.getElementById('user-avatar');
            
            // 1. 讓虛擬人仔移動到該圖標坐標 (絲滑行路效果保留)
            avatar.style.left = data.x + '%';
            avatar.style.top = data.y + '%';
            
            // 2. 填充卡片內容
            document.getElementById('pop-icon').innerHTML = data.icon;
            document.getElementById('pop-title').innerHTML = name;
            document.getElementById('pop-eng').innerHTML = data.eng;
            document.getElementById('pop-desc').innerHTML = data.desc;
            document.getElementById('pop-time').innerHTML = data.time;
            document.getElementById('pop-transport').innerHTML = data.transport;
            document.getElementById('pop-tips').innerHTML = "💡 小貼士：" + data.tips;
            
            // 3. 計算彈窗原地浮現位置 (防溢出算法)
            let pLeft = data.x + 3;
            let pTop = data.y - 4;
            if (pLeft > 65) pLeft = data.x - 43; // 太右邊就彈左邊
            if (pTop < 25) pTop = data.y + 4;   // 太上面就彈下面
            
            card.style.left = pLeft + '%';
            card.style.top = pTop + '%';
            
            // 4. 顯示卡片 (零重整、超流暢)
            card.style.display = 'block';
            setTimeout(() => {{ card.style.opacity = '1'; }}, 10);
            
            // 5. 按鈕綁定底層 Streamlit 同步功能 (點擊時透過隱藏 input 通知 Python)
            document.getElementById('btn-add-itinerary').onclick = function() {{
                sendToStreamlit("add", name);
            }};
            document.getElementById('btn-stamp').onclick = function() {{
                sendToStreamlit("stamp", name);
            }};
        }}
        
        function closePopup() {{
            const card = document.getElementById('popup-card');
            card.style.opacity = '0';
            setTimeout(() => {{ card.style.display = 'none'; }}, 200);
        }}
        
        // 精準對接原本功能：將數據推回給 Streamlit 處理
        function sendToStreamlit(action, place) {{
            const inputs = window.parent.document.querySelectorAll('input');
            let actInput, plcInput;
            inputs.forEach(input => {{
                if (input.ariaLabel === "js_action") actInput = input;
                if (input.ariaLabel === "js_place") plcInput = input;
            }});
            
            if (actInput && plcInput) {{
                actInput.value = action;
                actInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                plcInput.value = place;
                plcInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}
        
        // 預設主動觸發一次海洋公園彈窗，完美對齊初始狀態
        setTimeout(() => {{ openPopup("海洋公園"); }}, 500);
    </script>

    <style>
        @keyframes bounce {{
            0%, 100% {{ transform: translateX(-50%) translateY(0); }}
            50% {{ transform: translateX(-50%) translateY(-5px); }}
        }}
        .map-marker:hover {{
            transform: translate(-50%, -50%) scale(1.25) !important;
            box-shadow: 0 0 15px #2563eb !important;
            border-color: #2563eb !important;
            z-index: 100 !important;
        }}
    </style>
    """

    # 渲染全新升級的自訂畫布
    st.components.v1.html(map_html, height=830, scrolling=False)
# ==========================================
# ✈️ Tab 2: 智能行程功能（已完美修復高德純文字行程規劃）
# ==========================================
with tab2:
    st.header("✈️ 建立你的窮遊行程")
    
    with st.expander("🔗 載入分享代碼 / 還原行程", expanded=False):
        share_code_input = st.text_area("貼上行程 JSON 代碼", height=100)
        if st.button("確認還原"):
            try:
                st.session_state.itinerary = json.loads(share_code_input)
                st.success("✅ 行程已成功還原！")
                st.rerun()
            except:
                st.error("❌ 代碼格式錯誤")
                
    st.markdown("---")
    st.subheader("步驟 1：選擇旅行天數")
    current_days = len(st.session_state.itinerary.keys())
    days = st.slider("旅行天數", 1, 7, max(3, current_days))
    if st.button("設定/重置天數"):
        st.session_state.itinerary = {f"Day {d}": st.session_state.itinerary.get(f"Day {d}", []) for d in range(1, days + 1)}
        st.success(f"已設定為 {days} 天行程！")
        st.rerun()
        
    st.markdown("---")
    st.subheader("步驟 2 & 3：編排每日行程與時間")
    if st.session_state.itinerary:
        selected_day = st.selectbox("選擇要編輯的日子", options=list(st.session_state.itinerary.keys()))
        
        col_name, col_btn = st.columns([3, 1])
        with col_name:
            custom_place = st.text_input("輸入自訂景點名稱（例如：深水埗地鐵站）")
        with col_btn:
            st.write("")
            if st.button("手動加入", use_container_width=True):
                if custom_place:
                    st.session_state.itinerary[selected_day].append({"name": custom_place, "time": "12:00"})
                    st.success(f"已加入 {custom_place}")
                    st.rerun()
                    
        current_spots = st.session_state.itinerary.get(selected_day, [])
        if current_spots:
            st.write(f"#### 🕒 調整 {selected_day} 的時間安排：")
            updated_spots = []
            for idx, spot in enumerate(current_spots):
                col_t, col_n, col_del = st.columns([2, 4, 1])
                with col_t:
                    t_obj = datetime.strptime(spot["time"], "%H:%M").time()
                    new_time = st.time_input(f"時間", value=t_obj, key=f"t_{selected_day}_{idx}", label_visibility="collapsed")
                with col_n:
                    st.markdown(f"<div style='padding-top:5px;'><b>{spot['name']}</b></div>", unsafe_allow_html=True)
                with col_del:
                    if st.button("❌", key=f"del_{selected_day}_{idx}"):
                        current_spots.pop(idx)
                        st.session_state.itinerary[selected_day] = current_spots
                        st.rerun()
                updated_spots.append({"name": spot["name"], "time": new_time.strftime("%H:%M")})
            updated_spots.sort(key=lambda x: x["time"])
            st.session_state.itinerary[selected_day] = updated_spots
        else:
            st.info("這一天目前還沒有安排景點")
            
    st.markdown("---")
    st.subheader("🗺️ 🗺️ 🗺️ 一鍵地圖多站導航 🗺️ 🗺️ 🗺️")
    
    # 📌 智能離島中轉站導航 URL 生成與識別邏輯
    def generate_maps_urls(spots_list):
        if len(spots_list) < 2:
            return None, None, []
        
        processed_names = []
        tips = []
        
        # 逐個檢查景點，遇到跨海離島時自動在中間插入對應碼頭
        for i, spot in enumerate(spots_list):
            name = spot["name"]
            
            # 🔥 智能插針：若要去長洲，且前一個點不在長洲，自動安插「中環5號碼頭」
            if i > 0 and "長洲" in name and not ("長洲" in spots_list[i-1]["name"]):
                if "中環5號碼頭" not in processed_names:
                    processed_names.append("中環5號碼頭")
                    tips.append("🚢 **智能導航優化**：偵測到跨海前往長洲！系統已自動為您在導航中安插 **中環 5 號碼頭** 作為搭船中轉站。")
            
            # 💡 額外擴充：若要去坪洲，自動安插「中環6號碼頭」
            if i > 0 and "坪洲" in name and not ("坪洲" in spots_list[i-1]["name"]):
                if "中環6號碼頭" not in processed_names:
                    processed_names.append("中環6號碼頭")
                    tips.append("🚢 **智能導航優化**：偵測到跨海前往坪洲！系統已自動為您在導航中安插 **中環 6 號碼頭** 作為搭船中轉站。")
                    
            # 💡 額外擴充：若要去南丫島，自動安插「中環4號碼頭」
            if i > 0 and "南丫島" in name and not ("南丫島" in spots_list[i-1]["name"]):
                if "中環4號碼頭" not in processed_names:
                    processed_names.append("中環4號碼頭")
                    tips.append("🚢 **智能導航優化**：偵測到跨海前往南丫島！系統已自動為您在導航中安插 **中環 4 號碼頭** 作為搭船中轉站。")
            
            processed_names.append(name)
            
        origin = processed_names[0]
        destination = processed_names[-1]
        waypoints = processed_names[1:-1]
        
        # 1. Google Maps 多站導航網址（完全支持純文字多起訖點、中途站搜尋）
        g_url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}&waypoints={urllib.parse.quote('|'.join(waypoints))}&travelmode=transit"
        
        # 2. 🎯 修正後的高德地圖網址：
        # 改用大眾 H5 端路由協議（from[name]=xxx&to[name]=yyy）強制促使高德進行純文字語義搜尋。
        # 備註：因高德公開的外部網頁連結在「純文字模式」下無法同時解析多個 via 途經點，此處自動建立「出發站 ➔ 終點站」的直達行程，並透過下方 Tips 告知用戶。
        a_url = f"https://www.amap.com/dir?from[name]={urllib.parse.quote(origin)}&to[name]={urllib.parse.quote(destination)}"
        
        # 保留原有的大澳小常識提示
        names_str = "".join([s["name"] for s in spots_list])
        if "大澳" in names_str:
            tips.append("🚌 **大澳地道貼士**：如不坐船，亦可於東涌站巴士總站搭乘大嶼山巴士 11 號直達大澳。")
            
        # 增加高德純文字多站限制的貼心提示
        tips.append("🇨🇳 **高德地圖提示**：由於高德外部網頁不支援「純文字多站插針」，已自動為您載入 **起點 ➔ 終點** 的直達路線規劃。若需沿途多站精確導航，建議優先選用左側 **Google Maps** 連結。")
            
        return g_url, a_url, tips

    # 📌 循環顯示每天的行程與一鍵導航按鈕
    for day, spots in st.session_state.itinerary.items():
        st.markdown(f"#### 📅 {day} 導航與清單")
        if spots:
            gmaps_link, amap_link, transit_tips = generate_maps_urls(spots)
            if gmaps_link and amap_link:
                col_map1, col_map2 = st.columns(2)
                with col_map1: 
                    st.link_button(f"🗺️ Google Maps 一鍵導航 ({day})", gmaps_link, use_container_width=True, type="primary")
                with col_map2: 
                    st.link_button(f"🇨🇳 高德地圖 一鍵導航 ({day})", amap_link, use_container_width=True, type="secondary")
                
                # 觸發智能交通提示（Info 方塊）
                for tip in transit_tips:
                    st.info(tip)
            else:
                st.caption(f"💡 提示：{day} 的景點數量需要大於或等於 2 個，系統先會幫你自動開啟 Google & 高德多站一鍵導航按鈕喔！")
            
            # 顯示當天時間順序表
            for spot in spots:
                t_pretty = datetime.strptime(spot["time"], "%H:%M").strftime("%I:%M %p")
                st.write(f"- **{t_pretty}** : {spot['name']}")
        else:
            st.write("*此日期目前未有編排行程*")
        st.write("")
        
    st.divider()
    st.subheader("📋 行程匯出工具")
    col_pic, col_code = st.columns(2)
    with col_pic:
        if st.button("🖼️ 截圖分享說明", use_container_width=True):
            st.info("使用 Win + Shift + S 或 Cmd + Shift + 4 進行螢幕截圖")
    with col_code:
        if st.button("🔗 生成分享代碼", use_container_width=True):
            st.code(json.dumps(st.session_state.itinerary, ensure_ascii=False, indent=2), language="json")

# ==========================================
# 👥 Tab 3: 窮遊社群與自訂人仔
# ==========================================
with tab3:
    st.header("👥 窮遊玩家社交圈子")
    tab_hot, tab_mine, tab_region = st.tabs(["🔥 熱門公共路線", "👤 我的化身與帳戶", "🌍 跨地區玩家"])
    
    with tab_hot:
        st.subheader("🔥 全球熱門路線推薦")
        hot_routes = [
            {
                "user": "KOL_香港旅遊", "title": "5日4夜香港離島深度遊", "desc": "長洲 + 大澳 + 坪洲", "days": 5,
                "slots": {"Day 1": [{"name": "長洲大魚蛋", "time": "12:00"}], "Day 2": [{"name": "大澳漁村棚屋", "time": "11:00"}]}
            }
        ]
        for route in hot_routes:
            st.markdown(f"**{route['title']}** (by {route['user']})")
            st.write(route['desc'])
            if st.button("➕ 一鍵導入行程", key=f"add_{route['title']}", type="primary"):
                st.session_state.itinerary = route["slots"].copy()
                st.session_state.trip_completed = True
                st.success("🎉 成功匯入路線！請前往「✈️ 智能行程」查看。")
                st.rerun()
            st.divider()
            
    with tab_mine:
        st.subheader("👤 設定你的專專屬虛擬人仔 (Avatar)")
        
        col_avatar1, col_avatar2 = st.columns([2, 1])
        with col_avatar1:
            current_nickname = st.text_input("設定你的窮遊暱稱", value=st.session_state.user_profile["nickname"])
            style_sel = st.selectbox("挑選人仔風格", ["冒險家 (Adventurer)", "機械人 (Bottts)", "像素風 (Pixel Art)"])
            style_map = {"冒險家 (Adventurer)": "adventurer", "機械人 (Bottts)": "bottts", "像素風 (Pixel Art)": "pixel-art"}
            current_style = style_map[style_sel]
            
            share_loc = st.checkbox("在公眾地圖上分享我的實時位置", value=st.session_state.user_profile["is_sharing"])
            
        test_avatar_url = f"https://api.dicebear.com/7.x/{current_style}/svg?seed={urllib.parse.quote(current_nickname)}"
        
        with col_avatar2:
            st.markdown("<div style='text-align: center; font-weight: bold;'>人仔預覽</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><img src='{test_avatar_url}' style='width:110px; height:110px; border-radius:50%; border:3px solid #3b82f6; background:#f0f2f6; padding:5px;'></div>", unsafe_allow_html=True)
            
        if st.button("儲存並點亮地圖人仔", use_container_width=True, type="primary"):
            st.session_state.user_profile["nickname"] = current_nickname
            st.session_state.user_profile["avatar_style"] = current_style
            st.session_state.user_profile["is_sharing"] = share_loc
            
            if location and location.get('latitude'):
                st.session_state.user_profile["lat"] = location['latitude']
                st.session_state.user_profile["lng"] = location['longitude']
                
            st.success("🎉 人仔儲存成功！快去「🗺️ 實時社交地圖」看看自己吧！")
            st.rerun()

    with tab_region:
        st.subheader("🌍 挑選其他地區分流")
        st.selectbox("切換伺服器圈子", ["香港", "東京", "台北"])
        st.info("Demo 階段暫不開放跨區社交串流。")

# ==========================================
# 🧾 Tab 4: 清單與打卡圖鑑
# ==========================================
with tab4:
    st.header("🧾 旅遊清單與小貼士")
    
    st.markdown("""
        <style>
        .custom-card { background-color: #ffffff; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eef2f6; }
        .tips-card { background-color: #e8f4fd; padding: 20px; border-radius: 16px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
        .stamp-badge { background: linear-gradient(135deg, #fffaf0, #fff8f0); border: 2px dashed #d4a017; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)
    
    t_p, t_d, t_s = st.tabs(["🧳 行李清單", "👜 隨身備忘", "🏆 尋寶打卡進度"])
    
    with t_p:
        st.subheader("🧳 出發前行李大檢查")
        tot = len(st.session_state.packing_list)
        chk = sum(1 for i in range(tot) if st.session_state.get(f"p_chk_{i}", False))
        st.progress(chk / tot if tot > 0 else 0)
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.packing_list):
            st.checkbox(item, key=f"p_chk_{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with t_d:
        st.subheader("👜 每日出門隨身小物件")
        for i, item in enumerate(st.session_state.daily_list):
            st.checkbox(item, key=f"d_chk_{i}")
            
        st.markdown("""
        <div class="tips-card">
            <h4>💡 小常識</h4>
            <ul>
                <li>香港室內冷氣充足，建議攜帶薄外套。</li>
                <li>全面實施塑料袋徵費（每個最低 $1），建議自備購物袋。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with t_s:
        st.subheader("🏆 手繪尋寶打卡圖鑑")
        collected = len(st.session_state.stamp_collection)
        st.progress(min(collected / 10, 1.0))
        st.write(f"目前已點亮 **{collected}** 個手繪寶藏地標")
        
        if collected > 0:
            cols = st.columns(2)
            for i, item in enumerate(st.session_state.stamp_collection):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="stamp-badge">
                        <span style="font-size: 2rem;">📍</span>
                        <h4 style="margin:5px 0; color:#a82c35;">{item['name']}</h4>
                        <small style='color:#777;'>解鎖時間：{item['time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("快到地圖頁面點擊【📍 蓋章打卡】來收集獎勵吧！")

# ==========================================
# ℹ️ Tab 5: 關於 / 城市切換功能
# ==========================================
with tab5:
    st.header("ℹ️ 關於 Un-Tourist 平台")
    
    region_data = {
        "香港": {
            "title": "香港・東方之珠", "banner_color": "linear-gradient(135deg, #1f4068, #162447)",
            "lang": "粵語、英語、普通話", "currency": "港幣 (HKD)", "emergency": "999",
            "warnings": ["禁煙區違例定額罰款 $1,500。", "嚴禁攜帶電子煙或加熱煙入境。"]
        },
        "新加坡": {
            "title": "新加坡・獅城活力", "banner_color": "linear-gradient(135deg, #a82c35, #6c1a20)",
            "lang": "英語、馬來語、華語", "currency": "新加坡元 (SGD)", "emergency": "995",
            "warnings": ["嚴禁攜帶口香糖入境販售。", "地鐵站內及車廂內嚴禁任何飲食。"]
        }
    }
    
    if "current_region" not in st.session_state:
        st.session_state.current_region = "香港"
        
    @st.dialog("🌐 更改探索城市")
    def change_region_dialog():
        st.write("請选择您想切換的旅遊大本營：")
        chosen = st.selectbox("城市選單", options=list(region_data.keys()))
        if st.button("儲存並變更"):
            st.session_state.current_region = chosen
            st.rerun()
            
    info = region_data[st.session_state.current_region]
    
    st.markdown(f"""
    <div style='background: {info['banner_color']}; padding: 35px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0;'>{info['title']}</h2>
        <p style='margin: 5px 0 0 0; opacity: 0.8;'>CCMF 專案概念驗證環境</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🌐 切換目的地城市 (當前：{st.session_state.current_region})", use_container_width=True):
        change_region_dialog()
        
    st.markdown("### 📋 當前都市政策法規速覽")
    st.write(f"- **🗣️ 語言**: {info['lang']}")
    st.write(f"- **💰 貨幣單位**: {info['currency']}")
    st.write(f"- **🚨 緊急求助**: {info['emergency']}")
    st.error("💡 旅人安全警示：")
    for w in info['warnings']:
        st.write(f"- {w}")
