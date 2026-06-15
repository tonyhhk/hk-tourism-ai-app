from datetime import datetime, time
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup
import json

st.set_page_config(page_title="HK Tourism AI App", page_icon="🌏", layout="wide")
st.title("🌏 HK Tourism AI App - Demo")
st.subheader("CCMF Funding Demo | 2026")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ 地圖", "✈️ 行程", "👥 社群", "🧾 清單", "ℹ️ 關於"])

# ==================== 地圖 Tab ====================
with tab1:
    st.header("🗺️ 地圖")
    st.write("按類別同地區探索香港景點（Demo 版本）")

    if "itinerary" not in st.session_state:
        st.session_state.itinerary = {}

    data = {
        "自然": [
            {"name": "下白泥", "coords": [22.45, 113.95], "desc": "全港最靚日落海岸。", "hours": "全日開放"},
            {"name": "石澳", "coords": [22.23, 114.25], "desc": "前後灘 + 情人橋。", "hours": "全日開放"},
            {"name": "淺水灣", "coords": [22.23, 114.20], "desc": "著名海灘，適合游泳。", "hours": "全日開放"},
            {"name": "深水灣", "coords": [22.24, 114.18], "desc": "寧靜海灘，適合家庭。", "hours": "全日開放"},
            {"name": "黃金海岸", "coords": [22.37, 113.95], "desc": "美麗沙灘，適合睇日落。", "hours": "全日開放"},
            {"name": "西貢大浪灣", "coords": [22.38, 114.27], "desc": "著名衝浪勝地。", "hours": "全日開放"},
            {"name": "長洲", "coords": [22.21, 114.03], "desc": "寧靜離島，適合單車。", "hours": "全日開放"},
            {"name": "張保仔洞", "coords": [22.35, 114.05], "desc": "海盜張保仔藏身處。", "hours": "全日開放"},
            {"name": "觀音灣", "coords": [22.22, 114.22], "desc": "寧靜海灣，適合冥想。", "hours": "全日開放"},
            {"name": "萬宜水庫東壩", "coords": [22.38, 114.32], "desc": "1億4千萬年自然奇觀。", "hours": "全日開放"},
            {"name": "米埔自然保護區", "coords": [22.49, 114.05], "desc": "重要候鳥保護區。", "hours": "需預約"},
            {"name": "香港動植物公園", "coords": [22.28, 114.15], "desc": "市中心綠洲。", "hours": "每日 6:00-19:00"},
            {"name": "港島海濱公園", "coords": [22.28, 114.17], "desc": "沿海長廊，適合散步。", "hours": "全日開放"},
        ],
        "文化": [
            {"name": "M+", "coords": [22.30, 114.16], "desc": "視覺文化博物館。", "hours": "星期三至一 10:00-18:00"},
            {"name": "故宮博物館", "coords": [22.30, 114.16], "desc": "中國古代藝術珍品。", "hours": "星期三至一 10:00-18:00"},
            {"name": "天壇大佛", "coords": [22.254, 113.905], "desc": "香港最大戶外青銅佛像。", "hours": "每日 10:00-17:30"},
            {"name": "寶蓮禪寺", "coords": [22.25, 113.91], "desc": "著名佛教寺廟。", "hours": "每日 8:00-18:00"},
            {"name": "黃大仙", "coords": [22.34, 114.19], "desc": "著名求簽廟宇。", "hours": "每日 7:00-17:30"},
            {"name": "志蓮淨苑及南蓮園池", "coords": [22.34, 114.18], "desc": "優美園林同佛教建築。", "hours": "每日 7:00-17:00"},
            {"name": "廟街夜市", "coords": [22.31, 114.17], "desc": "著名夜市。", "hours": "傍晚至凌晨"},
            {"name": "怪獸大廈", "coords": [22.33, 114.16], "desc": "彩色外牆網紅點。", "hours": "全日（外觀）"},
            {"name": "九龍寨城公園", "coords": [22.33, 114.19], "desc": "前九龍寨城遺址。", "hours": "每日 6:30-23:00"},
        ],
        "美食": [
            {"name": "太安樓", "coords": [22.282, 114.222], "desc": "西灣河士林夜市附近茶餐廳。", "hours": "每日 7:00-22:00"},
            {"name": "東大街", "coords": [22.279, 114.230], "desc": "筲箕灣傳統茶餐廳街。", "hours": "每日"},
            {"name": "COA", "coords": [22.281, 114.158], "desc": "高級墨西哥菜，米芝蓮星級。", "hours": "視乎營業時間"},
            {"name": "澳洲牛奶公司", "coords": [22.306, 114.171], "desc": "經典奶茶同菠蘿油。", "hours": "每日 7:30-23:00"},
            {"name": "bakehouse", "coords": [22.276, 114.172], "desc": "人氣 bakery。", "hours": "每日"},
            {"name": "端記茶樓", "coords": [22.283, 114.155], "desc": "傳統茶樓，點心出色。", "hours": "每日"},
            {"name": "蘭芳園", "coords": [22.283, 114.153], "desc": "經典奶茶，結志街。", "hours": "每日"},
            {"name": "美都餐室", "coords": [22.283, 114.155], "desc": "老字號茶餐廳。", "hours": "每日"},
            {"name": "金華冰廳", "coords": [22.315, 114.170], "desc": "傳統冰廳。", "hours": "每日"},
            {"name": "勝香園", "coords": [22.283, 114.155], "desc": "著名茶餐廳。", "hours": "每日"},
        ],
        "娛樂": {
            "太平山頂區": [
                {"name": "香港蠟像館", "coords": [22.275, 114.145], "desc": "香港唯一蠟像館。", "hours": "每日 10:00-20:00"},
                {"name": "香港杜莎夫人蠟像館", "coords": [22.275, 114.145], "desc": "世界級蠟像館。", "hours": "每日 10:00-20:00"},
                {"name": "山頂纜車", "coords": [22.275, 114.145], "desc": "香港 iconic 纜車。", "hours": "每日 7:00-23:00"},
                {"name": "大富翁夢想世界", "coords": [22.275, 114.145], "desc": "大富翁主題遊樂場。", "hours": "每日 10:00-20:00"},
                {"name": "山頂凌霄閣", "coords": [22.275, 114.145], "desc": "太平山頂觀景台。", "hours": "視乎營業時間"},
            ],
            "尖沙咀區": [
                {"name": "尖沙咀鐘樓", "coords": [22.294, 114.168], "desc": "歷史建築。", "hours": "全日（外觀）"},
                {"name": "星光大道", "coords": [22.294, 114.172], "desc": "電影名人手印。", "hours": "全日開放"},
                {"name": "天際100香港觀景台", "coords": [22.30, 114.16], "desc": "香港最高觀景台。", "hours": "每日 8:00-23:00"},
            ],
            "中環區": [
                {"name": "中環街市", "coords": [22.283, 114.158], "desc": "歷史街市，文創空間。", "hours": "每日 10:00-22:00"},
                {"name": "LKF", "coords": [22.2815, 114.1555], "desc": "著名酒吧夜生活區。", "hours": "傍晚至凌晨"},
            ],
            "旺角區": [
                {"name": "女人街", "coords": [22.315, 114.17], "desc": "平價服裝街。", "hours": "每日 11:00-23:00"},
                {"name": "花園街（波鞋街）", "coords": [22.315, 114.17], "desc": "波鞋街。", "hours": "每日 10:00-22:00"},
            ],
            "銅鑼灣區": [
                {"name": "時代廣場", "coords": [22.28, 114.185], "desc": "大型購物商場。", "hours": "每日 10:00-22:00"},
            ],
            "其他": [
                {"name": "迪士尼", "coords": [22.31, 114.04], "desc": "香港迪士尼樂園。", "hours": "視乎季節"},
                {"name": "海洋公園", "coords": [22.25, 114.18], "desc": "香港著名主題樂園。", "hours": "視乎季節"},
                {"name": "昂坪360", "coords": [22.255, 113.905], "desc": "世界級觀光纜車。", "hours": "每日 10:00-18:00"},
            ]
        }
    }

    main_cat = st.selectbox("選擇大類別", options=list(data.keys()))

    if main_cat == "娛樂":
        area = st.selectbox("選擇地區", options=list(data["娛樂"].keys()))
        spots = data["娛樂"][area]
    else:
        spots = data[main_cat]

    m = folium.Map(location=[22.3193, 114.1694], zoom_start=11)

    for spot in spots:
        popup_html = f"""
        <div style="background:white; padding:10px 14px; border-radius:10px; min-width:200px;">
            <b style="color:#d4a017;">{spot['name']}</b><br>
            {spot['desc']}<br>
            <small><b>開放時間：</b>{spot['hours']}</small>
        </div>
        """
        folium.Marker(
            location=spot["coords"],
            popup=Popup(popup_html, max_width=260),
            tooltip=spot["name"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=700, height=500)

    st.markdown("---")

    # ==================== 選擇預設加入邊一日 ====================
    if st.session_state.itinerary:
        day_options = list(st.session_state.itinerary.keys())
    else:
        day_options = ["Day 1"]

    default_day = st.selectbox("預設加入邊一日", options=day_options, key="default_day_map")

    st.write(f"### {main_cat} 景點列表")

    for i, spot in enumerate(spots):
        with st.expander(f"📍 {spot['name']}"):
            st.write(spot['desc'])
            st.write(f"**開放時間**：{spot['hours']}")

            button_key = f"{main_cat}_{spot['name']}_{i}"

            if st.button(f"加入我的行程 - {spot['name']}", key=button_key):
                target_day = default_day

                if target_day not in st.session_state.itinerary:
                    st.session_state.itinerary[target_day] = []

                st.session_state.itinerary[target_day].append(spot['name'])
                st.success(f"✅ 已將「{spot['name']}」加入 {target_day}！")

# ==================== 行程 Tab ====================
with tab2:
    st.header("✈️ 行程（最優先）")

    if "itinerary" not in st.session_state:
        st.session_state.itinerary = {}
    if "itinerary_time" not in st.session_state:
        st.session_state.itinerary_time = {}

    # 載入分享代碼
    with st.expander("🔗 載入分享代碼 / 連結（可選）", expanded=False):
        st.write("如果你有之前生成嘅分享代碼，可以喺下面貼上還原行程：")
        share_code_input = st.text_area("貼上分享代碼", height=150, key="share_code_input")

        if st.button("還原行程"):
            if share_code_input:
                try:
                    loaded_data = json.loads(share_code_input)
                    st.session_state.itinerary = loaded_data.get("itinerary", {})

                    time_data = loaded_data.get("itinerary_time", {})
                    restored_time = {}
                    for day, places in time_data.items():
                        restored_time[day] = {}
                        for place, t_str in places.items():
                            restored_time[day][place] = datetime.strptime(t_str, "%H:%M").time()
                    st.session_state.itinerary_time = restored_time
                    st.success("✅ 行程已成功還原！")
                except:
                    st.error("分享代碼格式錯誤")

    st.markdown("---")

    # 步驟 1：選擇天數
    st.subheader("步驟 1：選擇旅行天數")
    days = st.slider("旅行天數", 1, 7, 3, key="trip_days")

    if st.button("確認天數"):
        for d in range(1, days + 1):
            if f"Day {d}" not in st.session_state.itinerary:
                st.session_state.itinerary[f"Day {d}"] = []
        st.success(f"已設定 {days} 日行程")

    st.markdown("---")

    # 步驟 2：加地方
    if st.session_state.itinerary:
        st.subheader("步驟 2：將地方加到每日行程")

        day_choice = st.selectbox("選擇日子", options=list(st.session_state.itinerary.keys()), key="day_select")
        place_name = st.text_input("輸入景點名稱")

        if st.button("加入呢一日"):
            if place_name:
                st.session_state.itinerary[day_choice].append(place_name)
                st.success(f"已加入 {place_name}")
            else:
                st.warning("請輸入景點名稱")

        st.markdown("### 目前行程")
        for day, places in st.session_state.itinerary.items():
            with st.expander(f"{day}（{len(places)} 個地方）"):
                if places:
                    for p in places:
                        st.write(f"- {p}")
                else:
                    st.write("（未有地方）")

    st.markdown("---")

    # 步驟 3：安排時間
    if st.session_state.itinerary:
        st.subheader("步驟 3：安排每站時間")

        day_for_time = st.selectbox("選擇要安排時間嘅日子", options=list(st.session_state.itinerary.keys()), key="time_day")
        places = st.session_state.itinerary.get(day_for_time, [])

        if places:
            st.write(f"**{day_for_time} 時間安排**")
            time_plan = {}
            for i, place in enumerate(places):
                time_input = st.time_input(f"{place} 開始時間", key=f"time_{day_for_time}_{i}")
                time_plan[place] = time_input

            if st.button("儲存時間安排"):
                st.session_state.itinerary_time[day_for_time] = time_plan
                st.success(f"已儲存 {day_for_time} 嘅時間")

            if day_for_time in st.session_state.itinerary_time:
                sorted_times = sorted(st.session_state.itinerary_time[day_for_time].items(), key=lambda x: x[1])
                st.markdown("**已安排時間（已自動排序）：**")
                for place, t in sorted_times:
                    st.write(f"- **{t.strftime('%I:%M %p')}**　{place}")
        else:
            st.info("呢一日未有地方")

    st.markdown("---")

    # 步驟 4：完成行程清單
    if st.session_state.itinerary:
        st.subheader("步驟 4：完成行程清單")

        if st.button("生成完整行程清單"):
            st.session_state.trip_completed = True

        if st.session_state.get("trip_completed", False):
            st.markdown("## 📋 你的完整行程清單")

            itinerary_text = ""
            for day in sorted(st.session_state.itinerary.keys()):
                places = st.session_state.itinerary[day]
                times = st.session_state.itinerary_time.get(day, {})

                itinerary_text += f"\n### {day}\n"
                for place in places:
                    time_str = times.get(place)
                    if time_str:
                        itinerary_text += f"- {time_str.strftime('%I:%M %p')}　{place}\n"
                    else:
                        itinerary_text += f"- {place}\n"

            # 自動按時間排序 + 顯示
            for day in sorted(st.session_state.itinerary.keys()):
                places = st.session_state.itinerary[day]
                times = st.session_state.itinerary_time.get(day, {})

                if times:
                    sorted_places = sorted(places, key=lambda p: times.get(p) or time.min)
                else:
                    sorted_places = places

                st.markdown(f"### {day}")
                for place in sorted_places:
                    time_str = times.get(place)
                    if time_str:
                        st.write(f"**{time_str.strftime('%I:%M %p')}**　{place}")
                    else:
                        st.write(f"- {place}")
                st.write("")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🖼️ 下載為圖片（分享用）"):
                    st.info("提示：請按鍵盤 Ctrl + Shift + S 截圖分享")

            with col2:
                if st.button("🔗 生成分享代碼"):
                    share_data = {
                        "itinerary": st.session_state.itinerary,
                        "itinerary_time": {k: {p: t.strftime('%H:%M') for p, t in v.items()}
                                           for k, v in st.session_state.itinerary_time.items()}
                    }
                    share_code = json.dumps(share_data, ensure_ascii=False, indent=2)
                    st.code(share_code, language="json")
                    st.success("請複製上面嘅分享代碼俾朋友")

# ==================== 其他 Tab ====================
with tab3:
    st.header("👥 社群")
    st.write("（之後會加入分享同發現路線功能）")

with tab4:
    st.header("🧾 清單")
    st.write("（之後會加入行李同日常清單）")

with tab5:
    st.header("ℹ️ 關於")
    st.write("（之後會加入地區資訊同每月活動）")