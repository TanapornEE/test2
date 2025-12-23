import streamlit as st
import matplotlib.pyplot as plt

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Early Puberty Screening System",
    page_icon="🩺",
    layout="wide"
)

# ================== HEADER ==================
st.markdown("""
<style>
.big-title {
    font-size:40px;
    font-weight:700;
}
.sub {
    color: #555;
}
.card {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🩺 ระบบประเมินภาวะโตก่อนวัย</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Early Puberty Screening Assistant (For Preliminary Assessment Only)</div>', unsafe_allow_html=True)

st.divider()

# ================== DATA (WHO / Thai Reference) ==================
age_std = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

h_P3  = [81,90,97,103,108,113,118,122,126,131,136,141,147,151,153,154,155,156]
h_P50 = [87,96,103,109,114,119,124,128,133,138,144,150,156,159,161,162,163,164]
h_P97 = [93,102,109,115,120,125,130,134,138,144,150,157,164,167,169,170,171,172]

w_P3  = [10,12,14,15,17,18,20,22,24,27,30,34,38,42,45,47,48,49]
w_P50 = [12,14,16,18,20,22,25,28,32,36,41,47,52,55,57,58,59,60]
w_P97 = [14,17,20,23,26,30,35,40,45,50,58,65,72,78,82,85,87,90]

# ================== LAYOUT ==================
left, right = st.columns([1, 1.2])

# ================== INPUT CARD ==================
with left:
    st.markdown("### 📋 ข้อมูลเด็ก")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    age = st.number_input("อายุ (ปี)", 2.0, 19.0, 10.0, step=0.1)
    height = st.number_input("ส่วนสูง (cm)", 50.0, 200.0, 140.0)
    weight = st.number_input("น้ำหนัก (kg)", 2.0, 120.0, 40.0)

    hair = st.radio("ลักษณะทางเพศทุติยภูมิ", ["ยังไม่พบ", "พบแล้ว"])

    xray = st.file_uploader("🦴 ภาพ X-ray ข้อมือ (ถ้ามี)", type=["jpg", "png"])

    st.markdown('</div>', unsafe_allow_html=True)

# ================== RESULT ==================
with right:
    st.markdown("### 📊 ผลการประเมิน")

    if st.button("🔍 ประเมินผล", use_container_width=True):

        # -------- GRAPH --------
        fig, ax1 = plt.subplots(figsize=(7, 9))

        ax1.plot(age_std, h_P3, "--", label="Height P3")
        ax1.plot(age_std, h_P50, linewidth=3, label="Height P50")
        ax1.plot(age_std, h_P97, "--", label="Height P97")
        ax1.scatter(age, height, s=130)

        ax1.set_xlabel("Age (years)")
        ax1.set_ylabel("Height (cm)")
        ax1.set_ylim(80, 180)
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.plot(age_std, w_P3, ":", label="Weight P3")
        ax2.plot(age_std, w_P50, linewidth=3, label="Weight P50")
        ax2.plot(age_std, w_P97, ":", label="Weight P97")
        ax2.scatter(age, weight, marker="x", s=130)

        ax2.set_ylabel("Weight (kg)")
        ax2.set_ylim(10, 90)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8)

        st.pyplot(fig)

        # -------- BONE AGE --------
        estimated_bone_age = age + (2.0 if hair == "พบแล้ว" else 0.5)

        st.markdown("### 🧠 สรุปผล")
        st.write(f"• อายุจริง: **{age:.1f} ปี**")
        st.write(f"• Bone Age (ประเมิน): **{estimated_bone_age:.1f} ปี**")

        if age < 8 and estimated_bone_age - age >= 2 and hair == "พบแล้ว":
            st.error("⚠️ พบความเสี่ยงภาวะโตก่อนวัย")
            st.write("คำแนะนำ: ควรปรึกษาแพทย์เฉพาะทางต่อมไร้ท่อเด็ก")
        else:
            st.success("✅ อยู่ในเกณฑ์ปกติ")
            st.write("คำแนะนำ: ติดตามการเจริญเติบโตอย่างสม่ำเสมอ")

        st.caption("ระบบนี้เป็นการประเมินเบื้องต้น ไม่สามารถใช้แทนการวินิจฉัยของแพทย์ได้")
