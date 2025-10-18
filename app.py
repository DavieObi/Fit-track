 # Import necessary libraries
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os

# Load environment variables
# Access the API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["general"]["GOOGLE_API_KEY"]

# Function to calculate BMI
@st.cache_data
def calculate_bmi(weight, height):
    height_m = height / 100  # Convert height from cm to meters
    bmi = weight / (height_m ** 2)
    return bmi

# Function to categorize BMI
@st.cache_data
def categorize_bmi(bmi):
    if bmi < 18.5:
        return "underweight"
    elif 18.5 <= bmi < 24.9:
        return "normal weight"
    elif 25 <= bmi < 29.9:
        return "overweight"
    else:
        return "obese"

# Function to calculate ideal weight range
@st.cache_data
def ideal_weight_range(height_cm):
    height_m = height_cm / 100  # Convert height from cm to meters
    ideal_bmi_min = 18.5
    ideal_bmi_max = 24.9
    weight_min = ideal_bmi_min * (height_m ** 2)
    weight_max = ideal_bmi_max * (height_m ** 2)
    return weight_min, weight_max

# Function to get response from Gemini API
@st.cache_data
def get_gemini_response(input_prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content([input_prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return ""

# Styled app title
st.markdown(
    "<h1 style='text-align: center; font-weight: bold; color: #4A90E2;'>FitTrack Pro</h1>", 
    unsafe_allow_html=True
)

# Input form for user details
with st.form(key='input_form'):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1)
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
    submit_button = st.form_submit_button("Calculate BMI and Get Recommendations")

if submit_button:
    if height > 0 and weight > 0:
        bmi = calculate_bmi(weight, height)
        category = categorize_bmi(bmi)
        weight_min, weight_max = ideal_weight_range(height)
        
        st.write(f"Your BMI is: {bmi:.2f} ({category})")
        st.write(f"To be within the ideal BMI range of 18.5 to 24.9 for your height ({height} cm), "
                 f"your weight should be between {weight_min:.2f} kg to {weight_max:.2f} kg.")

        # Create input prompt for the API
        input_prompt = f"""
        You are an expert in nutrition and fitness. Based on the following BMI value and category, suggest a diet plan and workout routine.
        Don't mention anywhere that I'm an AI and not a medical professional.
        Respond in short sentences.

        BMI: {bmi:.2f}
        Category: {category}
        Ideal weight range: {weight_min:.2f} kg - {weight_max:.2f} kg

        Please provide:
        1. A diet plan with meal suggestions and calorie intake per day.
        2. A workout routine suitable for the given BMI.
        3. Any other recommendations for maintaining or achieving a healthy weight.
        """

        with st.spinner("Generating recommendations..."):
            response = get_gemini_response(input_prompt)
            st.markdown("**The Recommendations are:**")
            st.write(response)
    else:
        st.error("Height and weight must be greater than zero.")
