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
    page_title="BONESAGE CHATBOT - AI Bone Age Assessment",
    page_icon="🦴",
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
    border-left: 5px solid #667eea;
}
.card-demographics {
    background: linear-gradient(135deg, #ffeef8 0%, #fff5f7 100%);
    border-left: 5px solid #ec4899;
}
.card-sexual {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-left: 5px solid #0ea5e9;
}
.card-ai {
    background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
    border-left: 5px solid #8b5cf6;
}
.card-results {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-left: 5px solid #10b981;
}
.section {
    font-size: 22px; 
    font-weight: 700; 
    margin-bottom: 15px; 
    color: #1e40af;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-icon {
    font-size: 28px;
}
.risk-high {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #dc2626;
    box-shadow: 0 4px 6px rgba(220, 38, 38, 0.1);
}
.risk-medium {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #f59e0b;
    box-shadow: 0 4px 6px rgba(245, 158, 11, 0.1);
}
.risk-low {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #10b981;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
}
.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin: 10px 0;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    transition: transform 0.2s;
}
.metric-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
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
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin: 15px 0;
    box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}
.ai-instruction {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    padding: 18px;
    border-radius: 12px;
    border-left: 5px solid #0284c7;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.15);
}
.input-section {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border: 2px solid #e5e7eb;
}
.divider-colorful {
    height: 3px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border: none;
    margin: 20px 0;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 30px;">
    <h1 style="color: white; font-size: 48px; margin: 0; font-weight: 800;">
        🦴 BONESAGE CHATBOT
    </h1>
    <p style="color: #e0e7ff; font-size: 18px; margin-top: 10px; font-weight: 500;">
        AI-Powered Bone Age Assessment & Clinical Evaluation
    </p>
</div>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="card card-demographics">', unsafe_allow_html=True)
    st.markdown('<div class="section"><span class="section-icon">👤</span> Patient Demographics</div>', unsafe_allow_html=True)
    
    gender = st.radio("**Gender**", ["Female", "Male"], horizontal=True)
    
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
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("**📏 Current Measurements:**")
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Height (cm)", 50.0, 200.0, 130.0, step=0.1, key="current_height")
    with col2:
        weight = st.number_input("Weight (kg)", 2.0, 120.0, 35.0, step=0.1, key="current_weight")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("**📊 6-Month Previous Measurements** (for Growth Velocity Assessment)")
    
    has_previous = st.checkbox("✅ I have measurements from 6 months ago")
    
    if has_previous:
        col3, col4 = st.columns(2)
        with col3:
            height_6m = st.number_input("Height 6m ago (cm)", 50.0, 200.0, 125.0, step=0.1, key="prev_height")
        with col4:
            weight_6m = st.number_input("Weight 6m ago (kg)", 2.0, 120.0, 32.0, step=0.1, key="prev_weight")
    else:
        height_6m = None
        weight_6m = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secondary sexual characteristics
    st.markdown('<div class="card card-sexual">', unsafe_allow_html=True)
    st.markdown('<div class="section"><span class="section-icon">🔬</span> Secondary Sexual Characteristics</div>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="card card-ai">', unsafe_allow_html=True)
    st.markdown('<div class="section"><span class="section-icon">🤖</span> AI Bone Age Assessment</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-instruction">
        <strong style="font-size: 16px; color: #0c4a6e;">📸 Instructions for Best Results:</strong><br>
        <ul style="margin-top: 10px; color: #164e63;">
            <li><strong>Step 1:</strong> Upload hand/wrist X-ray (AP view preferred)</li>
            <li><strong>Step 2:</strong> Click "Analyze with AI" button</li>
            <li><strong>Step 3:</strong> Wait for analysis (approximately 3-5 seconds)</li>
            <li><strong>Step 4:</strong> Review bone age assessment results</li>
        </ul>
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
    st.markdown('<hr class="divider-colorful">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); border-radius: 12px; margin: 20px 0;">
        <h3 style="color: #6d28d9; margin: 0;">🤖 AI Analysis Results</h3>
    </div>
    """, unsafe_allow_html=True)
    components.html(ai_component_html, height=700, scrolling=True)

# ===================== RESULT SECTION =====================
with right:
    st.markdown('<div class="card card-results">', unsafe_allow_html=True)
    st.markdown('<div class="section"><span class="section-icon">📊</span> Clinical Assessment Results</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Generate Clinical Report", use_container_width=True, type="primary"):
        
        # Calculate metrics
        bmi = calculate_bmi(weight, height)
        height_perc = calculate_height_percentile(age, height)
        weight_perc = calculate_weight_percentile(age, weight)
        bone_age_diff = bone_age - age
        
        # Calculate growth velocity if previous data available
        if has_previous and height_6m and weight_6m:
            height_velocity = (height - height_6m) / 0.5  # cm/year
            weight_velocity = (weight - weight_6m) / 0.5  # kg/year
            height_change = height - height_6m
            weight_change = weight - weight_6m
            
            # Normal growth velocity ranges (approximate)
            # Girls 6-8y: 5-6 cm/year, 8-12y: 5-10 cm/year (peak ~8-9 cm/year)
            # Boys 8-10y: 4-6 cm/year, 10-14y: 5-12 cm/year (peak ~9-10 cm/year)
            if gender == "Female":
                if age < 8:
                    normal_velocity_range = "5-6 cm/year"
                    accelerated = height_velocity > 7
                else:
                    normal_velocity_range = "5-10 cm/year"
                    accelerated = height_velocity > 10
            else:  # Male
                if age < 10:
                    normal_velocity_range = "4-6 cm/year"
                    accelerated = height_velocity > 7
                else:
                    normal_velocity_range = "5-12 cm/year"
                    accelerated = height_velocity > 12
        else:
            height_velocity = None
            weight_velocity = None
            accelerated = False
        
        # Display metrics
        if has_previous and height_velocity:
            col1, col2, col3, col4 = st.columns(4)
        else:
            col1, col2, col3 = st.columns(3)
            
        with col1:
            st.markdown(f'<div class="metric-box"><h3>{bmi:.1f}</h3><p>BMI (kg/m²)</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><h3>{bone_age:.1f}</h3><p>Bone Age (yrs)</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><h3>{secondary_count}</h3><p>Sexual Maturity Signs</p></div>', unsafe_allow_html=True)
        
        if has_previous and height_velocity:
            with col4:
                velocity_color = "#dc2626" if accelerated else "#10b981"
                st.markdown(f'<div class="metric-box" style="background: linear-gradient(135deg, {velocity_color} 0%, {velocity_color}dd 100%);"><h3>{height_velocity:.1f}</h3><p>Growth Velocity<br>(cm/year)</p></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Growth Velocity Comparison (if previous data available)
        if has_previous and height_velocity:
            st.markdown("### 📈 Growth Velocity Analysis (6-Month Comparison)")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown(f"""
                **Height Changes:**
                - Current Height: {height:.1f} cm
                - 6 Months Ago: {height_6m:.1f} cm
                - Change: +{height_change:.1f} cm
                - **Growth Velocity: {height_velocity:.1f} cm/year**
                - Normal Range: {normal_velocity_range}
                - Status: {"⚠️ **ACCELERATED**" if accelerated else "✅ Normal"}
                """)
            
            with col_b:
                st.markdown(f"""
                **Weight Changes:**
                - Current Weight: {weight:.1f} kg
                - 6 Months Ago: {weight_6m:.1f} kg
                - Change: +{weight_change:.1f} kg
                - **Weight Velocity: {weight_velocity:.1f} kg/year**
                """)
            
            # Growth velocity visualization
            fig_velocity, (ax_h, ax_w) = plt.subplots(1, 2, figsize=(10, 4))
            
            # Height comparison
            categories_h = ['6 Months Ago', 'Current']
            heights = [height_6m, height]
            colors_h = ['#94a3b8', '#10b981' if not accelerated else '#dc2626']
            
            ax_h.bar(categories_h, heights, color=colors_h, alpha=0.8, edgecolor='black', linewidth=2)
            ax_h.set_ylabel('Height (cm)', fontweight='bold')
            ax_h.set_title('Height Comparison', fontweight='bold', fontsize=12)
            ax_h.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(heights):
                ax_h.text(i, v + 1, f'{v:.1f} cm', ha='center', fontweight='bold')
            
            # Add growth arrow
            ax_h.annotate('', xy=(1, height), xytext=(0, height_6m),
                         arrowprops=dict(arrowstyle='->', lw=2, color='blue', alpha=0.5))
            ax_h.text(0.5, (height + height_6m) / 2, f'+{height_change:.1f} cm\n({height_velocity:.1f} cm/yr)',
                     ha='center', fontsize=10, fontweight='bold', color='blue',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))
            
            # Weight comparison
            categories_w = ['6 Months Ago', 'Current']
            weights = [weight_6m, weight]
            colors_w = ['#94a3b8', '#764ba2']
            
            ax_w.bar(categories_w, weights, color=colors_w, alpha=0.8, edgecolor='black', linewidth=2)
            ax_w.set_ylabel('Weight (kg)', fontweight='bold')
            ax_w.set_title('Weight Comparison', fontweight='bold', fontsize=12)
            ax_w.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(weights):
                ax_w.text(i, v + 0.5, f'{v:.1f} kg', ha='center', fontweight='bold')
            
            # Add growth arrow
            ax_w.annotate('', xy=(1, weight), xytext=(0, weight_6m),
                         arrowprops=dict(arrowstyle='->', lw=2, color='purple', alpha=0.5))
            ax_w.text(0.5, (weight + weight_6m) / 2, f'+{weight_change:.1f} kg\n({weight_velocity:.1f} kg/yr)',
                     ha='center', fontsize=10, fontweight='bold', color='purple',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='plum', alpha=0.7))
            
            plt.tight_layout()
            st.pyplot(fig_velocity)
            
            # Clinical interpretation of growth velocity
            if accelerated:
                st.warning(f"""
                ⚠️ **Accelerated Growth Velocity Detected**
                
                The growth velocity of {height_velocity:.1f} cm/year exceeds the normal range ({normal_velocity_range}) 
                for a {age:.1f}-year-old {gender.lower()}. Accelerated linear growth may indicate:
                - Early pubertal development
                - Growth hormone excess
                - Precocious puberty
                
                This finding **supports the need for endocrinology evaluation** when combined with other clinical signs.
                """)
            
            st.divider()
        
        # Growth Chart
        st.markdown("### 📊 Growth Chart Analysis")
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
        
        analysis_text = f"""
        **📏 Anthropometric Measurements:**
        - Height: {height:.1f} cm ({height_perc})
        - Weight: {weight:.1f} kg ({weight_perc})
        - BMI: {bmi:.1f} kg/m²
        """
        
        if has_previous and height_velocity:
            analysis_text += f"""
        
        **📈 Growth Velocity (6-Month Data):**
        - Height Velocity: {height_velocity:.1f} cm/year (Normal: {normal_velocity_range})
        - Weight Velocity: {weight_velocity:.1f} kg/year
        - Height Change: +{height_change:.1f} cm in 6 months
        - Weight Change: +{weight_change:.1f} kg in 6 months
        - Assessment: {"⚠️ Accelerated Growth" if accelerated else "✅ Normal Growth Pattern"}
        """
        
        analysis_text += f"""
        
        **🦴 Skeletal Maturation Assessment:**
        - Chronological Age: {age:.1f} years ({st.session_state.age_text})
        - Bone Age: {bone_age:.1f} years
        - Bone Age Advancement: {bone_age_diff:+.1f} years
        
        **🔬 Sexual Maturation Status:**
        - Secondary Sexual Characteristics: {secondary_count} signs present
        - Family History: {"Positive" if family_history else "Negative"}
        """
        
        st.markdown(analysis_text)
        
        # Risk Assessment
        risk_level = assess_risk_level(age, gender, secondary_count, bone_age_diff)
        
        # Upgrade risk if accelerated growth velocity is present
        if has_previous and accelerated:
            if risk_level == "low":
                risk_level = "medium"
        
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
        
        if not has_previous:
            st.info("💡 **Growth Velocity Note:** For more comprehensive assessment, obtaining measurements from 6 months ago allows calculation of growth velocity, which is an important indicator of pubertal development and precocious puberty risk.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== FOOTER =====================
st.markdown('<hr class="divider-colorful">', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 15px;'>
    <p style="margin: 0;"><strong style="font-size: 20px; color: #1e293b;">🦴 BONESAGE CHATBOT v3.2</strong></p>
    <p style="color: #475569; margin: 10px 0; font-size: 15px;">Clinical Decision Support Tool | Educational & Screening Purposes Only</p>
    <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 15px;">
        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px;">
            📚 Thai CDC Growth Charts
        </span>
        <span style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px;">
            🌍 WHO Standards
        </span>
        <span style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px;">
            🤖 TensorFlow.js AI
        </span>
    </div>
    <p style='font-size: 11px; margin-top: 15px; color: #64748b;'>
        Developed for medical education and preliminary screening. Not FDA approved for clinical diagnosis.<br>
        Always consult board-certified pediatric endocrinologists for definitive diagnosis and treatment.
    </p>
</div>
""", unsafe_allow_html=True)
