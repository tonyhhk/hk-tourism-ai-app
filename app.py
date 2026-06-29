from datetime import datetime, time, timedelta
import streamlit as st
import json
import urllib.parse
import base64
import random

# ==========================================
# 🌐 全域共享小隊中心 (跨 Session 數據同步 + 內建 AI 模擬器)
# ==========================================
@st.cache_resource
def get_global_team_hub():
    """
    用來儲存所有小隊的實時數據。
    結構：{ "小隊代碼": { "members": {...}, "expenses": [...], "itinerary": {...} } }
    """
    return {}

global_team_hub = get_global_team_hub()

# ==========================================
# 🛠️ 核心工具：將本地圖片轉成網頁睇得明嘅 Base64 格式
# ==========================================
def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return ""

# ==========================================
# 🗺️ 圖片物資載入 (對應地圖展示)
# ==========================================
MAP_IMAGE_NAME = "mapries地圖.png" 
map_base64 = get_base64_encoded_image(MAP_IMAGE_NAME)

try:
    big_buddha_base64 = get_base64_encoded_image("天壇大佛.jpg")
    BIG_BUDDHA_SRC = f"data:image/jpeg;base64,{big_buddha_base64}" if big_buddha_base64 else "⛰️"
except Exception:
    BIG_BUDDHA_SRC = "⛰️"

SUB_IMAGE_NAME = "sub_layer.png" 
sub_base64 = get_base64_encoded_image(SUB_IMAGE_NAME)


# ==================== 頁面基本設定 ====================
st.set_page_config(page_title="Un-Tourist 地道窮遊導航平台", page_icon="🌏", layout="wide")
st.title("🌏 Un-Tourist 地道窮遊導航平台 - Live Demo")
st.subheader("CCMF Funding Demo | 2026")

# ==================== 全局 Session State 初始化 ====================
if "selected_days" not in st.session_state:
    st.session_state.selected_days = 8  # 預設對應 image.png 顯示的 8 天 (6月9-16)
if "start_date" not in st.session_state:
    st.session_state.start_date = "2026-06-09"
if "end_date" not in st.session_state:
    st.session_state.end_date = "2026-06-16"

if "itinerary" not in st.session_state:
    st.session_state.itinerary = {}

# 💡 自動根據日曆動態天數補齊或裁剪 Day 數量
st.session_state.itinerary = {
    f"Day {i}": st.session_state.itinerary.get(f"Day {i}", []) 
    for i in range(1, st.session_state.selected_days + 1)
}

if "stamp_collection" not in st.session_state:
    st.session_state.stamp_collection = []
if "packing_list" not in st.session_state:
    st.session_state.packing_list = ["護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡", "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）", "洗漱用品", "藥物（常備藥）", "雨傘 / 摺傘"]
if "daily_list" not in st.session_state:
    st.session_state.daily_list = ["手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡", "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"]

if "budget_spent" not in st.session_state:
    st.session_state.budget_spent = 0.0

if "my_private_expenses" not in st.session_state:
    st.session_state["my_private_expenses"] = []
if "current_team" not in st.session_state:
    st.session_state["current_team"] = None

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "nickname": "本地遊俠_你",
        "avatar_style": "adventurer",  
        "lat": 22.3193,
        "lng": 114.1694,
        "x_pct": 52,  
        "y_pct": 48,
        "is_sharing": True
    }

# 🔄 【核心同步機制】如果加入了小隊，行程表直接與全域中心雙向綁定
t_code = st.session_state["current_team"]
if t_code and t_code in global_team_hub:
    if "itinerary" in global_team_hub[t_code]:
        st.session_state.itinerary = global_team_hub[t_code]["itinerary"]
    else:
        global_team_hub[t_code]["itinerary"] = st.session_state.itinerary

# 建立 5 大核心功能 Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 實時社交地圖", "✈️ 智能行程", "👥 窮遊社群", "🧾 清單小貼士", "ℹ️ 關於平台"])

# ==========================================
# 🗺️ Tab 1: 實時社交地圖
# ==========================================
with tab1:
    st.header("🗺️ 手繪風動態尋寶地圖")
    st.write("直接點擊地圖上的自訂圖標即可彈出攻略卡片，你與小隊成員的位置已實時標記在雷達上！")

    LANDMARKS = {
        "大澳漁村": {"x": 13, "y": 66, "category": "自然", "map_icon": "🛶", "card_icon": "🛶", "eng": "Tai O Fishing Village", "time": "全天開放", "transport": "🚌 東涌站乘搭 11 號巴士", "tips": "建議試試大澳大魚蛋同沙翁！", "desc": "香港獨特的水上棚屋漁村。"},
        "天壇大佛": {"x": 24, "y": 50, "category": "文化", "map_icon": BIG_BUDDHA_SRC, "card_icon": BIG_BUDDHA_SRC, "eng": "Big Buddha", "time": "10:00-17:30", "transport": "🚡 昂坪360纜車", "tips": "需要挑戰 268 級石階！", "desc": "全球最高的戶外青銅坐佛。"},
        "海洋公園": {"x": 68, "y": 78, "category": "美食", "map_icon": "🐼", "card_icon": "🐼", "eng": "Ocean Park", "time": "10:00-19:00", "transport": "🚇 地鐵海洋公園站", "tips": "避開週末人潮", "desc": "著名主題公園。"},
        "西貢市中心": {"x": 84, "y": 25, "category": "自然", "map_icon": "⚓", "card_icon": "⚓", "eng": "Sai Kung Town", "time": "全天開放", "transport": "🚌 彩虹站乘 1A 小巴", "tips": "可以去海鮮街食避風塘炒蟹！", "desc": "香港後花園與海鮮勝地。"},
        "黃大仙廟": {"x": 68, "y": 29, "category": "文化", "map_icon": "🙏", "card_icon": "🙏", "eng": "Wong Tai Sin Temple", "time": "07:30-16:30", "transport": "🚇 黃大仙站 B2 出口", "tips": "求籤非常靈驗，保持誠心。", "desc": "著名祠廟，有求必應。"},
        "九龍半島": {"x": 67, "y": 55, "category": "購物", "map_icon": "🛍️", "card_icon": "🛍️", "eng": "Kowloon", "time": "11:00-23:00", "transport": "🚇 旺角站 E2 出口", "tips": "漫步女人街，感受霓虹夜景。", "desc": "充滿地道霓虹氣息的熱鬧街區。"},
        "長洲": {"x": 30, "y": 80, "category": "美食", "map_icon": "🍢", "card_icon": "🍢", "eng": "Cheung Chau", "time": "渡輪全天候", "transport": "🚢 中環 5 號碼頭乘渡輪", "tips": "必食巨型咖哩魚蛋同糯米糍！", "desc": "充滿活力的小島。"}
    }

    selected_cat = st.selectbox("🎯 篩選地圖景點類別", ["全部", "自然", "文化", "購物", "美食"])

    st.markdown("### 🛠️ 地圖快捷控制與開支分攤")
    panel_col1, panel_col2 = st.columns(2)
    
    with panel_col1:
        itinerary_options = list(st.session_state.itinerary.keys()) if st.session_state.itinerary else ["Day 1"]
        map_target_day = st.selectbox("📅 景點同步加入哪一天？", options=itinerary_options)
        st.session_state["current_editing_day"] = map_target_day
        
    with panel_col2:
        st.markdown("<div style='margin-bottom: -5px;'>💰 窮遊隨手記帳 (公數分流自動AA版)</div>", unsafe_allow_html=True)
        sub_c1, sub_c2, sub_c3 = st.columns([2, 2, 1])
        with sub_c1:
            add_expense = st.number_input("開支金額 ($)", min_value=0.0, step=10.0, key="map_expense_input", label_visibility="collapsed")
        with sub_c2:
            expense_type = st.selectbox("支出類別", ["🔒 私人支出", "👥 小隊公數"], label_visibility="collapsed")
        with sub_c3:
            if st.button("記帳", use_container_width=True):
                if add_expense > 0:
                    new_log = {"user": st.session_state.user_profile["nickname"], "amount": add_expense, "time": datetime.now().strftime("%H:%M")}
                    if expense_type == "🔒 私人支出":
                        st.session_state["my_private_expenses"].append(new_log)
                        st.session_state.budget_spent += add_expense
                        st.toast(f"🔒 成功記錄個人開支 ${add_expense}！")
                    else:
                        t_code = st.session_state["current_team"]
                        if t_code:
                            global_team_hub[t_code]["expenses"].append(new_log)
                            st.toast(f"👥 成功記入小隊公數簿！其他電腦成員已同步知曉。")
                        else:
                            st.error("❌ 請先到【智能行程】分頁輸入代碼連動小隊！")
                            
        # 實算 AA 制分攤結果
        p_total = sum(item["amount"] for item in st.session_state["my_private_expenses"])
        pub_total = 0
        t_count = 1
        if t_code and t_code in global_team_hub:
            pub_total = sum(item["amount"] for item in global_team_hub[t_code]["expenses"])
            t_count = max(1, len(global_team_hub[t_code]["members"]))
            
        my_actual_burden = p_total + (pub_total / t_count)
        st.caption(f"📊 個人私人累計: **${p_total:.1f}** | 小隊公數池總額: **${pub_total:.1f}** ({t_count}人平分)")
        st.markdown(f"🚨 經過實時精算，我今日需負擔總額： **${my_actual_burden:.1f} HKD**")

    # 精準使用 Placeholder 定位 Map 事件，防止與日曆衝突
    map_click_data = st.text_input("Map Event Data Link", value="", key="map_event_data", placeholder="HIDDEN_MAP_INPUT", label_visibility="collapsed")
    if map_click_data:
        try:
            event_obj = json.loads(map_click_data)
            js_action = event_obj.get("action")
            js_place = event_obj.get("place")
            target_day = st.session_state.get("current_editing_day", "Day 1")
            
            if js_action == "add" and js_place:
                if target_day not in st.session_state.itinerary: st.session_state.itinerary[target_day] = []
                if not any(item["name"] == js_place for item in st.session_state.itinerary[target_day]):
                    st.session_state.itinerary[target_day].append({"time": "12:00", "name": js_place, "desc": LANDMARKS.get(js_place, {}).get("desc", "")})
                    if st.session_state["current_team"] and st.session_state["current_team"] in global_team_hub:
                        global_team_hub[st.session_state["current_team"]]["itinerary"] = st.session_state.itinerary
                    st.toast(f"📅 已將「{js_place}」同步加入 {target_day} 行程表！", icon="✅")
            elif js_action == "stamp" and js_place:
                if not any(stamp["name"] == js_place for stamp in st.session_state.stamp_collection):
                    st.session_state.stamp_collection.append({"name": js_place, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    st.balloons()
            st.session_state["map_event_data"] = ""
        except: pass

    my_p = st.session_state.user_profile
    avatar_url = f"https://api.dicebear.com/7.x/{my_p.get('avatar_style', 'adventurer')}/svg?seed={urllib.parse.quote(my_p.get('nickname', '本地遊俠_你'))}"
    map_src = f"data:image/png;base64,{map_base64}" if map_base64 else ""
    sub_map_src = f"data:image/png;base64,{sub_base64}" if sub_base64 else ""
    js_landmarks_data = json.dumps(LANDMARKS, ensure_ascii=False)
    js_team_members_data = json.dumps(global_team_hub[t_code]["members"], ensure_ascii=False) if t_code and t_code in global_team_hub else "{}"

    map_html = f"""
    <div style="position: relative; width: 100%; max-width: 800px; aspect-ratio: 1 / 1; margin: 15px auto 0 auto; overflow: visible; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); font-family: sans-serif;">
        <img src="{map_src}" style="width: 100%; height: 100%; display: block; object-fit: contain; border-radius: 16px;" />
        {f'<img src="{sub_map_src}" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: contain; z-index: 2; pointer-events: none;" />' if sub_base64 else ''}

        <div id="markers-container"></div>

        <div id="popup-card" style="
            position: absolute; width: 300px; background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 15px; box-shadow: 0 12px 36px rgba(0,0,0,0.15);
            border: 1px solid #e2e8f0; z-index: 9999; display: none; opacity: 0; transition: opacity 0.2s ease;
        ">
            <div onclick="closePopup()" style="position: absolute; right: 12px; top: 12px; color: #94a3b8; font-size: 14px; cursor: pointer; background: #f1f5f9; width: 20px; height: 20px; text-align: center; line-height: 20px; border-radius: 50%;">✕</div>
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div id="pop-icon" style="font-size: 22px; margin-right: 10px;">📍</div>
                <div>
                    <h4 id="pop-title" style="margin: 0; font-size: 16px; color: #0f172a;">景點</h4>
                    <div id="pop-eng" style="font-size: 11px; color: #64748b;">English</div>
                </div>
            </div>
            <p id="pop-desc" style="font-size: 12px; color: #475569; margin: 0 0 10px 0;">介紹...</p>
            <div style="font-size: 11px; margin-bottom: 12px; line-height: 1.4;">
                <div>🕒 營業：<span id="pop-time">-</span></div>
                <div>🚇 交通：<span id="pop-transport" style="color:#2563eb;">-</span></div>
                <div style="background:#f0fdf4; color:#166534; padding:5px; border-radius:6px; margin-top:5px;">💡 小貼士：<span id="pop-tips"></span></div>
            </div>
            <div style="display: flex; gap: 8px;">
                <div id="btn-add-itinerary" style="flex: 1; background: #ff4d4d; color: white; text-align: center; padding: 6px 0; border-radius: 15px; font-size: 12px; font-weight: bold; cursor: pointer;">📌 加入行程</div>
                <div id="btn-stamp" style="flex: 1; border: 1px solid #ff4d4d; color: #ff4d4d; text-align: center; padding: 5px 0; border-radius: 15px; font-size: 12px; font-weight: bold; cursor: pointer;">📍 現場打卡</div>
            </div>
        </div>

        <div id="user-avatar" style="position: absolute; left: {my_p.get('x_pct', 52)}%; top: {my_p.get('y_pct', 48)}%; transform: translate(-50%, -100%); z-index: 995; text-align: center; pointer-events: none;">
            <img src="{avatar_url}" style="width: 40px; height: 40px; border-radius: 50%; border: 3px solid #2563eb; background: white;" />
            <div style="background: rgba(15, 23, 42, 0.85); color: white; font-size: 9px; padding: 1px 5px; border-radius: 8px; white-space: nowrap;">{my_p.get('nickname')} (我)</div>
        </div>
    </div>

    <script>
        const landmarks = {js_landmarks_data};
        const selectedCategory = "{selected_cat}";
        const container = document.getElementById('markers-container');
        
        for (let name in landmarks) {{
            const data = landmarks[name];
            if (selectedCategory !== "全部" && data.category !== selectedCategory) continue;
            const marker = document.createElement('div');
            marker.style.position = 'absolute';
            marker.style.left = data.x + '%';
            marker.style.top = data.y + '%';
            marker.style.width = '32px'; marker.style.height = '32px'; marker.style.borderRadius = '50%';
            marker.style.backgroundColor = 'white'; marker.style.boxShadow = '0 3px 6px rgba(0,0,0,0.15)';
            marker.style.display = 'flex'; marker.style.alignItems = 'center'; marker.style.justifyContent = 'center';
            marker.style.fontSize = '16px'; marker.style.cursor = 'pointer'; marker.style.transform = 'translate(-50%, -50%)'; marker.style.zIndex = '10';
            
            if (data.map_icon && data.map_icon.startsWith('data:image')) {{
                marker.innerHTML = `<img src="${{data.map_icon}}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
            }} else {{ marker.innerHTML = data.map_icon || '📍'; }}
            
            marker.onclick = function(e) {{ e.stopPropagation(); openPopup(name); }};
            container.appendChild(marker);
        }}
        
        const teamMembers = {js_team_members_data};
        const myName = "{my_p.get('nickname')}";
        for (let mName in teamMembers) {{
            if (mName === myName) continue;
            const mInfo = teamMembers[mName];
            const tMarker = document.createElement('div');
            tMarker.style.position = 'absolute'; tMarker.style.left = mInfo.x + '%'; tMarker.style.top = mInfo.y + '%';
            tMarker.style.transform = 'translate(-50%, -50%)'; tMarker.style.zIndex = '990';
            tMarker.innerHTML = `
                <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=${{encodeURIComponent(mName)}}" style="width:34px; height:34px; border-radius:50%; border:3px solid #10b981; background:white;" />
                <div style="background: rgba(16, 185, 129, 0.95); color: white; font-size: 8px; padding: 1px 4px; border-radius: 6px; white-space: nowrap; font-weight:bold; text-align:center;">${{mName}}</div>
            `;
            container.appendChild(tMarker);
        }}
        
        function openPopup(name) {{
            const data = landmarks[name];
            const card = document.getElementById('popup-card');
            const avatar = document.getElementById('user-avatar');
            avatar.style.left = data.x + '%'; avatar.style.top = data.y + '%';
            
            document.getElementById('pop-title').innerHTML = name;
            document.getElementById('pop-eng').innerHTML = data.eng;
            document.getElementById('pop-desc').innerHTML = data.desc;
            document.getElementById('pop-time').innerHTML = data.time;
            document.getElementById('pop-transport').innerHTML = data.transport;
            document.getElementById('pop-tips').innerHTML = data.tips;
            
            card.style.left = (data.x > 60 ? data.x - 40 : data.x + 3) + '%';
            card.style.top = (data.y > 60 ? data.y - 30 : data.y + 3) + '%';
            card.style.display = 'block'; setTimeout(() => {{ card.style.opacity = '1'; }}, 10);
            
            document.getElementById('btn-add-itinerary').onclick = function() {{ sendToStreamlitNative("add", name); }};
            document.getElementById('btn-stamp').onclick = function() {{ sendToStreamlitNative("stamp", name); }};
        }}
        
        function closePopup() {{ document.getElementById('popup-card').style.display = 'none'; }}
        
        function sendToStreamlitNative(action, place) {{
            const payload = JSON.stringify({{ "action": action, "place": place }});
            let targetInput = window.parent.document.querySelector('input[placeholder="HIDDEN_MAP_INPUT"]');
            if (targetInput) {{
                targetInput.value = payload; targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}
    </script>
    """
    st.components.v1.html(map_html, height=820, scrolling=False)


# ==========================================
# ✈️ Tab 2: 智能行程功能 
# ==========================================
with tab2:
    st.header("✈️ 建立你的窮遊行程")
    
    st.markdown("### 👥 行程多站式小隊動態連動中心")
    col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
    with col_t1:
        team_code_input = st.text_input("🔑 設定或輸入小隊代碼 (試用體驗推薦輸入: TEAM-HK2026)", value=st.session_state["current_team"] or "")
    with col_t2:
        st.write("")
        if st.button("🚀 連動雲端小隊", use_container_width=True):
            if team_code_input:
                st.session_state["current_team"] = team_code_input
                if team_code_input not in global_team_hub:
                    global_team_hub[team_code_input] = {
                        "members": {
                            "🤖 窮遊大師_阿強": {"x": 13, "y": 66, "last_seen": "正在大澳買沙翁"},
                            "🤖 平遊少女_Wing": {"x": 68, "y": 29, "last_seen": "正在黃大仙廟求籤"}
                        },
                        "expenses": [
                            {"user": "🤖 窮遊大師_阿強", "amount": 160.0, "time": "10:15"},
                            {"user": "🤖 平遊少女_Wing", "amount": 95.0, "time": "11:42"}
                        ],
                        "itinerary": st.session_state.itinerary
                    }
                global_team_hub[team_code_input]["members"][st.session_state.user_profile["nickname"]] = {
                    "x": st.session_state.user_profile["x_pct"], "y": st.session_state.user_profile["y_pct"], "last_seen": datetime.now().strftime("%H:%M:%S")
                }
                st.success(f"🎉 成功連動！")
                st.rerun()
    with col_t3:
        st.write("")
        if st.button("🚪 退出小隊", use_container_width=True):
            t_code = st.session_state["current_team"]
            if t_code and t_code in global_team_hub:
                global_team_hub[t_code]["members"].pop(st.session_state.user_profile["nickname"], None)
            st.session_state["current_team"] = None
            st.rerun()

    # --- 🗺️ 【步驟 1 升級】 高顏值全自動日曆選擇模式 (對照 image.png 完美還原) ---
    st.markdown("---")
    st.markdown("### 🗓️ 步驟 1：選擇旅行日期範圍")
    st.write("點擊日曆中的**出發日子**與**回程日子**，系統會自動幫你精算並同步開拓旅遊行程天數：")

    # 接收日曆數據的專用 Input，利用 Placeholder 防衝突
    cal_click_data = st.text_input("Calendar Data Receiver", value="", key="cal_event_data", placeholder="HIDDEN_CALENDAR_INPUT", label_visibility="collapsed")
    if cal_click_data:
        try:
            cal_obj = json.loads(cal_click_data)
            s_date = cal_obj.get("start")
            e_date = cal_obj.get("end")
            days = cal_obj.get("days")
            if days and days > 0:
                st.session_state.selected_days = days
                st.session_state.start_date = s_date
                st.session_state.end_date = e_date
                # 重新動態同步行程天數
                st.session_state.itinerary = {
                    f"Day {i}": st.session_state.itinerary.get(f"Day {i}", []) 
                    for i in range(1, days + 1)
                }
                if st.session_state["current_team"] and st.session_state["current_team"] in global_team_hub:
                    global_team_hub[st.session_state["current_team"]]["itinerary"] = st.session_state.itinerary
                st.toast(f"🗓️ 成功設定日期：{s_date} 至 {e_date} (共 {days} 天)！", icon="📅")
                st.rerun()
        except: pass

    # 建立嵌入式 UI (高度模擬手機 App 的柔和色調與連貫範圍選取外觀)
    current_start = st.session_state.start_date
    current_end = st.session_state.end_date

    calendar_html = f"""
    <div style="width: 100%; max-width: 412px; margin: 0 auto; background: linear-gradient(180deg, #fff1f0 0%, #ffffff 100%); border-radius: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; overflow: hidden; padding-bottom: 20px;">
        
        <!-- 頂部標題 -->
        <div style="padding: 24px 24px 10px 24px;">
            <div style="width: 32px; height: 32px; background: rgba(0,0,0,0.04); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; margin-bottom: 16px;">
                <span style="font-weight: bold; color: #333; font-size: 14px;">←</span>
            </div>
            <h2 style="margin: 0; font-size: 28px; font-weight: 700; color: #1e293b; letter-spacing: -0.5px;">選擇日期</h2>
        </div>

        <!-- 滾動日曆本體 -->
        <div style="padding: 10px 20px; max-height: 480px; overflow-y: auto;">
            
            <!-- 六月 2026 -->
            <div style="text-align: center; font-weight: 700; color: #2e3a59; margin: 20px 0 10px 0; font-size: 16px;">六月 2026</div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 12px; color: #a2aab8; margin-bottom: 8px; font-weight: 500;">
                <div>周日</div><div>周一</div><div>周二</div><div>周三</div><div>周四</div><div>周五</div><div>周六</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); row-gap: 8px; text-align: center;" id="june-grid">
                <!-- 空白填補 (2026年6月1日是周一，故周日空1格) -->
                <div></div>
                {"".join([f'<div class="cal-day-cell {"cal-today" if d==29 else ""}" data-date="2026-06-{d:02d}" onclick="clickDate(\'2026-06-{d:02d}\')">{d}</div>' for d in range(1, 31)])}
            </div>

            <!-- 七月 2026 -->
            <div style="text-align: center; font-weight: 700; color: #2e3a59; margin: 30px 0 10px 0; font-size: 16px;">七月 2026</div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 12px; color: #a2aab8; margin-bottom: 8px; font-weight: 500;">
                <div>周日</div><div>周一</div><div>周二</div><div>周三</div><div>周四</div><div>周五</div><div>周六</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); row-gap: 8px; text-align: center;" id="july-grid">
                <!-- 空白填補 (2026年7月1日是周三，故周日至周二空3格) -->
                <div></div><div></div><div></div>
                {"".join([f'<div class="cal-day-cell" data-date="2026-07-{d:02d}" onclick="clickDate(\'2026-07-{d:02d}\')">{d}</div>' for d in range(1, 32)])}
            </div>
        </div>

        <!-- 底部確認按鈕區 -->
        <div style="padding: 15px 24px 10px 24px; text-align: center;">
            <div id="cal-summary" style="font-size: 15px; font-weight: 600; color: #ff5a43; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; gap: 6px;">
                📅 加載中...
            </div>
            <button onclick="submitRange()" style="width: 100%; background: #ff5a43; color: white; border: none; border-radius: 25px; padding: 14px 0; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(255, 90, 67, 0.3); transition: all 0.2s;">
                繼續
            </button>
            <div style="margin-top: 12px; font-size: 14px; color: #8e9aa8; cursor: pointer; font-weight: 500;">跳過</div>
        </div>
    </div>

    <style>
        .cal-day-cell {{
            height: 40px; line-height: 40px; font-size: 14px; font-weight: 600; color: #2e3a59; cursor: pointer; position: relative; user-select: none; transition: all 0.1s ease;
        }}
        .cal-today {{
            font-weight: 900 !important; color: #000 !important;
        }}
        /* 精準還原珊瑚紅範圍選取樣式 */
        .selected-start {{
            background-color: #ff5a43 !important; color: white !important; border-top-left-radius: 20px; border-bottom-left-radius: 20px;
        }}
        .selected-end {{
            background-color: #ff5a43 !important; color: white !important; border-top-right-radius: 20px; border-bottom-right-radius: 20px;
        }}
        .selected-range {{
            background-color: rgba(255, 90, 67, 0.15) !important; color: #ff5a43 !important; border-radius: 0px;
        }}
        .cal-day-cell:hover {{
            background-color: rgba(0,0,0,0.03); border-radius: 10px;
        }}
    </style>

    <script>
        let startDate = "{current_start}";
        let endDate = "{current_end}";

        function renderSelection() {{
            const cells = document.querySelectorAll('.cal-day-cell');
            cells.forEach(cell => {{
                const dStr = cell.getAttribute('data-date');
                if (!dStr) return;
                cell.classList.remove('selected-start', 'selected-end', 'selected-range');

                if (dStr === startDate && dStr === endDate) {{
                    cell.classList.add('selected-start', 'selected-end');
                }} else if (dStr === startDate) {{
                    cell.classList.add('selected-start');
                }} else if (dStr === endDate) {{
                    cell.classList.add('selected-end');
                }} else if (startDate && endDate && dStr > startDate && dStr < endDate) {{
                    cell.classList.add('selected-range');
                }}
            }});

            // 更新底部顯示格式（例如：6月 9 - 16）
            const summary = document.getElementById('cal-summary');
            if (startDate && endDate) {{
                summary.innerHTML = `📋 預計行程：${{formatDateText(startDate)}} - ${{formatDateText(endDate)}}`;
            }} else if (startDate) {{
                summary.innerHTML = `📅已選出發：${{formatDateText(startDate)}} (請選擇回程日子)`;
            }} else {{
                summary.innerHTML = `📅 請選取起止日子`;
            }}
        }}

        function formatDateText(dateStr) {{
            const parts = dateStr.split('-');
            return `${{parseInt(parts[1])}}月 ${{parseInt(parts[2])}}`;
        }}

        function clickDate(dateStr) {{
            if (!startDate || (startDate && endDate)) {{
                startDate = dateStr;
                endDate = null;
            }} else if (startDate && !endDate) {{
                if (dateStr >= startDate) {{
                    endDate = dateStr;
                }} else {{
                    startDate = dateStr;
                }}
            }}
            renderSelection();
        }}

        function submitRange() {{
            if (!startDate || !endDate) {{
                alert("請先在日曆上選取出發與回程完整範圍！");
                return;
            }}
            const d1 = new Date(startDate);
            const d2 = new Date(endDate);
            const diffTime = Math.abs(d2 - d1);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

            const payload = JSON.stringify({{ "start": startDate, "end": endDate, "days": diffDays }});
            let targetInput = window.parent.document.querySelector('input[placeholder="HIDDEN_CALENDAR_INPUT"]');
            if (targetInput) {{
                targetInput.value = payload;
                targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}

        // 初始化渲染
        renderSelection();
    </script>
    """
    st.components.v1.html(calendar_html, height=660, scrolling=False)

    st.info(f"💡 目前日曆綁定天數：**{st.session_state.selected_days} 天** ({st.session_state.start_date} ~ {st.session_state.end_date})")

    # ==================== 步驟 2 & 3：編排每日行程 ====================
    st.markdown("---")
    st.subheader("步驟 2 & 3：編排每日行程與時間")
    if st.session_state.itinerary:
        default_idx = 0
        itinerary_keys = list(st.session_state.itinerary.keys())
        if "current_editing_day" in st.session_state and st.session_state["current_editing_day"] in itinerary_keys:
            default_idx = itinerary_keys.index(st.session_state["current_editing_day"])
            
        selected_day = st.selectbox("選擇要編輯的日子", options=itinerary_keys, index=default_idx)
        st.session_state["current_editing_day"] = selected_day
        
        col_name, col_btn = st.columns([3, 1])
        with col_name:
            custom_place = st.text_input("輸入自訂景點名稱 (例如：深水埗地鐵站)")
        with col_btn:
            st.write("")
            if st.button("手動加入", use_container_width=True):
                if custom_place:
                    st.session_state.itinerary[selected_day].append({"name": custom_place, "time": "12:00"})
                    if t_code and t_code in global_team_hub: global_team_hub[t_code]["itinerary"] = st.session_state.itinerary
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
                        if t_code and t_code in global_team_hub: global_team_hub[t_code]["itinerary"] = st.session_state.itinerary
                        st.rerun()
                updated_spots.append({"name": spot["name"], "time": new_time.strftime("%H:%M")})
            updated_spots.sort(key=lambda x: x["time"])
            st.session_state.itinerary[selected_day] = updated_spots
            if t_code and t_code in global_team_hub: global_team_hub[t_code]["itinerary"] = st.session_state.itinerary
        else:
            st.info(f"💡 {selected_day} 目前還沒有安排景點。你可以去「實時社交地圖」點擊景點並按【加入行程】！")
            
    # ==================== 步驟 4：導航連結生成 ====================
    st.markdown("---")
    st.subheader("🗺️ 步驟 4：一鍵地圖多站導航與每日排程清單")
    
    def generate_maps_urls(spots_list):
        if not spots_list: return None, None, [], []
        processed_names = ["我的位置"]
        tips = []
        for spot in spots_list:
            name = spot["name"]
            if "長洲" in name and not any("中環5號碼頭" in p for p in processed_names):
                processed_names.append("中環5號碼頭")
                tips.append("🚢 **優化導航**：偵測到跨海去長洲，已為您自動安插 **中環 5 號碼頭** 轉乘站。")
            processed_names.append(name)
            
        origin, destination = processed_names[0], processed_names[-1]
        waypoints = processed_names[1:-1]
        waypoints_str = "&waypoints=" + urllib.parse.quote("|".join(waypoints)) if waypoints else ""
        
        g_url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origin)}&destination={urllib.parse.quote(destination)}{waypoints_str}&travelmode=transit"
        a_url = f"https://uri.amap.com/navigation?from=,,{urllib.parse.quote(origin)}&to=,,{urllib.parse.quote(destination)}&mode=bus"
        return g_url, a_url, processed_names, tips

    day_spots = st.session_state.itinerary.get(st.session_state.get("current_editing_day", "Day 1"), [])
    g_url, a_url, route_stops, navigation_tips = generate_maps_urls(day_spots)
    
    if g_url:
        for tip in navigation_tips:
            st.info(tip)
        col_link1, col_link2 = st.columns(2)
        with col_link1:
            st.link_button("🗺️ 開啟 Google Maps 導航", g_url, use_container_width=True)
        with col_link2:
            st.link_button("🗺️ 開啟 高德地圖 導航", a_url, use_container_width=True)


# ==========================================
# 👥 Tab 3: 窮遊社群
# ==========================================
with tab3:
    st.header("👥 窮遊玩家社交圈子")
    tab_hot, tab_mine, tab_team_detail = st.tabs(["🔥 熱門公共路線", "👤 我的化身帳戶", "🧾 小隊即時雷達與公數"])
    
    with tab_hot:
        st.subheader("🔥 全球熱門地道平民路線")
        st.write("大數據精選全港總花費最低的窮遊神級行程：")
        st.markdown("#### 🥢 深水埗尋寶平民大牌檔流 (預算: HKD $120)")
        if st.button("✨ 複製此路線至我的行程", type="primary"):
            st.session_state.itinerary = {"Day 1": [{"name": "深水埗", "time": "11:30"}, {"name": "旺角", "time": "18:00"}]}
            if t_code and t_code in global_team_hub: global_team_hub[t_code]["itinerary"] = st.session_state.itinerary
            st.success("✅ 匯入成功！")
            
    with tab_mine:
        st.subheader("👤 修改我的虛擬頭像")
        st.session_state.user_profile["nickname"] = st.text_input("我的暱稱", value=st.session_state.user_profile["nickname"])
        if st.button("更新檔案"): st.rerun()

    # 🧾 小隊實時狀態分頁 (這裡可以完美展示模擬出來的電腦隊友數據)
    with tab_team_detail:
        t_code = st.session_state["current_team"]
        if t_code and t_code in global_team_hub:
            st.markdown(f"### 📍 小隊【{t_code}】在線成員雷達 (含 AI 模擬成員)")
            members_data = global_team_hub[t_code]["members"]
            member_list = []
            for m_name, m_info in members_data.items():
                member_list.append({
                    "旅伴暱稱": m_name,
                    "地圖手繪風坐標 (X, Y)": f"{m_info['x']}% , {m_info['y']}%",
                    "目前狀態 / 最後活動時間": m_info["last_seen"]
                })
            st.table(member_list)
            
            st.markdown("### 🧾 小隊實時公數流水帳明細")
            team_expenses = global_team_hub[t_code]["expenses"]
            if team_expenses:
                for item in team_expenses:
                    st.markdown(f"🕒 `{item['time']}` | 👤 **{item['user']}** 墊付了項目 | 💰 **${item['amount']} HKD**")
        else:
            st.info("ℹ️ 目前處於個人單兵模式。請先到「智能行程」分頁連動小隊。")

# 補足其餘基本分頁以確保 app 正常運行
# ==========================================
# 🧾 Tab 4: 清單與尋寶打卡 (內建防禦初始化機制)
# ==========================================
with tab4:
    # 🛡️ 安全防護罩：確保 session_state 變數百分之百存在 (全面修復 image_8d84d6.png 報錯)
    if "packing_checked" not in st.session_state:
        st.session_state.packing_checked = {}
    if "daily_checked" not in st.session_state:
        st.session_state.daily_checked = {}
    if "scavenger_stamps" not in st.session_state:
        st.session_state.scavenger_stamps = {
            "中環大館藝術區": False,
            "尖沙咀天星碼頭": False,
            "旺角女人街霓虹站": False,
            "廟街地道夜市": False,
            "大澳水上棚屋": False,
            "昂坪市集大佛線": False,
            "鰂魚涌怪獸大廈": False,
            "西貢海鮮街碼頭": False
        }

    st.header("🧾 智能清單工具與探索地圖冊")
    st.write("配合你的旅行進度，動態管理物資與解鎖線下隱藏打卡點。")
    
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "🧳 1. 旅行必備大清單", 
        "🎒 2. 每日隨身包清單", 
        "📱 3. 因地制宜必備 Apps", 
        "📖 4. 尋寶打卡探索手冊"
    ])
    
    # 功能 1：旅行大清單
    with sub_tab1:
        st.subheader("🧳 出發前跨境/出境大型行李檢查")
        packing_items = ["護照/簽證/身份證", "來回機票/高鐵電子票確認書", "海外信用卡/港幣現金", "萬能轉換插頭/延長線", "個人換洗衣物與禦寒衣物", "常用個人藥品", "雨傘/輕便雨衣", "隨身行動電源 (需符合民航限制)"]
        
        checked_count = 0
        cols_p = st.columns(2)
        for idx, item in enumerate(packing_items):
            key = f"pack_{item}"
            with cols_p[idx % 2]:
                is_chk = st.checkbox(item, value=st.session_state.packing_checked.get(key, False), key=key)
                st.session_state.packing_checked[key] = is_chk
                if is_chk: checked_count += 1
        
        st.markdown("<br>", unsafe_allow_html=True)
        progress_val = checked_count / len(packing_items)
        st.progress(progress_val)
        st.caption(f"📊 大型行李準備進度：**{checked_count} / {len(packing_items)}** ({int(progress_val*100)}%)")

    # 功能 2：日常清單
    with sub_tab2:
        st.subheader("🎒 每日出門隨身包包「五字訣」")
        daily_items = ["「伸」- 手機與充電線", "「手」- 八達通卡 / 錢包現金", "「紙」- 小包紙巾 / 濕紙巾", "「鑰」- 酒店房卡 / 門牌密碼", "「傘」- 防曬帽 / 摺疊雨傘"]
        
        d_checked_count = 0
        cols_d = st.columns(2)
        for idx, item in enumerate(daily_items):
            key = f"daily_{item}"
            with cols_d[idx % 2]:
                is_chk = st.checkbox(item, value=st.session_state.daily_checked.get(key, False), key=key)
                st.session_state.daily_checked[key] = is_chk
                if is_chk: d_checked_count += 1
                
        st.markdown("<br>", unsafe_allow_html=True)
        d_progress_val = d_checked_count / len(daily_items)
        st.progress(d_progress_val)
        st.caption(f"📊 今日隨身裝備檢查：**{d_checked_count} / {len(daily_items)}** ({int(d_progress_val*100)}%)")

    # 功能 3：因地制宜必備 Apps
    with sub_tab3:
        st.subheader("📱 跨城導航 · 必備智能生態 Apps 推薦")
        target_city = st.selectbox("🌐 切換當前旅遊目的地城市", ["香港特別行政區", "廣東省深圳市", "日本東京都"], key="app_city_select")
        
        apps_data = {
            "香港特別行政區": [
                {"name": "MTR Mobile", "cat": "🚇 交通地鐵", "desc": "查港鐵車費、特惠站位置、轉線月台與最快上車門指南。"},
                {"name": "OpenRice 開飯喇", "cat": "🥢 美食搜尋", "desc": "全港最齊平民飯堂、茶餐廳大牌檔食評與訂座平台。"},
                {"name": "HKeMobility 香港出行易", "cat": "🚌 公共交通", "desc": "運輸署官方 App，實時查閱新巴、城巴、小巴幾點到站。"},
                {"name": "AlipayHK / 八達通", "cat": "💰 實時支付", "desc": "搭車、搭船、便利店一碼通行，本地無現金必備。"}
            ],
            "廣東省深圳市": [
                {"name": "高德地圖 / 百度地圖", "cat": "🗺️ 精準導航", "desc": "內地自由行神級地圖，步道公車精準到秒與室內導航。"},
                {"name": "大眾點評", "cat": "🍲 吃喝玩樂", "desc": "搵深港兩地團購優惠券、地道老字號、網紅店評價必看。"},
                {"name": "美團 / 餓了麼", "cat": "🛵 外賣跑腿", "desc": "深夜喺酒店叫宵夜、叫喜茶奈雪、買藥送貨即時送達。"},
                {"name": "微信 / 支付寶（乘車碼）", "cat": "🚇 乘車支付", "desc": "內置小程序一鍵開通「深圳地鐵/公交乘車碼」，直接掃碼過閘。"}
            ],
            "日本東京都": [
                {"name": "Google Maps", "cat": "🗺️ 國際導航", "desc": "日本搵鐵路月台與步行路線、景點營業時間最準確。"},
                {"name": "乘換案內 (Navitime)", "cat": "🚄 鐵路轉乘", "desc": "東京複雜地鐵網救星，車資、最快轉乘、班次延誤完美對接。"},
                {"name": "PayPay", "cat": "💰 行動支付", "desc": "日本普及率極高的電子錢包，許多小店家均支援掃碼。"},
                {"name": "Tabelog (食べログ)", "cat": "🍣 美食食評", "desc": "日本在地人嚴格篩選的高分居酒屋與隱藏美食評分工具。"}
            ]
        }
        
        st.info(f"💡 系統已為您動態切換 **{target_city}** 的專屬本地數位推薦：")
        cols = st.columns(2)
        for idx, app in enumerate(apps_data[target_city]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background:#f8fafc; border-left:4px solid #3b82f6; padding:12px; border-radius:0 8px 8px 0; margin-bottom:10px; min-height:105px;">
                    <span style="background:#dbeafe; color:#1e40af; font-size:11px; padding:2px 6px; border-radius:4px; font-weight:bold;">{app['cat']}</span>
                    <h4 style="margin:5px 0 2px 0; color:#1e293b; font-size:14px;">{app['name']}</h4>
                    <p style="margin:0; font-size:12px; color:#64748b; line-height:1.4;">{app['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

    # 功能 4：尋寶打卡探索手冊
    with sub_tab4:
        st.markdown("### 📖 香港景點尋寶探索地圖冊")
        st.caption("Scavenger Hunt Trail Map Book (對應現場 GPS / 密碼解鎖進度)")
        
        c1, c2 = st.columns([2, 1])
        with c1: 
            selected_station = st.selectbox("🎯 選擇你目前身處的線下密碼寶箱點：", list(st.session_state.scavenger_stamps.keys()), key="scavenger_select")
        with c2:
            st.write("")
            st.write("")
            if st.button("📍 現場簽到打卡 / 解鎖寶箱", use_container_width=True, key="btn_stamp_trigger"):
                st.session_state.scavenger_stamps[selected_station] = True
                st.toast(f"🎉 成功解鎖打卡點：【{selected_station}】！印章已同步至你的雲端手帳。")
                if all(st.session_state.scavenger_stamps.values()): 
                    st.balloons()
                    st.success("🏆 恭喜！你已成功解鎖全港所有尋寶打卡點，獲得「Un-Tourist 終極地道遊俠」勳章！")

        st.markdown("""
        <style>
            .stamped-y { background: #fffbeb; border: 2px dashed #d97706; padding: 12px; border-radius: 14px; text-align: center; box-shadow: 0 4px 6px -1px rgba(217, 119, 6, 0.1); }
            .stamped-n { background: #f8fafc; border: 2px solid #e2e8f0; padding: 12px; border-radius: 14px; text-align: center; opacity: 0.5; }
        </style>
        """, unsafe_allow_html=True)
        
        sc_cols = st.columns(4)
        stations_list = list(st.session_state.scavenger_stamps.items())
        
        for idx, (s_name, is_stamped) in enumerate(stations_list):
            with sc_cols[idx % 4]:
                style_class = "stamped-y" if is_stamped else "stamped-n"
                icon = "🏆" if idx == 6 else ("🔑" if idx == 0 else "📍")
                status_text = "❤️ 已蓋章解鎖" if is_stamped else "🔒 未解鎖"
                st.markdown(f"""
                <div class="{style_class}" style="margin-bottom: 15px; min-height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="font-size:24px; margin-bottom:4px;">{icon}</div>
                    <b style="font-size:12px; color:#78350f; display:block; line-height:1.2;">{s_name}</b>
                    <div style="font-size:11px; margin-top:6px; font-weight:bold; color: { '#d97706' if is_stamped else '#64748b' };">{status_text}</div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# ℹ️ Tab 5: 關於景點手帳 (全新純上下滿版排版)
# ==========================================
with tab5:
    # 1. 注入精美的卡片與滿版 Banner 樣式 CSS
    st.markdown("""
    <style>
        /* 滿版大背景 Banner */
        .top-hero-banner { 
            background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url('https://images.unsplash.com/photo-1506970845246-18f21d533b20?auto=format&fit=crop&w=1200&q=80'); 
            background-size: cover; 
            background-position: center; 
            height: 240px; 
            border-radius: 16px; 
            color: white; 
            display: flex; 
            flex-direction: column; 
            justify-content: flex-end; 
            padding: 24px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* 基礎資訊網格排版 (滿版下更寬敞) */
        .info-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 16px; 
            margin-top: 15px; 
        }
        .info-item { 
            background: #f8fafc; 
            padding: 14px; 
            border-radius: 10px; 
            border: 1px solid #e2e8f0; 
        }
        .info-label { 
            color: #94a3b8; 
            font-size: 11px; 
            margin-bottom: 4px; 
        }
        .info-value { 
            color: #1e293b; 
            font-size: 15px; 
            font-weight: bold; 
        }
        
        /* 白底通用滿版卡片外觀 */
        .white-card-full { 
            background: white; 
            border-radius: 16px; 
            padding: 24px; 
            border: 1px solid #e2e8f0; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # --- 🟢 1. 頂部：滿版地方背景主 Banner ---
    st.markdown("""
    <div class="top-hero-banner">
        <h1 style="margin:0; font-size:32px; font-weight:bold; letter-spacing:1px; text-shadow:2px 2px 6px rgba(0,0,0,0.8); color:white;">香港 · 東方之珠</h1>
        <span style="font-size:15px; opacity:0.95; font-style:italic; text-shadow:1px 1px 4px rgba(0,0,0,0.8); color:white;">Pearl of the Orient · 探索香港，留住美好時光</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 🟢 2. 中間：滿版 香港基本資訊 ---
    st.markdown("""
    <div class="white-card-full">
        <b style="color:#2563eb; font-size:18px;">🏙️ 香港基本資訊</b>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">語言</div>
                <div class="info-value">粵語、英語、普通話</div>
            </div>
            <div class="info-item">
                <div class="info-label">貨幣</div>
                <div class="info-value">港幣（HKD）</div>
            </div>
            <div class="info-item">
                <div class="info-label">時區</div>
                <div class="info-value">UTC+8（香港時間）</div>
            </div>
            <div class="info-item">
                <div class="info-label">電壓</div>
                <div class="info-value">220V / 50Hz（英式3腳）</div>
            </div>
            <div class="info-item">
                <div class="info-label">緊急電話</div>
                <div class="info-value" style="color:#dc2626;">999（警察/救護/消防）</div>
            </div>
            <div class="info-item">
                <div class="info-label">旅遊查詢</div>
                <div class="info-value">2508 1234（旅發局）</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    # --- 🟢 3. 底部：滿版 旅遊小貼士 ---
    st.markdown("""
    <div class="white-card-full">
        <b style="color:#d97706; font-size:18px;">💡 旅遊小貼士</b>
        <ul style="font-size:14px; color:#475569; padding-left:20px; margin-top:12px; line-height:1.8;">
            <li><b>八達通卡</b>：可在機場或地鐵站購買，搭車食飯一卡通行（按金 HK$50）。</li>
            <li><b>香港室內冷氣極強</b>：商場及地鐵冷氣非常充足，建議隨身帶備薄外套。</li>
            <li><b>颱風季節（5-11月）</b>：請密切留意天文台信號，若掛 8 號或以上風球大部分交通將會停運。</li>
            <li><b>香港小費文化</b>：一般餐廳結帳時通常已自動收取 10% 服務費，不需額外給小費。</li>
            <li><b>免費公廁</b>：市區內的大型商場、政府綜合大樓及港鐵站均設有免費且乾淨的公廁。</li>
            <li><b>購物免稅</b>：香港全港不設消費稅，標價即為最終售價，無需辦理退稅手續。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
