import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
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
.age-display {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin: 15px 0;
}
.ai-instruction {
    background-color: #e0f2fe;
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #0284c7;
    margin: 10px 0;
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
def calculate_age(birth_date):
    """Calculate age from birth date in years with decimal"""
    today = date.today()
    delta = relativedelta(today, birth_date)
    age_years = delta.years + delta.months / 12 + delta.days / 365.25
    return age_years, f"{delta.years} years {delta.months} months {delta.days} days"

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
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }}
            .status {{
                padding: 12px;
                border-radius: 8px;
                margin: 10px 0;
                font-weight: bold;
            }}
            .success {{ background-color: #d1fae5; color: #065f46; }}
            .error {{ background-color: #fee2e2; color: #991b1b; }}
            .loading {{ background-color: #dbeafe; color: #1e40af; }}
            .prediction-item {{
                margin: 12px 0;
                background: #f9fafb;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }}
            .progress-bar {{
                background: #e5e7eb;
                height: 24px;
                border-radius: 12px;
                margin-top: 8px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 12px;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            .final-result {{
                margin-top: 20px;
                padding: 20px;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 12px;
                text-align: center;
            }}
            h2 {{ color: #1e40af; margin-top: 0; }}
            h3 {{ color: #4f46e5; margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🤖 AI X-ray Image Analysis</h2>
            <div id="status" class="status loading">⏳ Loading AI Model...</div>
            <div id="result"></div>
        </div>
        
        <script type="text/javascript">
            const URL = "https://teachablemachine.withgoogle.com/models/AffepRuZp/";
            let model, maxPredictions;

            async function init() {{
                const modelURL = URL + "model.json";
                const metadataURL = URL + "metadata.json";

                try {{
                    model = await tmImage.load(modelURL, metadataURL);
                    maxPredictions = model.getTotalClasses();
                    
                    document.getElementById("status").className = "status success";
                    document.getElementById("status").innerHTML = '✅ AI Model Loaded Successfully! Analyzing Image...';
                    
                    await predict();
                }} catch (error) {{
                    document.getElementById("status").className = "status error";
                    document.getElementById("status").innerHTML = '❌ Model Loading Error: ' + error.message;
                }}
            }}

            async function predict() {{
                try {{
                    const img = new Image();
                    img.src = "{image_data}";
                    
                    await img.decode();
                    
                    const prediction = await model.predict(img);
                    
                    let resultHTML = '<h2>🎯 AI Analysis Results:</h2>';
                    let maxProb = 0;
                    let maxClass = '';
                    
                    for (let i = 0; i < maxPredictions; i++) {{
                        const className = prediction[i].className;
                        const probability = (prediction[i].probability * 100).toFixed(1);
                        
                        if (prediction[i].probability > maxProb) {{
                            maxProb = prediction[i].probability;
                            maxClass = className;
                        }}
                        
                        resultHTML += '<div class="prediction-item">';
                        resultHTML += '<div style="display: flex; justify-content: space-between; align-items: center;">';
                        resultHTML += '<strong style="font-size: 16px;">📊 ' + className + '</strong>';
                        resultHTML += '<span style="font-size: 18px; font-weight: bold; color: #667eea;">' + probability + '%</span>';
                        resultHTML += '</div>';
                        resultHTML += '<div class="progress-bar">';
                        resultHTML += '<div class="progress-fill" style="width: ' + probability + '%;">';
                        if (parseFloat(probability) > 20) {{
                            resultHTML += probability + '%';
                        }}
                        resultHTML += '</div></div></div>';
                    }}
                    
                    resultHTML += '<div class="final-result">';
                    resultHTML += '<h3>🏆 Predicted Classification</h3>';
                    resultHTML += '<h2 style="margin: 10px 0; color: white;">' + maxClass + '</h2>';
                    resultHTML += '<p style="font-size: 18px; margin: 5px 0;">Confidence Level: ' + (maxProb * 100).toFixed(1) + '%</p>';
                    resultHTML += '</div>';
                    
                    document.getElementById("result").innerHTML = resultHTML;
                    document.getElementById("status").className = "status success";
                    document.getElementById("status").innerHTML = '✅ Analysis Complete!';
                    
                    window.parent.postMessage({{
                        type: 'prediction',
                        data: {{
                            predictions: prediction,
                            maxClass: maxClass,
                            maxProb: maxProb
                        }}
                    }}, '*');
                    
                }} catch (error) {{
                    document.getElementById("status").className = "status error";
                    document.getElementById("status").innerHTML = '❌ Analysis Error: ' + error.message;
                }}
            }}

            window.onload = init;
        </script>
    </body>
    </html>
    """
    return html_code

# ===================== INITIALIZE SESSION STATE =====================
if 'calculated_age' not in st.session_state:
    st.session_state.calculated_age = None
if 'age_text' not in st.session_state:
    st.session_state.age_text = None

# ===================== LAYOUT =====================
left, right = st.columns([1, 1.4])

# ===================== INPUT SECTION =====================
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📋 Patient Demographics</div>', unsafe_allow_html=True)
    
    gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
    
    # Birth date input
    birth_date = st.date_input(
        "📅 Date of Birth", 
        value=datetime(2015, 6, 1),
        min_value=datetime(2005, 1, 1),
        max_value=datetime.now()
    )
    
    # Calculate age automatically
    if birth_date:
        age_years, age_text = calculate_age(birth_date)
        st.session_state.calculated_age = age_years
        st.session_state.age_text = age_text
        
        st.markdown(f'<div class="age-display">🎂 Chronological Age: {age_text}<br>({age_years:.1f} years)</div>', 
                   unsafe_allow_html=True)
    
    # Use calculated age
    age = st.session_state.calculated_age if st.session_state.calculated_age else 8.5
    
    height = st.number_input("Height (cm)", 50.0, 200.0, 130.0, step=0.1)
    weight = st.number_input("Weight (kg)", 2.0, 120.0, 35.0, step=0.1)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secondary sexual characteristics
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🔬 Secondary Sexual Characteristics</div>', unsafe_allow_html=True)
    
    # Use same characteristics for both genders (female pattern)
    pubic_hair = st.checkbox("📍 Pubarche (Pubic Hair Development)")
    axillary_hair = st.checkbox("📍 Axillary Hair")
    body_odor = st.checkbox("📍 Apocrine Body Odor")
    
    if gender == "Female":
        breast = st.checkbox("📍 Thelarche (Breast Development)")
        menarche = st.checkbox("📍 Menarche (First Menstruation)")
        secondary_count = sum([pubic_hair, axillary_hair, body_odor, breast, menarche])
    else:
        # For males, still show these options but without breast/menarche
        breast = False
        menarche = False
        secondary_count = sum([pubic_hair, axillary_hair, body_odor])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI X-ray Analysis
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">🤖 AI Bone Age Assessment</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-instruction">
        <strong>📸 Instructions:</strong><br>
        1. Upload hand/wrist X-ray (AP view preferred)<br>
        2. Click "Analyze with AI" button<br>
        3. Wait for analysis (approximately 3-5 seconds)<br>
        4. Review bone age assessment results
    </div>
    """, unsafe_allow_html=True)
    
    xray = st.file_uploader("📤 Upload X-ray Image", type=["jpg", "png", "jpeg"], key="xray_upload")
    
    ai_component_html = None
    show_ai_analysis = False
    
    if xray:
        image = Image.open(xray)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption="Uploaded X-ray Image", use_container_width=True)
        
        with col2:
            if st.button("🔍 Analyze with AI", use_container_width=True, type="primary"):
                show_ai_analysis = True
                
                # Convert image to base64
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                image_data = f"data:image/jpeg;base64,{img_str}"
                
                ai_component_html = create_tm_html(image_data)
    
    st.markdown("---")
    
    bone_age_known = st.checkbox("💡 Manual Bone Age Entry (if radiologist assessment available)")
    if bone_age_known:
        bone_age = st.number_input("Bone Age (years)", 2.0, 19.0, age, step=0.1)
    else:
        bone_age = age + (0.5 if secondary_count >= 2 else 0)
    
    family_history = st.checkbox("👨‍👩‍👧‍👦 Family History of Precocious Puberty")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== AI COMPONENT DISPLAY =====================
if show_ai_analysis and ai_component_html:
    st.markdown("---")
    st.markdown("### 🤖 AI Analysis Results")
    components.html(ai_component_html, height=700, scrolling=True)

# ===================== RESULT SECTION =====================
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section">📊 Clinical Assessment Results</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Generate Clinical Report", use_container_width=True, type="primary"):
        
        # Calculate metrics
        bmi = calculate_bmi(weight, height)
        height_perc = calculate_height_percentile(age, height)
        weight_perc = calculate_weight_percentile(age, weight)
        bone_age_diff = bone_age - age
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><h3>{bmi:.1f}</h3><p>BMI (kg/m²)</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><h3>{bone_age:.1f}</h3><p>Bone Age (yrs)</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><h3>{secondary_count}</h3><p>Sexual Maturity Signs</p></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Growth Chart
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
        
        # Detailed Analysis
        st.markdown("### 🧠 Clinical Analysis Summary")
        
        st.markdown(f"""
        **📏 Anthropometric Measurements:**
        - Height: {height:.1f} cm ({height_perc})
        - Weight: {weight:.1f} kg ({weight_perc})
        - BMI: {bmi:.1f} kg/m²
        
        **🦴 Skeletal Maturation Assessment:**
        - Chronological Age: {age:.1f} years ({st.session_state.age_text})
        - Bone Age: {bone_age:.1f} years
        - Bone Age Advancement: {bone_age_diff:+.1f} years
        
        **🔬 Sexual Maturation Status:**
        - Secondary Sexual Characteristics: {secondary_count} signs present
        - Family History: {"Positive" if family_history else "Negative"}
        """)
        
        # Risk Assessment
        risk_level = assess_risk_level(age, gender, secondary_count, bone_age_diff)
        
        st.markdown("### ⚕️ Clinical Risk Stratification")
        
        if risk_level == "high":
            st.markdown('<div class="risk-high">', unsafe_allow_html=True)
            st.markdown("#### 🔴 High Risk - Urgent Endocrinology Referral Required")
            st.markdown("""
            **Clinical Recommendations:**
            - **Immediate referral** to Pediatric Endocrinologist
            - **Comprehensive diagnostic workup:**
              - Skeletal maturation (bone age X-ray if not completed)
              - Hormonal evaluation (LH, FSH, Estradiol/Testosterone, DHEA-S)
              - GnRH stimulation test (if indicated)
              - Brain MRI to rule out CNS pathology
              - Thyroid function tests (TSH, Free T4)
            - **Growth velocity monitoring** every 3 months
            - **Treatment consideration:** GnRH analogue therapy
            - Early intervention may prevent:
              - Adult short stature
              - Psychosocial complications
              - Premature epiphyseal closure
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif risk_level == "medium":
            st.markdown('<div class="risk-medium">', unsafe_allow_html=True)
            st.markdown("#### 🟡 Moderate Risk - Endocrinology Evaluation Recommended")
            st.markdown("""
            **Clinical Recommendations:**
            - Schedule evaluation with Pediatric Endocrinologist
            - **Serial monitoring protocol:**
              - Growth parameters every 3-6 months
              - Tanner staging assessment
              - Growth velocity calculation
            - **Diagnostic considerations:**
              - Bone age radiography (if not performed)
              - Baseline hormonal screening
            - **Documentation requirements:**
              - Systematic recording of pubertal progression
              - Growth chart plotting
            - Re-evaluation if progression accelerates
            - Parental education regarding precocious puberty
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="risk-low">', unsafe_allow_html=True)
            st.markdown("#### 🟢 Low Risk - Normal Development Pattern")
            st.markdown("""
            **Clinical Recommendations:**
            - Growth and development within normal parameters
            - **Routine surveillance:**
              - Annual well-child examinations
              - Growth monitoring on standard curves
              - Pubertal development tracking
            - **Anticipatory guidance:**
              - Normal puberty education
              - Healthy lifestyle counseling
            - **Re-evaluation criteria:**
              - Rapid progression of secondary sexual characteristics
              - Accelerated growth velocity
              - Parental concerns
            - No intervention required at this time
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Warning and disclaimer
        st.warning("⚠️ **Medical Disclaimer:** This screening tool is designed for educational purposes and preliminary assessment only. AI-based bone age evaluation provides supplementary information and cannot replace professional radiological interpretation or clinical judgment. All findings must be confirmed by qualified healthcare professionals. This system is not FDA-approved for diagnostic purposes and should not be used as the sole basis for clinical decision-making.")
        
        if not bone_age_known and not xray:
            st.info("💡 **Clinical Note:** Bone age estimation without radiographic assessment is approximate and based on clinical parameters. For accurate skeletal maturation assessment, hand/wrist radiography (Greulich-Pyle or Tanner-Whitehouse method) is recommended.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== FOOTER =====================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Early Puberty Screening System v3.1 AI-Enhanced</strong></p>
    <p>Clinical Decision Support Tool | Educational & Screening Purposes Only</p>
    <p style='font-size: 12px;'>📚 References: Thai CDC Growth Charts, WHO Growth Standards, Pediatric Endocrinology Clinical Guidelines</p>
    <p style='font-size: 12px;'>🤖 AI Technology: Teachable Machine by Google (TensorFlow.js)</p>
    <p style='font-size: 11px; margin-top: 10px;'>Developed for medical education and preliminary screening. Not FDA approved for clinical diagnosis.<br>
    Always consult board-certified pediatric endocrinologists for definitive diagnosis and treatment.</p>
</div>
""", unsafe_allow_html=True)
