from datetime import datetime, time
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup
import json
import urllib.parse

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
# 🗺️ Tab 1: 實時社交地圖功能
# ==========================================
with tab1:
    st.header("🗺️ 手繪風實時尋寶地圖")
    st.write("探索香港隱藏景點，並喺地圖上與其他在線窮遊俠實時互動！")
    
    # 預設景點數據
    data = {
        "自然": [
            {"name": "下白泥", "coords": [22.45, 113.95], "desc": "全港最靚日落海岸。", "hours": "全日開放"},
            {"name": "石澳", "coords": [22.23, 114.25], "desc": "前後灘 + 情人橋。", "hours": "全日開放"},
            {"name": "淺水灣", "coords": [22.23, 114.20], "desc": "著名海灘，適合游泳。", "hours": "全日開放"},
        ],
        "文化": [
            {"name": "天壇大佛", "coords": [22.254, 113.905], "desc": "香港最大戶外青銅佛像。", "hours": "每日 10:00-17:30"},
            {"name": "黃大仙", "coords": [22.34, 114.19], "desc": "著名求簽廟宇。", "hours": "每日 7:00-17:30"},
        ],
        "娛樂": [
            {"name": "迪士尼樂園", "coords": [22.313, 114.043], "desc": "奇妙夢想城堡與童話世界。", "hours": "視乎官方季節"},
            {"name": "海洋公園", "coords": [22.246, 114.175], "desc": "依山而建的經典主題樂園。", "hours": "視乎官方季節"},
        ]
    }
    
    main_cat = st.selectbox("篩選景點類別", options=list(data.keys()))
    spots = data[main_cat]
    
    # 創建基礎 Folium 地圖
    m = folium.Map(location=[22.3193, 114.1694], zoom_start=11)
    
    # 1. 渲染傳統景點標記
    for spot in spots:
        popup_html = f"""
        <div style='background:white; padding:12px; border-radius:8px; min-width:200px;'>
            <b>{spot['name']}</b><br>
            {spot['desc']}<br>
            <small><b>開放時間：</b>{spot['hours']}</small>
        </div>
        """
        folium.Marker(
            location=spot["coords"],
            popup=Popup(popup_html, max_width=260),
            tooltip=spot["name"]
        ).add_to(m)
        
    # 2. 渲染其他在線用戶的虛擬人仔 (NPC/Mock Data)
    for other in st.session_state.mock_users:
        other_icon_html = f"""
        <div style='position: relative; width: 42px; height: 42px;'>
            <img src='{other['avatar']}' style='width:40px; height:40px; border-radius:50%; border:2px solid #ef4444; background:white; box-shadow: 0px 2px 6px rgba(0,0,0,0.3);'>
            <div style='position: absolute; bottom: -18px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.7); color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; white-space: nowrap;'>
                {other['nickname']}
            </div>
        </div>
        """
        folium.Marker(
            location=other["coords"],
            icon=folium.DivIcon(html=other_icon_html, icon_size=(40, 40), icon_anchor=(20, 20)),
            popup=other['nickname']
        ).add_to(m)

    # 3. 渲染用戶自己的人仔（如果開啟了位置分享）
    if st.session_state.user_profile["is_sharing"]:
        my_p = st.session_state.user_profile
        my_avatar_url = f"https://api.dicebear.com/7.x/{my_p['avatar_style']}/svg?seed={urllib.parse.quote(my_p['nickname'])}"
        
        my_icon_html = f"""
        <div style='position: relative; width: 46px; height: 46px;'>
            <img src='{my_avatar_url}' style='width:44px; height:44px; border-radius:50%; border:3px solid #3b82f6; background:white; box-shadow: 0px 2px 8px rgba(59,130,246,0.5);'>
            <div style='position: absolute; bottom: -18px; left: 50%; transform: translateX(-50%); background: #3b82f6; color: white; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; white-space: nowrap;'>
                🌟 你的位置 ({my_p['nickname']})
            </div>
        </div>
        """
        folium.Marker(
            location=[my_p["lat"], my_p["lng"]],
            icon=folium.DivIcon(html=my_icon_html, icon_size=(44, 44), icon_anchor=(22, 22)),
            popup="你目前的位置"
        ).add_to(m)

    # 顯示地圖
    st_folium(m, width="100%", height=500)
    
    st.markdown("---")
    st.subheader("📌 快速加入行程或蓋章打卡")
    
    day_options = list(st.session_state.itinerary.keys())
    selected_day = st.selectbox("選擇要加入嘅日子", options=day_options if day_options else ["Day 1"])
    
    for spot in spots:
        with st.expander(f"{spot['name']}"):
            st.write(spot['desc'])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"加入 {selected_day}", key=f"add_{main_cat}_{spot['name']}"):
                    if selected_day not in st.session_state.itinerary:
                        st.session_state.itinerary[selected_day] = []
                    
                    if any(s["name"] == spot['name'] for s in st.session_state.itinerary[selected_day]):
                        st.warning(f"「{spot['name']}」已經喺 {selected_day} 入面")
                    else:
                        st.session_state.itinerary[selected_day].append({"name": spot['name'], "time": "12:00"})
                        st.success(f"✅ 已將「{spot['name']}」加入 {selected_day}")
                        st.rerun()
            with col2:
                if st.button(f"📍 蓋章打卡", key=f"stamp_{main_cat}_{spot['name']}"):
                    if not any(s["name"] == spot['name'] for s in st.session_state.stamp_collection):
                        st.session_state.stamp_collection.append({
                            "name": spot['name'],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success(f"🎉 成功蓋章「{spot['name']}」！")
                        st.rerun()
                    else:
                        st.warning("呢個景點已經打卡過囉！")

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
