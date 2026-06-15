from datetime import datetime, time
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup
import json

st.set_page_config(page_title="HK Tourism AI App", page_icon="🌏", layout="wide")
st.title("🌏 HK Tourism AI App - Demo")
st.subheader("CCMF Funding Demo | 2026")

# ==================== 初始化 ====================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = {"Day 1": []}
if "trip_completed" not in st.session_state:
    st.session_state.trip_completed = False
if "packing_list" not in st.session_state:
    st.session_state.packing_list = [
        "護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡",
        "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）",
        "洗漱用品（牙刷、牙膏、洗面奶）", "藥物（常備藥、個人藥）", "雨傘 / 摺傘"
    ]
if "daily_list" not in st.session_state:
    st.session_state.daily_list = [
        "手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡",
        "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"
    ]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 地圖", "✈️ 行程", "👥 社群", "🧾 清單", "ℹ️ 關於"])

# ==================== 地圖 Tab (手繪插畫風格升級) ====================
with tab1:
    st.header("🗺️ 互動探索地圖")
    st.write("配合手繪尋寶風格，按類別同地區探索香港景點")

    data = {
        "自然": [
            {"name": "下白泥", "coords": [22.435, 113.945], "desc": "全港最靚日落海岸。", "hours": "全日開放", "icon": "🌅"},
            {"name": "石澳", "coords": [22.230, 114.250], "desc": "前後灘 + 情人橋。", "hours": "全日開放", "icon": "🏖️"},
            {"name": "淺水灣", "coords": [22.236, 114.197], "desc": "著名海灘，適合游泳與放鬆。", "hours": "全日開放", "icon": "🏖️"},
            {"name": "赤柱", "coords": [22.218, 114.213], "desc": "充滿歐陸風情的小鎮與市集。", "hours": "全日開放", "icon": "🎪"},
            {"name": "西貢", "coords": [22.383, 114.270], "desc": "香港後花園，海鮮與地道小船。", "hours": "全日開放", "icon": "⛵"},
            {"name": "長洲", "coords": [22.206, 114.028], "desc": "寧靜離島，必食大魚蛋同平安包。", "hours": "全日開放", "icon": "🥯"},
            {"name": "大澳漁村", "coords": [22.254, 113.862], "desc": "東方威尼斯，獨特棚屋景觀。", "hours": "全日開放", "icon": "🛶"},
            {"name": "萬宜水庫東壩", "coords": [22.375, 114.341], "desc": "1億4千萬年自然奇觀。", "hours": "全日開放", "icon": "🗿"},
        ],
        "文化": [
            {"name": "M+博物館", "coords": [22.301, 114.159], "desc": "西九文化區視覺文化博物館。", "hours": "星期三至一 10:00-18:00", "icon": "🖼️"},
            {"name": "香港故宮", "coords": [22.302, 114.155], "desc": "展示中國古代藝術珍品。", "hours": "星期三至一 10:00-18:00", "icon": "🏺"},
            {"name": "天壇大佛", "coords": [22.254, 113.905], "desc": "大嶼山昂坪著名戶外青銅大佛。", "hours": "每日 10:00-17:30", "icon": "🧘"},
            {"name": "黃大仙廟", "coords": [22.342, 114.193], "desc": "香火鼎盛的著名求籤廟宇。", "hours": "每日 7:00-17:30", "icon": "🛕"},
            {"name": "南蓮園池", "coords": [22.339, 114.204], "desc": "唐代風格的優美清幽園林。", "hours": "每日 7:00-17:00", "icon": "⛩️"},
            {"name": "廟街夜市", "coords": [22.308, 114.170], "desc": "充滿港式大牌檔與懷舊霓虹燈。", "hours": "傍晚至凌晨", "icon": "🏮"},
            {"name": "深水埗", "coords": [22.330, 114.162], "desc": "尋寶天堂，數碼產品與街頭小食。", "hours": "每日開放", "icon": "🔌"},
        ],
        "美食": [
            {"name": "太安樓", "coords": [22.282, 114.222], "desc": "西灣河地道「深夜食堂」小食街。", "hours": "每日 12:00-24:00", "icon": "🍳"},
            {"name": "元創方 (PMQ)", "coords": [22.283, 114.152], "desc": "前已婚警察宿舍改建的文創美食區。", "hours": "每日 07:00-23:00", "icon": "☕"},
            {"name": "天星小輪", "coords": [22.293, 114.168], "desc": "百年歷史渡輪，飽覽維港美景。", "hours": "每日 06:30-23:30", "icon": "⛴️"},
            {"name": "澳洲牛奶公司", "coords": [22.306, 114.171], "desc": "經典超滑炒蛋與燉奶。", "hours": "星期四至二 07:30-22:00", "icon": "🥛"},
        ],
        "娛樂": {
            "尖沙咀與維港區": [
                {"name": "尖沙咀鐘樓", "coords": [22.293, 114.169], "desc": "九廣鐵路舊車站的歷史地標。", "hours": "全日（外觀）", "icon": "🕰️"},
                {"name": "星光大道", "coords": [22.293, 114.174], "desc": "尋找巨星手印，欣賞維港天際線。", "hours": "全日開放", "icon": "⭐"},
                {"name": "香港摩天輪", "coords": [22.285, 114.162], "desc": "中環海濱摩天輪，浪漫夜景首選。", "hours": "每日 11:00-23:00", "icon": "🎡"},
                {"name": "天際100", "coords": [22.303, 114.160], "desc": "全港最高室內觀景台。", "hours": "每日 10:00-20:30", "icon": "🏙️"},
                {"name": "金紫荊廣場", "coords": [22.284, 114.174], "desc": "灣仔海濱，見證歷史的地標。", "hours": "全日開放", "icon": "🔱"},
            ],
            "旺角區": [
                {"name": "旺角女人街", "coords": [22.319, 114.170], "desc": "體驗香港最密集的地道露天市集。", "hours": "每日 11:00-23:00", "icon": "🛍️"},
            ],
            "主題樂園與其他": [
                {"name": "迪士尼樂園", "coords": [22.313, 114.043], "desc": "奇妙夢想城堡與童話世界。", "hours": "視乎官方季節", "icon": "🏰"},
                {"name": "海洋公園", "coords": [22.246, 114.175], "desc": "依山而建的經典主題樂園與大熊貓。", "hours": "視乎官方季節", "icon": "🐼"},
                {"name": "沙田馬場", "coords": [22.400, 114.205], "desc": "感受熱血沸騰的香港賽馬文化。", "hours": "賽馬日開放", "icon": "🐎"},
                {"name": "跑馬地馬場", "coords": [22.272, 114.182], "desc": "市中心夜間賽馬與 Happy Wednesday 派對。", "hours": "週三晚間", "icon": "🐎"},
            ]
        }
    }

    main_cat = st.selectbox("選擇類別", options=list(data.keys()), key="map_cat_selector")

    if main_cat == "娛樂":
        area = st.selectbox("選擇地區", options=list(data["娛樂"].keys()), key="map_area_selector")
        spots = data["娛樂"][area]
    else:
        spots = data[main_cat]

    m = folium.Map(
        location=[22.315, 114.169],
        zoom_start=11,
        tiles="CartoDB Positron",
        control_scale=True
    )

    for spot in spots:
        popup_html = f"""
        <div style="background: #fff8f0; padding: 12px; border-radius: 10px; border: 2px solid #d4a017; font-family: 'Comic Sans MS', sans-serif; min-width: 200px;">
            <b style="color:#a82c35; font-size: 1.1rem;">{spot['icon']} {spot['name']}</b><br>
            <span style="color: #555; font-size: 0.9rem;">{spot['desc']}</span><br>
            <small style="color: #999;"><b>🕰️ 開放：</b>{spot['hours']}</small>
        </div>
        """

        icon_html = f"""
        <div style="font-size: 28px; text-align: center; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); cursor: pointer;">
            {spot['icon']}
            <div style="font-size: 11px; background: rgba(255, 248, 240, 0.85); border: 1px solid #d4a017; border-radius: 4px; padding: 1px 4px; color: #333; font-weight: bold; white-space: nowrap; margin-top: -2px;">
                {spot['name']}
            </div>
        </div>
        """

        folium.Marker(
            location=spot["coords"],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(60, 60),
                icon_anchor=(30, 30)
            )
        ).add_to(m)

    st_folium(m, width="100%", height=550)

    st.markdown("---")

    day_options = list(st.session_state.itinerary.keys())
    default_day = st.selectbox("選擇要加入嘅日子", options=day_options, key="default_day_map")

    st.write(f"### 🗺️ {main_cat} 景點探索卡片")

    for i, spot in enumerate(spots):
        with st.expander(f"{spot['icon']} {spot['name']}"):
            st.markdown(f"**{spot['desc']}**")
            st.write(f"**開放時間**：{spot['hours']}")

            if "迪士尼" in spot['name']:
                st.markdown("🚇 **交通建議**：港鐵迪士尼綫直達")
            elif "大佛" in spot['name'] or "寶蓮" in spot['name']:
                st.markdown("🚠 **交通建議**：東涌站轉乘昂坪360纜車")
            elif "海洋公園" in spot['name']:
                st.markdown("🚇 **交通建議**：港鐵南港島綫海洋公園站")
            elif "M+" in spot['name'] or "故宮" in spot['name']:
                st.markdown("🚌 **交通建議**：九龍站下車步行至西九文化區")
            else:
                st.markdown("📍 **地點**：香港地道街區探索")

            st.markdown("💡 **小貼士**：仿照手繪地圖尋寶趣，非繁忙時段造訪體驗更佳！")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"加入 {default_day}", key=f"add_{main_cat}_{i}", use_container_width=True):
                    st.session_state.itinerary[default_day].append({
                        "name": spot['name'],
                        "time": "12:00"
                    })
                    st.success(f"✅ 已將「{spot['name']}」加入 {default_day}")
                    st.rerun()   # ← 已加入

            with col2:
                if st.button("📍 蓋章打卡", key=f"stamp_{main_cat}_{i}", use_container_width=True):
                    stamp_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    already = any(s["name"] == spot['name'] for s in st.session_state.stamp_collection)
                    if not already:
                        st.session_state.stamp_collection.append({
                            "name": spot['name'],
                            "time": stamp_time
                        })
                        st.success(f"🎉 成功在圖鑑中蓋章「{spot['name']}」！")
                    else:
                        st.warning("呢個景點你已經成功解鎖過囉！")
# ==================== 行程 Tab ====================
with tab2:
    st.header("✈️ 行程管理")

    with st.expander("🔗 載入分享代碼 / 還原行程", expanded=False):
        share_code_input = st.text_area("貼上 JSON 分享代碼", height=120)
        if st.button("確認還原"):
            if share_code_input:
                try:
                    st.session_state.itinerary = json.loads(share_code_input)
                    st.success("✅ 行程已成功還原！")
                    st.rerun()
                except:
                    st.error("❌ 分享代碼格式錯誤")

    st.markdown("---")
    st.subheader("步驟 1：選擇旅行天數")
    current_days = len(st.session_state.itinerary.keys())
    days = st.slider("旅行天數", 1, 7, max(3, current_days))
    if st.button("設定/重置天數"):
        new_itinerary = {f"Day {d}": st.session_state.itinerary.get(f"Day {d}", []) for d in range(1, days + 1)}
        st.session_state.itinerary = new_itinerary
        st.success(f"已成功設定 {days} 天行程！")
        st.rerun()

    st.markdown("---")
    st.subheader("步驟 2 & 3：編排每日行程與時間")

    if st.session_state.itinerary:
        selected_day = st.selectbox("選擇要編輯的日子", options=list(st.session_state.itinerary.keys()))

        col_name, col_btn = st.columns([3, 1])
        with col_name:
            custom_place = st.text_input("輸入自訂景點名稱", key="custom_place")
        with col_btn:
            if st.button("手動加入"):
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
                    st.markdown(f"<b>{spot['name']}</b>", unsafe_allow_html=True)
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
    st.subheader("步驟 4：完成並匯出行程")
    if st.button("生成完整行程清單"):
        st.session_state.trip_completed = True

    if st.session_state.trip_completed:
        st.markdown("### 📋 您的最終行程表")
        for day, spots in st.session_state.itinerary.items():
            st.markdown(f"#### 📅 {day}")
            for spot in spots:
                t_pretty = datetime.strptime(spot["time"], "%H:%M").strftime("%I:%M %p")
                st.write(f"- **{t_pretty}** : {spot['name']}")
            st.write("")

        col_pic, col_code = st.columns(2)
        with col_pic:
            if st.button("🖼️ 截圖分享說明"):
                st.info("使用 Win + Shift + S 或 Cmd + Shift + 4 進行截圖")
        with col_code:
            if st.button("🔗 生成分享代碼"):
                st.code(json.dumps(st.session_state.itinerary, ensure_ascii=False, indent=2), language="json")

# ==================== 社群 Tab ====================
with tab3:
    st.header("👥 社群")
    st.info("【CCMF 未來規劃】用戶可以一鍵公開自己的 JSON 行程至社群，其他旅客能進行點讚、收藏並直接複製行程。")

# ==================== 清單 Tab ====================
with tab4:
    st.header("🧾 清單")

    # 四個分頁
    tab_pack, tab_daily, tab_app, tab_stamp = st.tabs([
        "🧳 行李清單", 
        "👜 日常必備", 
        "📱 必備 Apps", 
        "📍 我的打卡"
    ])

    # ========== 1. 行李清單 ==========
    with tab_pack:
        st.subheader("🧳 行李清單")

        if "packing_list" not in st.session_state:
            st.session_state.packing_list = [
                "護照 / 身份證明文件", "機票 / 電子機票", "現金 + 信用卡",
                "手機 + 充電器 + 行動電源", "衣物（內衣、襪子、外套、鞋）",
                "洗漱用品", "藥物（常備藥）", "雨傘 / 摺傘"
            ]

        total = len(st.session_state.packing_list)
        checked = sum(1 for i in range(total) if st.session_state.get(f"pack_check_{i}", False))
        st.progress(checked / total if total > 0 else 0)
        st.caption(f"已完成 {checked} / {total}")

        for i, item in enumerate(st.session_state.packing_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.checkbox(item, key=f"pack_check_{i}")
            with col2:
                if st.button("❌", key=f"del_pack_{i}"):
                    st.session_state.packing_list.pop(i)
                    st.rerun()

        new_item = st.text_input("新增行李項目", key="new_pack")
        if st.button("加入行李清單", key="add_pack"):
            if new_item:
                st.session_state.packing_list.append(new_item)
                st.success(f"已加入：{new_item}")
                st.rerun()

    # ========== 2. 日常必備 ==========
    with tab_daily:
        st.subheader("👜 日常必備")

        if "daily_list" not in st.session_state:
            st.session_state.daily_list = [
                "手機 + 行動電源", "錢包 / 銀包", "八達通 / 信用卡",
                "雨傘", "紙巾 / 濕紙巾", "口罩", "充電線", "鎖匙"
            ]

        total_d = len(st.session_state.daily_list)
        checked_d = sum(1 for i in range(total_d) if st.session_state.get(f"daily_check_{i}", False))
        st.progress(checked_d / total_d if total_d > 0 else 0)
        st.caption(f"已完成 {checked_d} / {total_d}")

        for i, item in enumerate(st.session_state.daily_list):
            col1, col2 = st.columns([10, 1])
            with col1:
                st.checkbox(item, key=f"daily_check_{i}")
            with col2:
                if st.button("❌", key=f"del_daily_{i}"):
                    st.session_state.daily_list.pop(i)
                    st.rerun()

        new_daily = st.text_input("新增日常項目", key="new_daily")
        if st.button("加入日常清單", key="add_daily"):
            if new_daily:
                st.session_state.daily_list.append(new_daily)
                st.success(f"已加入：{new_daily}")
                st.rerun()

    # ========== 3. 必備 Apps ==========
    with tab_app:
        st.subheader("📱 必備 Apps")
        apps = [
            ("八達通 App", "交通、便利店、超市支付"),
            ("Klook", "門票、體驗、景點預訂"),
            ("Trip.com", "機票、酒店、火車票"),
            ("Google Maps", "地圖導航、交通資訊"),
            ("Citymapper / Moovit", "香港公共交通路線規劃"),
            ("PayMe / AlipayHK", "電子支付"),
        ]
        for name, desc in apps:
            with st.expander(f"📲 {name}"):
                st.write(desc)
        st.info("💡 建議出發前下載並登入相關 App")

          # ========== 4. 我的打卡（尋寶風格 + 卡片） ==========
    with tab_stamp:
        st.subheader("📍 香港景點尋寶進度")

        if "stamp_collection" not in st.session_state:
            st.session_state.stamp_collection = []

        total_collected = len(st.session_state.stamp_collection)

        # 進度條
        progress = min(total_collected / 10, 1.0)
        st.progress(progress)
        st.caption(f"已打卡 **{total_collected}** 個景點 ｜ 目標：10 個")

        if total_collected > 0:
            st.markdown("### 🏆 已收集景點")

            for i, item in enumerate(st.session_state.stamp_collection):
                # 簡單 emoji 對應（可之後擴充）
                emoji = "📍"
                name = item['name']
                if "天壇大佛" in name or "大佛" in name:
                    emoji = "🗿"
                elif "迪士尼" in name:
                    emoji = "🏰"
                elif "天星小輪" in name or "小輪" in name:
                    emoji = "⛴️"
                elif "鐘樓" in name:
                    emoji = "🕰️"
                elif "摩天輪" in name:
                    emoji = "🎡"
                elif "海洋公園" in name:
                    emoji = "🐬"
                elif "山頂" in name or "纜車" in name:
                    emoji = "🚠"
                elif "LKF" in name or "蘭桂坊" in name:
                    emoji = "🍸"
                elif "女人街" in name:
                    emoji = "🛍️"

                with st.container():
                    col1, col2 = st.columns([9, 2])
                    with col1:
                        st.markdown(f"### {emoji} {name}")
                        st.caption(f"打卡時間：{item['time']}")
                    with col2:
                        if st.button("刪除", key=f"del_stamp_{i}"):
                            st.session_state.stamp_collection.pop(i)
                            st.rerun()

            st.markdown("---")

            if total_collected >= 5:
                st.success("🎉 太棒了！你已經收集咗 5 個以上景點！繼續探索香港～")
            else:
                st.info("繼續去地圖打卡更多景點，解鎖更多驚喜吧！")

        else:
            st.info("你仲未有打卡記錄！\n去地圖 Tab 加入景點時可以一併打卡～")

# ==================== 關於 Tab ====================
# ==================== 關於 Tab (全新升級版) ====================
with tab5:
    st.header("ℹ️ 關於")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;">
        <h2 style="margin:0;">香港旅遊 AI App</h2>
        <p style="margin:8px 0 0 0; opacity:0.9;">探索香港，留住美好時光</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📱 項目簡介")
    st.write("""
    **HK Tourism AI App** 係一個專為來港旅客設計嘅智慧旅遊工具。
    透過互動地圖、個人化行程規劃同打卡收藏功能，幫助旅客輕鬆探索香港更多元化嘅景點，
    同時為本地中小企帶來更多客流機會。
    """)

    st.markdown("---")

    st.subheader("🇭🇰 香港基本資訊")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🗣️ 語言**<br>粵語、英語、普通話", unsafe_allow_html=True)
        st.write("")
        st.markdown("**🕒 時區**<br>UTC+8（香港時間）", unsafe_allow_html=True)
        st.write("")
        st.markdown("**🚨 緊急電話**<br><span style='color:red;'>999（警察/救護/消防）</span>", unsafe_allow_html=True)
    with c2:
        st.markdown("**💰 貨幣**<br>港幣 (HKD)", unsafe_allow_html=True)
        st.write("")
        st.markdown("**🔌 電壓**<br>220V / 50Hz（英式3腳）", unsafe_allow_html=True)
        st.write("")
        st.markdown("**📞 旅遊查詢**<br>2508 1234（旅發局）", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("💡 旅遊小貼士")
    st.markdown("""
    - 香港為免稅港，全港購物均**免消費稅**，**無需辦理退稅**
    - 八達通可在機場、地鐵站、便利店購買
    - 建議下載「香港出行易」App 查交通
    - 大型商場有退稅服務（只限非香港居民）
    """)

    st.markdown("---")
    st.caption("本 App 由 Tony Ho（何浩強）開發 ｜ CCMF Funding Demo 2026")
