from datetime import datetime, time
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup
import json
import urllib.parse  # 💡 新增：用於 URL 安全編碼，防止中文景點變亂碼

st.set_page_config(page_title="Un-Tourist 地道窮遊導航平台", page_icon="🌏", layout="wide")
st.title("🌏 Un-Tourist 地道窮遊導航平台 - Demo")
st.subheader("CCMF Funding Demo | 2026")

# ==================== 初始化 Session State ====================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = {"Day 1": []}
if "trip_completed" not in st.session_state:
    st.session_state.trip_completed = False
if "stamp_collection" not in st.session_state:
    st.session_state.stamp_collection = []

# 建立 5 大核心功能 Tab
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 地圖", "✈️ 行程", "👥 社群", "🧾 清單", "ℹ️ 關於"])

# ==========================================
# 🗺️ Tab 1: 地圖功能
# ==========================================
with tab1:
    st.header("🗺️ 手繪風尋寶地圖")
    st.write("按類別探索香港景點，點亮專屬路線")
    
    # 景點數據
    data = {
        "自然": [
            {"name": "下白泥", "coords": [22.45, 113.95], "desc": "全港最靚日落海岸。", "hours": "全日開放"},
            {"name": "石澳", "coords": [22.23, 114.25], "desc": "前後灘 + 情人橋。", "hours": "全日開放"},
            {"name": "淺水灣", "coords": [22.23, 114.20], "desc": "著名海灘，適合游泳。", "hours": "全日開放"},
            {"name": "西貢大浪灣", "coords": [22.38, 114.27], "desc": "著名衝浪勝地。", "hours": "全日開放"},
        ],
        "文化": [
            {"name": "天壇大佛", "coords": [22.254, 113.905], "desc": "香港最大戶外青銅佛像。", "hours": "每日 10:00-17:30"},
            {"name": "黃大仙", "coords": [22.34, 114.19], "desc": "著名求簽廟宇。", "hours": "每日 7:00-17:30"},
            {"name": "南蓮園池", "coords": [22.339, 114.204], "desc": "唐代風格優美園林。", "hours": "每日 7:00-17:00"},
        ],
        "娛樂": [
            {"name": "迪士尼樂園", "coords": [22.313, 114.043], "desc": "奇妙夢想城堡與童話世界。", "hours": "視乎官方季節"},
            {"name": "海洋公園", "coords": [22.246, 114.175], "desc": "依山而建的經典主題樂園。", "hours": "視乎官方季節"},
            {"name": "昂坪360", "coords": [22.255, 113.905], "desc": "世界級觀光纜車。", "hours": "每日 10:00-18:00"},
        ]
    }
    
    main_cat = st.selectbox("選擇類別", options=list(data.keys()))
    spots = data[main_cat]
    
    # 顯示 Folium 地圖
    m = folium.Map(location=[22.3193, 114.1694], zoom_start=11)
    for spot in spots:
        popup_html = f"""
        <div style="background:white; padding:12px; border-radius:8px; min-width:200px;">
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
    st_folium(m, width="100%", height=500)
    
    st.markdown("---")
    st.subheader("將景點加入行程或打卡")
    
    day_options = list(st.session_state.itinerary.keys())
    if not day_options:
        day_options = ["Day 1"]
        st.session_state.itinerary = {"Day 1": []}
    selected_day = st.selectbox("選擇要加入嘅日子", options=day_options)
    
    for spot in spots:
        with st.expander(f"{spot['name']}"):
            st.write(spot['desc'])
            st.write(f"**開放時間**：{spot['hours']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"加入 {selected_day}", key=f"add_{main_cat}_{spot['name']}"):
                    already_added = any(
                        s["name"] == spot['name']
                        for s in st.session_state.itinerary.get(selected_day, [])
                    )
                    if already_added:
                        st.warning(f"「{spot['name']}」已經喺 {selected_day} 入面")
                    else:
                        if selected_day not in st.session_state.itinerary:
                            st.session_state.itinerary[selected_day] = []
                        st.session_state.itinerary[selected_day].append({
                            "name": spot['name'],
                            "time": "12:00"
                        })
                        st.success(f"✅ 已將「{spot['name']}」加入 {selected_day}")
            with col2:
                if st.button(f"📍 蓋章打卡", key=f"stamp_{main_cat}_{spot['name']}"):
                    already = any(s["name"] == spot['name'] for s in st.session_state.stamp_collection)
                    if not already:
                        st.session_state.stamp_collection.append({
                            "name": spot['name'],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.success(f"🎉 成功蓋章「{spot['name']}」！")
                    else:
                        st.warning("呢個景點已經打卡過")

# ==========================================
# ✈️ Tab 2: 行程功能 (串聯地圖匯出核心)
# ==========================================
with tab2:
    st.header("✈️ 建立你的窮遊行程")
    
    with st.expander("🔗 載入分享代碼 / 還原行程", expanded=False):
        share_code_input = st.text_area("貼上 JSON 分享代碼", height=100)
        if st.button("確認還原"):
            try:
                st.session_state.itinerary = json.loads(share_code_input)
                st.success("✅ 行程已成功還原！")
                st.rerun()
            except:
                st.error("❌ 分享代碼格式錯誤")
                
    st.markdown("---")
    
    # 步驟 1：選擇旅行天數
    st.subheader("步驟 1：選擇旅行天數")
    current_days = len(st.session_state.itinerary.keys())
    days = st.slider("旅行天數", 1, 7, max(3, current_days))
    if st.button("設定/重置天數"):
        new_itinerary = {f"Day {d}": st.session_state.itinerary.get(f"Day {d}", []) for d in range(1, days + 1)}
        st.session_state.itinerary = new_itinerary
        st.success(f"已成功設定 {days} 天行程！")
        st.rerun()
        
    st.markdown("---")
    
    # 步驟 2 & 3：編排每日行程與時間
    st.subheader("步驟 2 & 3：編排每日行程與時間")
    if st.session_state.itinerary:
        selected_day = st.selectbox("選擇要編輯的日子", options=list(st.session_state.itinerary.keys()))
        
        col_name, col_btn = st.columns([3, 1])
        with col_name:
            custom_place = st.text_input("輸入自訂景點名稱（例如：深水埗地鐵站、美荷樓）")
        with col_btn:
            st.write("") # 調整排版高度
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
    
    # 🎯 核心串聯優化：步驟 4：完成並匯出行程 (動態地圖跳轉邏輯)
    st.subheader("🎉 步驟 4：完成並匯出行程")
    
    # 🛠️ 定義多系統地圖 Deep Link 生成函數
    def generate_maps_urls(spots_list):
        if len(spots_list) < 2:
            return None, None
            
        # 提取經時間排序後的純景點文字清單
        names = [s["name"] for s in spots_list]
        origin = names[0]
        destination = names[-1]
        waypoints = names[1:-1]
        
        # 1. Google Maps 官方標準跨平台 Deep Link 格式
        encoded_origin = urllib.parse.quote(origin)
        encoded_destination = urllib.parse.quote(destination)
        encoded_waypoints = urllib.parse.quote("|".join(waypoints))
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={encoded_origin}&destination={encoded_destination}&waypoints={encoded_waypoints}&travelmode=transit"
        
        # 2. 高德地圖官方跨平台導航跳轉格式 (適合內地旅客環境)
        encoded_amap_dest = urllib.parse.quote(destination)
        encoded_amap_via = urllib.parse.quote(",".join(waypoints)) # 高德中途站用逗號分隔
        amap_url = f"https://uri.amap.com/navigation?to={encoded_amap_dest}&via={encoded_amap_via}&mode=bus&src=UnTourist"
        
        return gmaps_url, amap_url

    if st.button("生成完整行程清單及導航連結", type="primary", use_container_width=True):
        st.session_state.trip_completed = True
        
    if st.session_state.trip_completed:
        st.markdown("### 📋 您的最終行程表")
        
        for day, spots in st.session_state.itinerary.items():
            st.markdown(f"#### 📅 {day}")
            
            if spots:
                # 📢 動態計算並渲染該天行程的地圖跳轉按鈕
                gmaps_link, amap_link = generate_maps_urls(spots)
                
                if gmaps_link and amap_link:
                    col_map1, col_map2 = st.columns(2)
                    with col_map1:
                        st.link_button(f"🗺️ 一鍵貼上 Google Maps 導航 ({day})", gmaps_link, use_container_width=True)
                    with col_map2:
                        st.link_button(f"🇨🇳 一鍵貼上 高德地圖 導航 ({day})", amap_link, use_container_width=True)
                else:
                    st.caption("💡 提示：該天景點數量需大於或等於 2 個，方可啟用一鍵地圖導航功能。")
                
                # 印出景點時間軸
                for spot in spots:
                    t_pretty = datetime.strptime(spot["time"], "%H:%M").strftime("%I:%M %p")
                    st.write(f"- **{t_pretty}** : {spot['name']}")
            else:
                st.write("*此日期目前未有編排行程*")
            st.write("")
            
        st.divider()
        col_pic, col_code = st.columns(2)
        with col_pic:
            if st.button("🖼️ 截圖分享說明", use_container_width=True):
                st.info("使用 Win + Shift + S 或 Cmd + Shift + 4 進行屏幕截圖")
        with col_code:
            if st.button("🔗 生成分享代碼", use_container_width=True):
                st.code(json.dumps(st.session_state.itinerary, ensure_ascii=False, indent=2), language="json")

# ==========================================
# 👥 Tab 3: 社群功能
# ==========================================
with tab3:
    st.header("👥 社群")
    tab_hot, tab_mine, tab_region = st.tabs(["🔥 熱門路線", "👤 我的帳戶", "🌍 挑選地區"])
    
    with tab_hot:
        st.subheader("🔥 全球熱門路線 (用戶訂閱優先出現)")
        hot_routes = [
            {
                "user": "KOL_香港旅遊",
                "title": "5日4夜香港離島深度遊",
                "desc": "長洲 + 大澳 + 坪洲",
                "days": 5,
                "places": 5,
                "slots": {
                    "Day 1": [{"name": "長洲大魚蛋", "time": "12:00"}, {"name": "長洲張保仔洞", "time": "15:00"}],
                    "Day 2": [{"name": "大澳漁村棚屋", "time": "11:00"}, {"name": "大澳文物酒店下午茶", "time": "15:30"}],
                    "Day 3": [{"name": "坪洲秘密花園", "time": "14:00"}],
                    "Day 4": [{"name": "昂坪360纜車", "time": "10:30"}],
                    "Day 5": [{"name": "東涌小炮台", "time": "13:00"}]
                }
            },
            {
                "user": "日本自由行達人",
                "title": "東京+京都7日經典路線",
                "desc": "必去景點 + 隱藏美食",
                "days": 7,
                "places": 7,
                "slots": {
                    "Day 1": [{"name": "東京雷門淺草寺", "time": "10:00"}],
                    "Day 2": [{"name": "SHIBUYA SKY 展望台", "time": "17:30"}],
                    "Day 3": [{"name": "京都清水寺", "time": "09:00"}],
                    "Day 4": [{"name": "伏見稻荷大社", "time": "14:00"}],
                    "Day 5": [{"name": "金閣寺", "time": "11:00"}],
                    "Day 6": [{"name": "嵐山竹林小徑", "time": "15:00"}],
                    "Day 7": [{"name": "關西機場免稅店", "time": "16:00"}]
                }
            },
        ]
        for route in hot_routes:
            st.markdown(f"**{route['title']}**")
            st.caption(f"by {route['user']} · {route['days']}日")
            st.write(route['desc'])
            col1, col2, col3 = st.columns(3)
            with col1: st.button("👍 讚", key=f"like_{route['title']}")
            with col2: st.button("⭐ 收藏", key=f"save_{route['title']}")
            with col3:
                if st.button("➕ 一鍵導入行程", key=f"add_{route['title']}", type="primary"):
                    st.session_state.itinerary = route["slots"].copy()
                    st.session_state.trip_completed = True
                    st.success(f"🎉 成功匯入整條「{route['title']}」！請即前往「✈️ 行程」查看完整規劃與導航連結。")
            st.divider()
            
    with tab_mine:
        st.subheader("👤 我的帳戶")
        sub1, sub2, sub3 = st.tabs(["我分享的", "我收藏的", "我讚過的"])
        with sub1: st.info("暫無數據")
        with sub2: st.info("暫無數據")
        with sub3: st.info("暫無數據")
        
    with tab_region:
        st.subheader("🌍 挑選地區")
        region = st.selectbox("選擇地區", ["香港", "日本", "台灣"])
        st.write(f"以下係 {region} 熱門路線（Demo）")

# ==========================================
# 🧾 Tab 4: 清單與打卡圖鑑
# ==========================================
with tab4:
    if "packing_list" not in st.session_state:
        st.session_state.packing_list = ["護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡", "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）", "洗漱用品", "藥物（常備藥）", "雨傘 / 摺傘"]
    if "daily_list" not in st.session_state:
        st.session_state.daily_list = ["手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡", "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"]

    st.header("🧾 旅遊清單與小貼士")
    st.write("出發前同每日行程準備，確保旅程萬無一失")
    
    st.markdown("""
        <style>
        .custom-card { background-color: #ffffff; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eef2f6; }
        .tips-card { background-color: #e8f4fd; padding: 20px; border-radius: 16px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
        .stamp-badge { background: linear-gradient(135deg, #fffaf0, #fff8f0); border: 2px dashed #d4a017; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)
    
    tab_pack, tab_daily, tab_app, tab_stamp = st.tabs(["🧳 行李清單", "👜 日常必備", "📱 必備 Apps", "🏆 我的打卡圖鑑"])
    
    with tab_pack:
        st.subheader("🧳 出發前行李檢查")
        total = len(st.session_state.packing_list)
        checked = sum(1 for i in range(total) if st.session_state.get(f"pack_check_{i}", False))
        st.progress(checked / total if total > 0 else 0)
        st.caption(f"📊 整備進度：已完成 {checked} / {total}")
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.packing_list):
            col1, col2 = st.columns([10, 1])
            with col1: st.checkbox(item, key=f"pack_check_{i}")
            with col2:
                if st.button("❌", key=f"del_pack_{i}"):
                    st.session_state.packing_list.pop(i)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        new_item = st.text_input("➕ 新增自訂行李項目", key="new_pack")
        if st.button("加入行李清單", key="add_pack", use_container_width=True):
            if new_item:
                st.session_state.packing_list.append(new_item)
                st.rerun()
                
    with tab_daily:
        st.subheader("👜 每日出門隨身必備")
        total_d = len(st.session_state.daily_list)
        checked_d = sum(1 for i in range(total_d) if st.session_state.get(f"daily_check_{i}", False))
        st.progress(checked_d / total_d if total_d > 0 else 0)
        st.caption(f"📊 今日出門進度：已完成 {checked_d} / {total_d}")
        
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        for i, item in enumerate(st.session_state.daily_list):
            col1, col2 = st.columns([10, 1])
            with col1: st.checkbox(item, key=f"daily_check_{i}")
            with col2:
                if st.button("❌", key=f"del_daily_{i}"):
                    st.session_state.daily_list.pop(i)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="tips-card">
            <h4>💡 旅客實用小貼士</h4>
            <ul style="padding-left: 20px; color: #333333; line-height: 1.8;">
                <li><b>八達通卡</b>可在機場或地鐵站購買，押金 HK$50。</li>
                <li>香港室內<b>冷氣極強</b>，建議隨身攜帶薄外套。</li>
                <li>香港為免稅港，全港購物均<b>免消費稅</b>。</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with tab_app:
        st.subheader("📱 推薦下載官方實用 Apps")
        apps = [
            ("八達通 App", "交通乘車、便利店電子支付與餘額查詢", "💳"),
            ("Citymapper", "香港最準確的公共交通路線規劃與實時到站時間", "🚇"),
            ("OpenRice 開飯喇", "香港最強搵食搵餐廳、睇食評與訂座神器", "🍛"),
        ]
        for name, desc, app_emoji in apps:
            with st.expander(f"{app_emoji} {name}"):
                st.write(desc)
                
    with tab_stamp:
        st.subheader("🏆 香港手繪尋寶打卡圖鑑")
        total_collected = len(st.session_state.stamp_collection)
        st.progress(min(total_collected / 10, 1.0))
        st.caption(f"🎯 已解鎖 **{total_collected}** / 10 個手繪景點標記")
        
        if total_collected > 0:
            cols = st.columns(2)
            for i, item in enumerate(st.session_state.stamp_collection):
                current_col = cols[i % 2]
                with current_col:
                    st.markdown(f"""
                    <div class="stamp-badge">
                        <span style="font-size: 2.5rem;">📍</span>
                        <h4 style="margin: 5px 0; color: #a82c35;">{item['name']}</h4>
                        <small style="color: #777;">✨ 已解鎖<br>{item['time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("撤銷蓋章", key=f"del_stamp_{i}", use_container_width=True):
                        st.session_state.stamp_collection.pop(i)
                        st.rerun()
        else:
            st.info("🧭 快去「🗺️ 地圖」探索香港景點並點擊【📍 蓋章打卡】來點亮圖鑑吧！")

# ==========================================
# ℹ️ Tab 5: 關於 / 城市切換功能
# ==========================================
with tab5:
    st.header("ℹ️ 關於 Un-Tourist")
    try:
        from streamlit_geolocation import streamlit_geolocation
        col_gps, _ = st.columns([1, 4])
        with col_gps:
            st.caption("自動定位切換地區：")
            location = streamlit_geolocation()
    except:
        location = None
        
    region_data = {
        "香港": {
            "title": "香港・東方之珠", "subtitle": "Pearl of the Orient", "banner_color": "linear-gradient(135deg, #1f4068, #162447)",
            "lang": "粵語、英語、普通話", "currency": "港幣 (HKD)", "timezone": "UTC+8", "voltage": "220V (英式3腳)", "emergency": "999", "inquiry": "2508 1234",
            "michelin": "🎵 2026最新：香港街頭小食及多間中菜廳蟬聯米芝蓮三星！太安樓亦有平價美食上榜。",
            "warnings": ["禁煙區違例定額罰款 $1,500。", "嚴禁攜帶電子煙、加熱煙入境。", "攜帶生肉或蛋類入境屬違法行為。"]
        },
        "新加坡": {
            "title": "新加坡・獅城活力", "subtitle": "The Garden City", "banner_color": "linear-gradient(135deg, #a82c35, #6c1a20)",
            "lang": "英語、馬來語、華語", "currency": "新加坡元 (SGD)", "timezone": "UTC+8", "voltage": "230V (英式3腳)", "emergency": "999 / 995", "inquiry": "+65 6736 2000",
            "michelin": "🎵 2026最新：麥士威熟食中心多間傳統檔位新入選必比登推介！",
            "warnings": ["嚴禁攜帶口香糖入境販售。", "亂丟垃圾、隨地吐痰面臨高額罰款。", "地鐵站內及車廂內嚴禁飲食。"]
        }
    }
    
    default_idx = 0
    if location and location.get('latitude'):
        if 1.0 <= location['latitude'] <= 1.5:
            default_idx = 1
            
    if "current_region" not in st.session_state:
        st.session_state.current_region = list(region_data.keys())[default_idx]
        
    @st.dialog("🌐 更改探索地區 / 查看地球儀")
    def change_region_dialog():
        st.write("請選擇您想查看的旅遊城市：")
        chosen = st.selectbox("地區選擇", options=list(region_data.keys()), index=list(region_data.keys()).index(st.session_state.current_region))
        st.info("🔮 提示：未來版本此處將會展示 3D 旋轉地球儀！")
        if st.button("確認切換", use_container_width=True):
            st.session_state.current_region = chosen
            st.rerun()
            
    current_city = st.session_state.current_region
    info = region_data[current_city]
    
    banner_html = f"""
    <div style="background: {info['banner_color']}; padding: 40px 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700;">{info['title']}</h1>
        <p style="margin: 5px 0 0 0; font-style: italic; opacity: 0.8;">{info['subtitle']}</p>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
    
    if st.button(f"🌐 更改地區 (目前：{current_city})", use_container_width=True):
        change_region_dialog()
        
    st.markdown(f"### 🧳 {current_city} 基本資訊")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**🗣️ 語言**<br>{info['lang']}", unsafe_allow_html=True)
        st.markdown(f"**🚨 緊急電話**<br><span style='color:red;'>{info['emergency']}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"**💰 貨幣**<br>{info['currency']}", unsafe_allow_html=True)
        st.markdown(f"**📞 旅遊查詢**<br>{info['inquiry']}", unsafe_allow_html=True)
        
    st.markdown("---")
    st.info(info['michelin'])
    st.warning(f"前往{current_city}前請特別注意出入境禁忌與法規：")
    for warning in info['warnings']:
        st.markdown(f"* {warning}")
