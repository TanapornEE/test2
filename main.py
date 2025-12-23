import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Early Puberty Screening System",
    page_icon="🩺",
    layout="wide"
)

# ===================== STYLE =====================
st.markdown("""
<style>
body {background-color: #f4f6fb;}
.title {font-size: 40px; font-weight: 700; color: #1e3a8a;}
.subtitle {color: #555; margin-bottom: 20px; font-size: 16px;}
.card {
    background-color: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.section {font-size: 22px; font-weight: 600; margin-bottom: 10px; color: #1e40af;}
.risk-high {background-color: #fee2e2; padding: 15px; border-radius: 8px; border-left: 4px solid #dc2626;}
.risk-medium {background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;}
.risk-low {background-color: #d1fae5; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;}
.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown('<div class="title">🩺 ระบบประเมินภาวะโตก่อนวัย</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Early Puberty Screening Assistant - ระบบประเมินเชิงวิชาการเบื้องต้น</div>', unsafe_allow_html=True)
st.divider()

# ===================== STANDARD DATA (Thai CDC) =====================
age_std = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

# Height percentiles (cm)
h_P3  = [81,90,97,103,108,113,118,122,126,131,136,141,147,151,153,154,155,156]
h_P50 = [87,96,103,109,114,119,124,128,133,138,144,150,156,159,161,162,163,164]
h_P97 = [93,102,109,115,120,125,130,134,138,144,150,157,164,167,169,170,171,172]

# Weight percentiles (kg)
w_P3  = [10,12,14,15,17,18,20,22,24,27,30,34,38,42,45,47,48,49]
w_P50 = [12,14,16,18,20,22,25,28,32,36,41,47,52,55,57,58,59,60]
w_P97 = [14,17,20,23,26,30,35,40,45,50,58,65,72,78,82,85,87,90]

# ===================== HELPER FUNCTIONS =====================
def interpolate_percentile(age, age_list, value_list):
    """Interpolate percentile values for exact age"""
    return np.interp(age, age_list, value_list)

def calculate_height_percentile(age, height):
    """Calculate which percentile the height falls into"""
    p3 = interpolate_percentile(age, age_std, h_P3)
    p50 = interpolate_percentile(age, age_std, h_P50)
    p97 = interpolate_percentile(age, age_std, h_P97)
    
    if height < p3:
        return "< P3 (ต่ำกว่ามาตรฐาน)"
    elif height < p50:
        return "P3-P50 (ปกติ)"
    elif height < p97:
        return "P50-P97 (ปกติ)"
    else:
        return "> P97 (สูงกว่ามาตรฐาน)"

def calculate_weight_percentile(age, weight):
    """Calculate which percentile the weight falls into"""
    p3 = interpolate_percentile(age, age_std, w_P3)
    p50 = interpolate_percentile(age, age_std, w_P50)
    p97 = interpolate_percentile(age, age_std, w_P97)
    
    if weight < p3:
        return "< P3 (ต่ำกว่ามาตรฐาน)"
    elif weight < p50:
        return "P3-P50 (ปกติ)"
    elif weight < p97:
        return "P50-P97 (ปกติ)"
    else:
        return "> P97 (สูงกว่ามาตรฐาน)"

def calculate_bmi(weight, height_cm):
    """Calculate BMI"""
    height_m = height_cm / 100
    return weight / (height_m ** 2)

def assess_risk_level(age, gender, secondary_signs, bone_age_diff):
    """Assess precocious puberty risk level based on clinical criteria"""
    # Age threshold for precocious puberty
    if gender == "หญิง":
        age_threshold = 8
    else:  # ชาย
        age_threshold = 9
    
    # Check criteria
    early_age = age < age_threshold
    significant_secondary = secondary_signs >= 2
    advanced_bone_age = bone_age_diff >= 2
    
    if early_age and significant_secondary and advanced_bone_age:
        return "high"
    elif early_age and (significant_secondary or advanced_bone_age):
        return "medium"
    elif significant_secondary and advanced_bone_age:
        return "medium"
    else:
        return "low"

# ===================== LAYOUT =====================
left, right = st.columns([1, 1.4])

# ===================== INPUT SECTION =====================
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📋 ข้อมูลพื้นฐาน</div>', unsafe_allow_html=True)
    
    gender = st.radio("เพศ", ["หญิง", "ชาย"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("อายุ (ปี)", 2.0, 19.0, 8.5, step=0.1)
    with col2:
        birth_date = st.date_input("วันเกิด (ถ้าทราบ)", 
                                   value=datetime(2015, 1, 1),
                                   max_value=datetime.now())
    
    height = st.number_input("ส่วนสูง (cm)", 50.0, 200.0, 130.0, step=0.1)
    weight = st.number_input("น้ำหนัก (kg)", 2.0, 120.0, 35.0, step=0.1)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secondary sexual characteristics
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🔬 ลักษณะทางเพศทุติยภูมิ</div>', unsafe_allow_html=True)
    
    if gender == "หญิง":
        breast = st.checkbox("📍 มีการพัฒนาของเต้านม (Breast Development)")
        pubic_hair = st.checkbox("📍 มีขนบริเวณอวัยวะเพศ (Pubic Hair)")
        axillary_hair = st.checkbox("📍 มีขนรักแร้ (Axillary Hair)")
        menarche = st.checkbox("📍 มีประจำเดือนแล้ว (Menarche)")
        body_odor = st.checkbox("📍 มีกลิ่นตัว (Body Odor)")
        
        secondary_count = sum([breast, pubic_hair, axillary_hair, menarche, body_odor])
    else:
        testicular = st.checkbox("📍 อัณฑะโตขึ้น (Testicular Enlargement)")
        penile = st.checkbox("📍 องคชาตโตขึ้น (Penile Growth)")
        pubic_hair = st.checkbox("📍 มีขนบริเวณอวัยวะเพศ (Pubic Hair)")
        facial_hair = st.checkbox("📍 มีขนหน้า (Facial Hair)")
        voice_change = st.checkbox("📍 เสียงแตก (Voice Change)")
        body_odor = st.checkbox("📍 มีกลิ่นตัว (Body Odor)")
        
        secondary_count = sum([testicular, penile, pubic_hair, facial_hair, voice_change, body_odor])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional information
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🦴 ข้อมูลเพิ่มเติม</div>', unsafe_allow_html=True)
    
    bone_age_known = st.checkbox("ทราบ Bone Age จากการตรวจ X-ray")
    if bone_age_known:
        bone_age = st.number_input("Bone Age (ปี)", 2.0, 19.0, age, step=0.1)
    else:
        bone_age = age + (0.5 if secondary_count >= 2 else 0)
    
    xray = st.file_uploader("📷 อัพโหลดภาพ X-ray ข้อมือ (ถ้ามี)", type=["jpg", "png", "jpeg"])
    if xray:
        st.image(xray, width=280, caption="X-ray Image")
    
    family_history = st.checkbox("ประวัติครอบครัวมีภาวะโตก่อนวัย")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== RESULT SECTION =====================
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📊 ผลการประเมินและวิเคราะห์</div>', unsafe_allow_html=True)
    
    if st.button("🔍 ประเมินผล", use_container_width=True, type="primary"):
        
        # Calculate metrics
        bmi = calculate_bmi(weight, height)
        height_perc = calculate_height_percentile(age, height)
        weight_perc = calculate_weight_percentile(age, weight)
        bone_age_diff = bone_age - age
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><h3>{bmi:.1f}</h3><p>BMI</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><h3>{bone_age:.1f}</h3><p>Bone Age</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><h3>{secondary_count}</h3><p>ลักษณะทุติยภูมิ</p></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # -------- GROWTH CHART --------
        fig, ax1 = plt.subplots(figsize=(8, 10))
        
        # Height plot
        ax1.fill_between(age_std, h_P3, h_P97, alpha=0.1, color='lightblue', label='Height Normal Range')
        ax1.plot(age_std, h_P3, "--", color="#ff9999", linewidth=1.5, label="Height P3")
        ax1.plot(age_std, h_P50, "-", color="#0057b7", linewidth=3, label="Height P50 (Median)")
        ax1.plot(age_std, h_P97, "--", color="#ff9999", linewidth=1.5, label="Height P97")
        ax1.scatter(age, height, color="green", s=200, zorder=5, marker='o', edgecolors='darkgreen', linewidths=2)
        ax1.axvline(age, linestyle="--", alpha=0.3, color='gray')
        
        ax1.annotate(f"{height:.1f} cm", (age, height),
                     textcoords="offset points", xytext=(8,8),
                     fontsize=11, fontweight='bold', color="green",
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
        
        ax1.set_xlabel("Age (years)", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Height (cm)", fontsize=12, fontweight='bold', color='#0057b7')
        ax1.set_ylim(80, 180)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.tick_params(axis='y', labelcolor='#0057b7')
        
        # Weight plot
        ax2 = ax1.twinx()
        ax2.fill_between(age_std, w_P3, w_P97, alpha=0.1, color='lightyellow', label='Weight Normal Range')
        ax2.plot(age_std, w_P3, ":", color="#ffcc99", linewidth=1.5, label="Weight P3")
        ax2.plot(age_std, w_P50, "-", color="#ff7f0e", linewidth=3, label="Weight P50 (Median)")
        ax2.plot(age_std, w_P97, ":", color="#ffcc99", linewidth=1.5, label="Weight P97")
        ax2.scatter(age, weight, marker="D", color="purple", s=180, zorder=5, edgecolors='darkviolet', linewidths=2)
        
        ax2.annotate(f"{weight:.1f} kg", (age, weight),
                     textcoords="offset points", xytext=(8,-18),
                     fontsize=11, fontweight='bold', color="purple",
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="plum", alpha=0.7))
        
        ax2.set_ylabel("Weight (kg)", fontsize=12, fontweight='bold', color='#ff7f0e')
        ax2.set_ylim(10, 90)
        ax2.tick_params(axis='y', labelcolor='#ff7f0e')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left", framealpha=0.9)
        
        plt.title(f"Growth Chart - {gender} อายุ {age:.1f} ปี", fontsize=14, fontweight='bold', pad=20)
        st.pyplot(fig)
        
        st.divider()
        
        # -------- DETAILED ANALYSIS --------
        st.markdown("### 🧠 การวิเคราะห์โดยละเอียด")
        
        st.markdown(f"""
        **📏 ข้อมูลการเจริญเติบโต:**
        - ส่วนสูง: {height:.1f} cm ({height_perc})
        - น้ำหนัก: {weight:.1f} kg ({weight_perc})
        - BMI: {bmi:.1f} kg/m²
        
        **🦴 ข้อมูล Bone Age:**
        - อายุจริง: {age:.1f} ปี
        - Bone Age: {bone_age:.1f} ปี
        - ความแตกต่าง: {bone_age_diff:+.1f} ปี
        
        **🔬 ลักษณะทางเพศทุติยภูมิ:**
        - พบลักษณะ: {secondary_count} ข้อ
        - ประวัติครอบครัว: {"มี" if family_history else "ไม่มี"}
        """)
        
        # -------- RISK ASSESSMENT --------
        risk_level = assess_risk_level(age, gender, secondary_count, bone_age_diff)
        
        st.markdown("### ⚕️ สรุปผลการประเมิน")
        
        if risk_level == "high":
            st.markdown('<div class="risk-high">', unsafe_allow_html=True)
            st.markdown("#### 🔴 มีความเสี่ยงภาวะโตก่อนวัย")
            st.markdown("""
            **คำแนะนำ:**
            - ควรพบแพทย์เฉพาะทาง (กุมารเวชศาสตร์ต่อมไร้ท่อ) โดยเร็ว
            - อาจต้องตรวจเพิ่มเติม: Bone Age X-ray, Hormone Level, Brain MRI
            - ติดตามการเจริญเติบโตอย่างใกล้ชิด
            - พิจารณาการรักษาเพื่อชะลอพัฒนาการ
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif risk_level == "medium":
            st.markdown('<div class="risk-medium">', unsafe_allow_html=True)
            st.markdown("#### 🟡 ควรติดตามและปรึกษาแพทย์")
            st.markdown("""
            **คำแนะนำ:**
            - แนะนำให้พบแพทย์เพื่อประเมินเพิ่มเติม
            - ติดตามการเจริญเติบโตทุก 3-6 เดือน
            - สังเกตพัฒนาการทางเพศทุติยภูมิ
            - บันทึกการเปลี่ยนแปลงอย่างสม่ำเสมอ
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="risk-low">', unsafe_allow_html=True)
            st.markdown("#### 🟢 อยู่ในเกณฑ์ปกติ")
            st.markdown("""
            **คำแนะนำ:**
            - การเจริญเติบโตอยู่ในเกณฑ์ปกติ
            - ติดตามการเจริญเติบโตตามปกติ
            - ตรวจสุขภาพประจำปีตามกำหนด
            - หากมีการเปลี่ยนแปลงผิดปกติ ควรปรึกษาแพทย์
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Warning and disclaimer
        st.warning("⚠️ **คำเตือนสำคัญ:** ระบบนี้เป็นเครื่องมือคัดกรองเบื้องต้นเท่านั้น ไม่สามารถใช้แทนการวินิจฉัยของแพทย์ได้ ควรปรึกษาแพทย์เฉพาะทางเพื่อการตรวจวินิจฉัยที่แม่นยำ")
        
        st.info("💡 **หมายเหตุ:** การประเมิน Bone Age ที่ไม่ได้มาจาก X-ray เป็นเพียงการประมาณการเบื้องต้นเท่านั้น ควรตรวจ X-ray ข้อมือจริงเพื่อความแม่นยำ")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== FOOTER =====================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Early Puberty Screening System v2.0</strong></p>
    <p>ระบบประเมินภาวะโตก่อนวัยเบื้องต้น | เพื่อการศึกษาและคัดกรองเท่านั้น</p>
    <p style='font-size: 12px;'>📚 อ้างอิง: Thai CDC Growth Chart, WHO Standards, Pediatric Endocrinology Guidelines</p>
</div>
""", unsafe_allow_html=True)
