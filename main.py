import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

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
.ai-result {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown('<div class="title">🩺 Early Puberty Screening System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Bone Age Assessment & Clinical Evaluation</div>', unsafe_allow_html=True)
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
        return "< P3 (Below Standard)"
    elif height < p50:
        return "P3-P50 (Normal)"
    elif height < p97:
        return "P50-P97 (Normal)"
    else:
        return "> P97 (Above Standard)"

def calculate_weight_percentile(age, weight):
    """Calculate which percentile the weight falls into"""
    p3 = interpolate_percentile(age, age_std, w_P3)
    p50 = interpolate_percentile(age, age_std, w_P50)
    p97 = interpolate_percentile(age, age_std, w_P97)
    
    if weight < p3:
        return "< P3 (Below Standard)"
    elif weight < p50:
        return "P3-P50 (Normal)"
    elif weight < p97:
        return "P50-P97 (Normal)"
    else:
        return "> P97 (Above Standard)"

def calculate_bmi(weight, height_cm):
    """Calculate BMI"""
    height_m = height_cm / 100
    return weight / (height_m ** 2)

def assess_risk_level(age, gender, secondary_signs, bone_age_diff):
    """Assess precocious puberty risk level based on clinical criteria"""
    # Age threshold for precocious puberty
    if gender == "Female":
        age_threshold = 8
    else:  # Male
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

def create_tm_html(image_data):
    """Create HTML with Teachable Machine model integration"""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    </head>
    <body>
        <div id="result" style="font-family: Arial; padding: 20px;"></div>
        <div id="label-container" style="font-family: Arial; padding: 10px;"></div>
        
        <script type="text/javascript">
            const URL = "https://teachablemachine.withgoogle.com/models/AffepRuZp/";
            let model, maxPredictions;

            async function init() {{
                const modelURL = URL + "model.json";
                const metadataURL = URL + "metadata.json";

                try {{
                    model = await tmImage.load(modelURL, metadataURL);
                    maxPredictions = model.getTotalClasses();
                    
                    document.getElementById("result").innerHTML = '<p style="color: green;">✅ Model loaded successfully!</p>';
                    
                    // Predict from base64 image
                    await predict();
                }} catch (error) {{
                    document.getElementById("result").innerHTML = '<p style="color: red;">❌ Error loading model: ' + error.message + '</p>';
                }}
            }}

            async function predict() {{
                try {{
                    // Create image element
                    const img = new Image();
                    img.src = "{image_data}";
                    
                    await img.decode();
                    
                    const prediction = await model.predict(img);
                    
                    let resultHTML = '<h3>🎯 AI Prediction Results:</h3>';
                    let maxProb = 0;
                    let maxClass = '';
                    
                    for (let i = 0; i < maxPredictions; i++) {{
                        const className = prediction[i].className;
                        const probability = (prediction[i].probability * 100).toFixed(2);
                        
                        if (prediction[i].probability > maxProb) {{
                            maxProb = prediction[i].probability;
                            maxClass = className;
                        }}
                        
                        resultHTML += '<div style="margin: 10px 0; background: #f0f0f0; padding: 10px; border-radius: 5px;">';
                        resultHTML += '<strong>' + className + ':</strong> ' + probability + '%';
                        resultHTML += '<div style="background: #ddd; height: 20px; border-radius: 10px; margin-top: 5px;">';
                        resultHTML += '<div style="background: linear-gradient(90deg, #667eea, #764ba2); width: ' + probability + '%; height: 100%; border-radius: 10px;"></div>';
                        resultHTML += '</div></div>';
                    }}
                    
                    resultHTML += '<div style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 10px;">';
                    resultHTML += '<h3>Predicted Class: ' + maxClass + '</h3>';
                    resultHTML += '<p>Confidence: ' + (maxProb * 100).toFixed(2) + '%</p>';
                    resultHTML += '</div>';
                    
                    document.getElementById("label-container").innerHTML = resultHTML;
                    
                    // Send results back to Streamlit
                    window.parent.postMessage({{
                        type: 'prediction',
                        data: {{
                            predictions: prediction,
                            maxClass: maxClass,
                            maxProb: maxProb
                        }}
                    }}, '*');
                    
                }} catch (error) {{
                    document.getElementById("result").innerHTML = '<p style="color: red;">❌ Prediction error: ' + error.message + '</p>';
                }}
            }}

            // Initialize on load
            window.onload = init;
        </script>
    </body>
    </html>
    """
    return html_code

# ===================== LAYOUT =====================
left, right = st.columns([1, 1.4])

# ===================== INPUT SECTION =====================
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📋 Basic Information</div>', unsafe_allow_html=True)
    
    gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (years)", 2.0, 19.0, 8.5, step=0.1)
    with col2:
        birth_date = st.date_input("Birth Date (if known)", 
                                   value=datetime(2015, 1, 1),
                                   max_value=datetime.now())
    
    height = st.number_input("Height (cm)", 50.0, 200.0, 130.0, step=0.1)
    weight = st.number_input("Weight (kg)", 2.0, 120.0, 35.0, step=0.1)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secondary sexual characteristics
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🔬 Secondary Sexual Characteristics</div>', unsafe_allow_html=True)
    
    if gender == "Female":
        breast = st.checkbox("📍 Breast Development")
        pubic_hair = st.checkbox("📍 Pubic Hair")
        axillary_hair = st.checkbox("📍 Axillary Hair")
        menarche = st.checkbox("📍 Menarche (First Period)")
        body_odor = st.checkbox("📍 Body Odor")
        
        secondary_count = sum([breast, pubic_hair, axillary_hair, menarche, body_odor])
    else:
        testicular = st.checkbox("📍 Testicular Enlargement")
        penile = st.checkbox("📍 Penile Growth")
        pubic_hair = st.checkbox("📍 Pubic Hair")
        facial_hair = st.checkbox("📍 Facial Hair")
        voice_change = st.checkbox("📍 Voice Change")
        body_odor = st.checkbox("📍 Body Odor")
        
        secondary_count = sum([testicular, penile, pubic_hair, facial_hair, voice_change, body_odor])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional information with AI
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🤖 AI X-ray Analysis</div>', unsafe_allow_html=True)
    
    st.info("📸 Upload hand/wrist X-ray for AI-powered bone age assessment")
    xray = st.file_uploader("Upload X-ray Image", type=["jpg", "png", "jpeg"], key="xray_upload")
    
    ai_component_html = None
    
    if xray:
        image = Image.open(xray)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        st.image(image, width=280, caption="X-ray Image")
        
        if st.button("🔍 Analyze with AI", use_container_width=True):
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data = f"data:image/jpeg;base64,{img_str}"
            
            # Create HTML component with Teachable Machine
            ai_component_html = create_tm_html(image_data)
    
    st.markdown("---")
    
    bone_age_known = st.checkbox("Or manually enter Bone Age")
    if bone_age_known:
        bone_age = st.number_input("Bone Age (years)", 2.0, 19.0, age, step=0.1)
    else:
        bone_age = age + (0.5 if secondary_count >= 2 else 0)
    
    family_history = st.checkbox("Family History of Precocious Puberty")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== AI COMPONENT DISPLAY =====================
if ai_component_html:
    st.markdown("---")
    st.markdown("### 🤖 AI Model Analysis")
    components.html(ai_component_html, height=600, scrolling=True)

# ===================== RESULT SECTION =====================
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📊 Assessment Results & Analysis</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Generate Report", use_container_width=True, type="primary"):
        
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
            st.markdown(f'<div class="metric-box"><h3>{secondary_count}</h3><p>Signs Present</p></div>', unsafe_allow_html=True)
        
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
        
        plt.title(f"Growth Chart - {gender}, Age {age:.1f} years", fontsize=14, fontweight='bold', pad=20)
        st.pyplot(fig)
        
        st.divider()
        
        # -------- DETAILED ANALYSIS --------
        st.markdown("### 🧠 Detailed Analysis")
        
        st.markdown(f"""
        **📏 Growth Parameters:**
        - Height: {height:.1f} cm ({height_perc})
        - Weight: {weight:.1f} kg ({weight_perc})
        - BMI: {bmi:.1f} kg/m²
        
        **🦴 Bone Age Assessment:**
        - Chronological Age: {age:.1f} years
        - Bone Age: {bone_age:.1f} years
        - Difference: {bone_age_diff:+.1f} years
        
        **🔬 Sexual Development:**
        - Signs Present: {secondary_count} characteristics
        - Family History: {"Yes" if family_history else "No"}
        """)
        
        # -------- RISK ASSESSMENT --------
        risk_level = assess_risk_level(age, gender, secondary_count, bone_age_diff)
        
        st.markdown("### ⚕️ Clinical Risk Assessment")
        
        if risk_level == "high":
            st.markdown('<div class="risk-high">', unsafe_allow_html=True)
            st.markdown("#### 🔴 High Risk - Medical Consultation Required")
            st.markdown("""
            **Recommendations:**
            - Urgent consultation with Pediatric Endocrinologist recommended
            - Comprehensive evaluation needed:
              - Bone Age X-ray (if not done)
              - Hormone Levels (LH, FSH, Estradiol/Testosterone)
              - Brain MRI (if indicated)
            - Close growth monitoring required
            - Consider GnRH analogue therapy to delay development
            - Early intervention can prevent complications
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif risk_level == "medium":
            st.markdown('<div class="risk-medium">', unsafe_allow_html=True)
            st.markdown("#### 🟡 Moderate Risk - Follow-up Recommended")
            st.markdown("""
            **Recommendations:**
            - Schedule evaluation with Pediatric Endocrinologist
            - Monitor growth every 3-6 months
            - Track development of secondary sexual characteristics
            - Document changes systematically
            - Consider Bone Age X-ray for accurate assessment
            - Re-evaluate if progression continues
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="risk-low">', unsafe_allow_html=True)
            st.markdown("#### 🟢 Low Risk - Normal Development")
            st.markdown("""
            **Recommendations:**
            - Growth and development within normal parameters
            - Continue routine growth monitoring
            - Regular annual health check-ups
            - Consult physician if unusual changes occur
            - Maintain healthy lifestyle habits
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Warning and disclaimer
        st.warning("⚠️ **Important Notice:** This system is a screening tool for educational purposes only. AI assessment provides preliminary analysis and cannot replace professional medical diagnosis. Always consult qualified healthcare professionals for accurate diagnosis and treatment planning.")
        
        if not bone_age_known and not xray:
            st.info("💡 **Note:** Bone Age estimation without X-ray is approximate. For accurate assessment, hand/wrist X-ray evaluation is recommended.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== FOOTER =====================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Early Puberty Screening System v3.0 AI-Powered</strong></p>
    <p>Clinical Decision Support Tool | Educational & Screening Purposes Only</p>
    <p style='font-size: 12px;'>📚 References: Thai CDC Growth Charts, WHO Standards, Pediatric Endocrinology Guidelines</p>
    <p style='font-size: 12px;'>🤖 AI Technology: Teachable Machine by Google</p>
    <p style='font-size: 11px; margin-top: 10px;'>Developed for medical education and preliminary screening. Not FDA approved for clinical diagnosis.</p>
</div>
""", unsafe_allow_html=True)
