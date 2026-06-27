import base64
import json
import urllib.parse
from datetime import datetime, time

import streamlit as st

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
# 🗺️ 圖片物資載入
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

st.title("🌏 Un-Tourist 地道窮遊導航平台 - Demo")
st.subheader("CCMF Funding Demo | 2026")

# ==================== 全局 Session State 初始化 ====================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = {
        "Day 1": [],
        "Day 2": [],
        "Day 3": []
    }

if "stamp_collection" not in st.session_state:
    st.session_state.stamp_collection = []

if "packing_list" not in st.session_state:
    st.session_state.packing_list = ["護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡", "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）", "洗漱用品", "藥物（常備藥）", "雨傘 / 摺傘"]

if "daily_list" not in st.session_state:
    st.session_state.daily_list = ["手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡", "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"]

if "budget_spent" not in st.session_state:
    st.session_state.budget_spent = 0.0

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "nickname": "未命名窮遊俠",
        "avatar_style": "adventurer",
        "lat": 22.3193,
        "lng": 114.1694,
        "is_sharing": False
    }

# 建立 5 大核心功能 Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 實時社交地圖", "✈️ 智能行程", "👥 窮遊社群", "🧾 清單小貼士", "ℹ️ 關於平台"])

# ==========================================
# 🗺️ Tab 1: 實時尋寶地圖
# ==========================================
with tab1:
    st.header("🗺️ 手繪風動態尋寶地圖")
    st.write("直接點擊地圖上的自訂圖標，即可在原地彈出詳細攻略卡片，與行程、打卡功能完美連動！")

    LANDMARKS = {
        "大澳漁村": {
            "x": 13, "y": 66, "category": "自然", "map_icon": "🛶", "card_icon": "🛶", "eng": "Tai O Fishing Village",
            "time": "全天開放 (店舖多營業 10:00-18:00)", "transport": "🚌 於東涌站乘搭 11 號巴士",
            "tips": "建議坐舢舨小艇尋找白海豚，回程試試大澳沙翁！",
            "desc": "參觀香港獨特的水上棚屋，感受遠離繁囂的傳統漁村風情。"
        },
        "天壇大佛": {
            "x": 24, "y": 50, "category": "文化",
            "map_icon": BIG_BUDDHA_SRC,
            "card_icon": BIG_BUDDHA_SRC,
            "eng": "Big Buddha",
            "time": "10:00-17:30", "transport": "🚡 昂坪360纜車 / 23號巴士",
            "tips": "需要挑戰 268 級石階，參觀前記得準備好腳力！",
            "desc": "全球最高的戶外青銅坐佛，巍峨肅穆，是洗滌心靈的文化勝地。"
        },
        "海洋公園": {
            "x": 68, "y": 78, "category": "美食", "map_icon": "🐼", "card_icon": "🐼", "eng": "Ocean Park",
            "time": "10:00-19:00 (週末至20:00)", "transport": "🚇 地鐵海洋公園站",
            "tips": "建議購買網上優惠票，避開週末人潮",
            "desc": "世界級主題公園，擁有大熊貓、海洋生物及機動遊戲。"
        },
        "西貢市中心": {
            "x": 84, "y": 25, "category": "自然", "map_icon": "⚓", "card_icon": "⚓", "eng": "Sai Kung Town",
            "time": "全天開放 (海鮮街多營業至 22:00)", "transport": "🚌 彩虹站乘 1A 綠色小巴",
            "tips": "可以在碼頭直接租街渡前往半月灣或橋咀島玩水！",
            "desc": "香港後花園，擁有風光如畫的海景與新鮮生猛的避風塘海鮮街。"
        },
        "黃大仙廟": {
            "x": 68, "y": 29, "category": "文化", "map_icon": "🙏", "card_icon": "🙏", "eng": "Wong Tai Sin Temple",
            "time": "07:30-16:30", "transport": "🚇 觀塘綫 · 黃大仙站 B2 出口",
            "tips": "廟宇內香火鼎盛，求籤非常靈驗，記得保持誠心。",
            "desc": "香港著名祠廟，建築金碧輝煌，崇奉儒、釋、道三教，有求必應。"
        },
        "九龍半島": {
            "x": 67, "y": 55, "category": "購物", "map_icon": "🛍️", "card_icon": "🛍️", "eng": "Kowloon Peninsula",
            "time": "11:00-23:00", "transport": "🚇 荃灣綫/觀塘綫 · 旺角站 E2 出口",
            "tips": "漫步女人街與波鞋街，感受地道香港霓虹夜景。",
            "desc": "香港最熱鬧的街區之一，充滿地道霓虹氣息與各式特色小攤檔。"
        },
        "長洲": {
            "x": 30, "y": 80, "category": "美食", "map_icon": "🍢", "card_icon": "🍢", "eng": "Cheung Chau Island",
            "time": "渡輪全天候運營", "transport": "🚢 中環 5 號碼頭乘搭渡輪直達",
            "tips": "必食塊頭超大的巨型咖哩魚蛋、糯米糍與香脆炸鮮奶！",
            "desc": "充滿活力的小島，行山、睇日落、踩單車，仲可以參觀張保仔洞。"
        },
        "南丫島": {
            "x": 46, "y": 91, "category": "自然", "map_icon": "🐟", "card_icon": "🐟", "eng": "Lamma Island",
            "time": "渡輪全天候運營", "transport": "🚢 中環 4 號碼頭乘搭渡輪直達",
            "tips": "感受索罟灣漁村風情，享受悠閒嘅海鮮與行山之旅。",
            "desc": "充滿異國風情與中西交融的小島，島上步伐悠閒，海鮮十分出名。"
        }
    }

    category_list = ["全部", "自然", "文化", "購物", "美食"]
    selected_cat = st.selectbox("🎯 篩選地圖景點類別", category_list)

    st.markdown("### 🛠️ 地圖快捷控制面板")
    panel_col1, panel_col2 = st.columns(2)

    with panel_col1:
        itinerary_options = list(st.session_state.itinerary.keys()) if st.session_state.itinerary else ["Day 1", "Day 2", "Day 3"]
        map_target_day = st.selectbox(
            "📅 景點同步加入哪一天？",
            options=itinerary_options,
            help="在地圖彈窗中點擊「📌 加入行程」時，景點會自動歸入此日子。"
        )
        st.session_state["current_editing_day"] = map_target_day

    with panel_col2:
        st.markdown("<div style='margin-bottom: -5px;'>💰 窮遊今日花費記帳</div>", unsafe_allow_html=True)
        sub_c1, sub_c2 = st.columns([2, 1])
        with sub_c1:
            add_expense = st.number_input("增添開支 ($)", min_value=0.0, step=10.0, key="map_expense_input", label_visibility="collapsed")
        with sub_c2:
            if st.button("記帳", use_container_width=True):
                st.session_state.budget_spent += add_expense
                st.toast(f"💵 成功記錄開支 ${add_expense}！")
        st.caption(f"📊 當前累計花費： **${st.session_state.budget_spent:.1f} HKD**")

    # 🛑 核心突破：直接利用官方安全、不佔位置的互動元件來監聽地圖點擊
    # 如果檢測到地圖有新傳入的值，立即執行行程派發！
    map_click_data = st.text_input("Map Event Data Link", value="", key="map_event_data", label_visibility="collapsed")

    if map_click_data:
        try:
            event_obj = json.loads(map_click_data)
            js_action = event_obj.get("action")
            js_place = event_obj.get("place")
            target_day = st.session_state.get("current_editing_day", "Day 1")

            if js_action == "add" and js_place:
                if target_day not in st.session_state.itinerary:
                    st.session_state.itinerary[target_day] = []
                if not any(item["name"] == js_place for item in st.session_state.itinerary[target_day]):
                    st.session_state.itinerary[target_day].append({
                        "time": "12:00",
                        "name": js_place,
                        "desc": LANDMARKS.get(js_place, {}).get("desc", "")
                    })
                    st.toast(f"📅 已將「{js_place}」同步加入 {target_day} 行程表！", icon="✅")
                else:
                    st.toast(f"👀 「{js_place}」已經喺行程表入面喇！")
            elif js_action == "stamp" and js_place:
                if not any(stamp["name"] == js_place for stamp in st.session_state.stamp_collection):
                    st.session_state.stamp_collection.append({
                        "name": js_place,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.balloons()
                    st.toast(f"🏅 打卡成功！解鎖「{js_place}」徽章！", icon="🎉")
                else:
                    st.toast(f"🐾 你之前已經收集過「{js_place}」的足跡囉！")

            # 清除以防重覆觸發
            st.session_state["map_event_data"] = ""
        except Exception as e:
            pass

    my_p = st.session_state.user_profile
    avatar_url = f"https://api.dicebear.com/7.x/{my_p.get('avatar_style', 'adventurer')}/svg?seed={urllib.parse.quote(my_p.get('nickname', '窮遊俠'))}"

    map_src = f"data:image/png;base64,{map_base64}" if map_base64 else ""
    sub_map_src = f"data:image/png;base64,{sub_base64}" if sub_base64 else ""
    js_landmarks_data = json.dumps(LANDMARKS, ensure_ascii=False)

    map_html = f"""
    <div style="position: relative; width: 100%; max-width: 800px; aspect-ratio: 1 / 1; margin: 15px auto 0 auto; overflow: visible; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
        <img src="{map_src}" style="width: 100%; height: 100%; display: block; object-fit: contain; border-radius: 16px;" />
        {f'<img src="{sub_map_src}" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: contain; z-index: 2; pointer-events: none;" />' if sub_base64 else ''}

        <div id="markers-container"></div>

        <div id="popup-card" style="
            position: absolute; width: 320px; background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(10px);
            border-radius: 24px; padding: 18px; box-shadow: 0 12px 36px rgba(15, 23, 42, 0.15);
            border: 1px solid rgba(226, 232, 240, 0.8); z-index: 9999; display: none; opacity: 0; transition: opacity 0.2s ease-in-out;
        ">
            <div onclick="closePopup()" style="position: absolute; right: 16px; top: 16px; color: #94a3b8; font-size: 14px; cursor: pointer; font-weight: bold; width: 22px; height: 22px; text-align: center; line-height: 22px; border-radius: 50%; background: #f1f5f9;">✕</div>

            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div id="pop-icon" style="font-size: 24px; background: #ffebe6; width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-right: 12px; overflow: hidden;">📍</div>
                <div style="padding-right: 20px;">
                    <h4 id="pop-title" style="margin: 0; font-size: 17px; color: #0f172a; font-weight: 700;">景點</h4>
                    <div id="pop-eng" style="font-size: 11px; color: #64748b; margin-top: 1px;">English</div>
                </div>
            </div>

            <p id="pop-desc" style="font-size: 12px; color: #475569; line-height: 1.5; margin: 0 0 12px 0;">詳細介紹...</p>

            <div style="display: flex; flex-direction: column; gap: 8px; border-top: 1px solid #f1f5f9; padding-top: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: flex-start; font-size: 12px; color: #334155;">
                    <span style="width: 20px;">🕒</span>
                    <div style="flex: 1;"><span style="color: #64748b;">營業時間：</span><span id="pop-time" style="color: #0f172a;">-</span></div>
                </div>
                <div style="display: flex; align-items: flex-start; font-size: 12px; color: #334155;">
                    <span style="width: 20px;">🚇</span>
                    <div style="flex: 1;"><span style="color: #64748b;">交通方式：</span><span id="pop-transport" style="color: #2563eb; font-weight: 500;">-</span></div>
                </div>
                <div style="display: flex; align-items: flex-start; font-size: 11px; color: #166534; background: #f0fdf4; padding: 6px 10px; border-radius: 8px; border-left: 3px solid #22c55e;">
                    <span style="width: 18px;">💡</span>
                    <div id="pop-tips" style="flex: 1;">小貼士...</div>
                </div>
            </div>

            <div style="display: flex; gap: 8px;">
                <div id="btn-add-itinerary" style="flex: 1; background: #ff4d4d; color: white; text-align: center; padding: 8px 0; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(255,77,77,0.25);">
                    📌 加入行程
                </div>
                <div id="btn-stamp" style="flex: 1; background: transparent; color: #ff4d4d; border: 1px solid #ff4d4d; text-align: center; padding: 7px 0; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer;">
                    📍 打卡
                </div>
            </div>
        </div>

        <div id="user-avatar" style="
            position: absolute; left: 50%; top: 50%; transform: translate(-50%, -100%);
            transition: left 1s cubic-bezier(0.25, 1, 0.5, 1), top 1s cubic-bezier(0.25, 1, 0.5, 1);
            z-index: 995; text-align: center; pointer-events: none;
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

        const container = document.getElementById('markers-container');
        for (let name in landmarks) {{
            const data = landmarks[name];
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
            marker.style.overflow = 'hidden';

            if (data.map_icon && data.map_icon.startsWith('data:image')) {{
                marker.innerHTML = `<img src="${{data.map_icon}}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block;">`;
            }} else {{
                marker.innerHTML = data.map_icon || '📍';
            }}

            marker.onclick = function(e) {{
                e.stopPropagation();
                openPopup(name);
            }};
            container.appendChild(marker);
        }}

        function openPopup(name) {{
            const data = landmarks[name];
            const card = document.getElementById('popup-card');
            const avatar = document.getElementById('user-avatar');

            avatar.style.left = data.x + '%';
            avatar.style.top = data.y + '%';

            const iconBox = document.getElementById('pop-icon');
            if (data.card_icon && data.card_icon.startsWith('data:image')) {{
                iconBox.innerHTML = `<img src="${{data.card_icon}}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 12px; display: block;">`;
            }} else {{
                iconBox.innerHTML = data.card_icon || '📍';
            }}

            document.getElementById('pop-title').innerHTML = name;
            document.getElementById('pop-eng').innerHTML = data.eng;
            document.getElementById('pop-desc').innerHTML = data.desc;
            document.getElementById('pop-time').innerHTML = data.time;
            document.getElementById('pop-transport').innerHTML = data.transport;
            document.getElementById('pop-tips').innerHTML = data.tips;

            let pLeft = data.x + 3;
            let pTop = data.y - 4;
            if (pLeft > 65) pLeft = data.x - 43;
            if (pTop < 25) pTop = data.y + 4;

            card.style.left = pLeft + '%';
            card.style.top = pTop + '%';
            card.style.display = 'block';
            setTimeout(() => {{ card.style.opacity = '1'; }}, 10);

            document.getElementById('btn-add-itinerary').onclick = function() {{
                sendToStreamlitNative("add", name);
            }};
            document.getElementById('btn-stamp').onclick = function() {{
                sendToStreamlitNative("stamp", name);
            }};
        }}

        function closePopup() {{
            const card = document.getElementById('popup-card');
            card.style.opacity = '0';
            setTimeout(() => {{ card.style.display = 'none'; }}, 200);
        }}

        // 🛑 頂級修復邏輯：透過原生安全通道，直接將按鈕指令發送到父頁面的 Bridge 欄位
        function sendToStreamlitNative(action, place) {{
            const payload = JSON.stringify({{ "action": action, "place": place }});
            const inputs = window.parent.document.querySelectorAll('input');
            for (let input of inputs) {{
                if (input.getAttribute('aria-label') === 'Map Event Data Link') {{
                    input.value = payload;
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    break;
                }}
            }}
        }}
    </script>
    """

    st.components.v1.html(map_html, height=850, scrolling=False)

# ==========================================
# ✈️ Tab 2: 智能行程
# ==========================================
with tab2:
    st.header("✈️ 智能行程表")
    st.write("以下是你從地圖同步或自行安排的窮遊行程：")
    for day, items in st.session_state.itinerary.items():
        st.subheader(f"📅 {day}")
        if not items:
            st.info("目前這一天還沒有安排景點，快去地圖點擊「📌 加入行程」吧！")
        else:
            for item in items:
                with st.expander(f"⏰ {item['time']} | 📍 {item['name']}"):
                    st.write(item['desc'])

# ==========================================
# 👥 Tab 3: 窮遊社群
# ==========================================
with tab3:
    st.header("👥 窮遊俠社群與個人成就")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("👤 個人檔案設定")
        st.session_state.user_profile["nickname"] = st.text_input("你的江湖綽號", value=st.session_state.user_profile["nickname"])
        st.session_state.user_profile["avatar_style"] = st.selectbox("頭像風格", ["adventurer", "bottts", "avataaars"], index=0)
    with col_p2:
        st.subheader("🏅 尋寶足跡徽章櫃")
        if not st.session_state.stamp_collection:
            st.info("你還沒有解鎖任何足跡徽章！快去地圖上「📍 打卡」吧！")
        else:
            for stamp in st.session_state.stamp_collection:
                st.success(f"🎉 已解鎖：**{stamp['name']}** (打卡時間: {stamp['time']})")

# ==========================================
# 🧾 Tab 4: 清單小貼士
# ==========================================
with tab4:
    st.header("🧾 窮遊必備物資清單")
    c_l1, c_l2 = st.columns(2)
    with c_l1:
        st.subheader("🧳 出發前行李大點兵")
        for x in st.session_state.packing_list:
            st.checkbox(x, key=f"pack_{x}")
    with c_l2:
        st.subheader("🎒 每日隨身出巡法寶")
        for y in st.session_state.daily_list:
            st.checkbox(y, key=f"daily_{y}")

# ==========================================
# ℹ️ Tab 5: 關於平台
# ==========================================
with tab5:
    st.header("ℹ️ 關於 Un-Tourist 平台")
    st.write("我們致力於為全球背包客提供最地道、最省錢、最具趣味性的互動式導航體驗。此版本為 CCMF 基金資助之完美連動 Demo 演示。")
