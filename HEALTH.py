from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt,image):
    """
    Sends the user's prompt and  an image to the Gemini model to get a response
    """
    model=genai.GenerativeModel('gemini-1.5-pro')
    response=model.generate_content([input_prompt,image[0]])
    return response.text
def input_image_setup(uploded_file,captured_image_bytes):
    """
    Prepare the uploaded image file or caputured image for the Gemini API call.
    """
    
    if uploded_file is not None:
       bytes_data=uploded_file.getvalue()
       mime_type=uploded_file.type
    elif captured_image_bytes is not None:
       bytes_data=captured_image_bytes
       mime_type="image/jpeg "
    else:
       raise FileNotFoundError("No file is uploded or image captured")
    
    image_parts=[
        {
            "mime_type": mime_type,
            "data": bytes_data
        }
    ]   
    return image_parts
       
st.set_page_config(page_title="Personlized Calories Advisor App")
st.header("Personlized Calories Advisor App")

st.markdown("Analyzed your meal and get a personlize diet plan.") 

st.subheader("Your personal details")
age=st.number_input("Age", min_value=1, max_value=120,value=25)
sex=st.selectbox("Sex",("male","female"))
height=st.number_input("Height (cm)", min_value=50, max_value=300, value=170)
weight=st.number_input("Weight (kg)", min_value=10, max_value=500, value=70)
activity_level = st.selectbox(
    "Activity Level",
    ("Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active")
)
health_goal=st.selectbox(
    "Health Goal",
   ("Maintain weight","loss weight","gain weight", "muscle gain")
)


st.subheader("Your Meal")
source = st.radio("Choose image source:",("Upload an image","Take a picture"))

uploaded_file =None
captured_image_bytes  = None
image = None
 
if source == "Upload an image":
    uploaded_file = st.file_uploader("Choose an image of your meal...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Meal Image.", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")
else:  # Take a picture
    captured_image = st.camera_input("Take a picture of your meal")
    if captured_image:
        captured_image_bytes = captured_image.getvalue()
        # Optionally display the captured image
        st.image(captured_image, caption="Captured Meal Image.", use_container_width=True)     

submit = st.button("Get My Personalized Plan")

if submit:
    if uploaded_file is None and captured_image_bytes is None:
        st.warning("Please upload a food image or take a picture to proceed.")
    else:
        try:
            image_data = input_image_setup(uploaded_file, captured_image_bytes)        

            input_prompt=f"""
            Your are an expert nutritionist who can analyze a meal from an image to provide a detailed personalised health plan.
           
             First,please identify all the food items in the image and estimate the total calorise. provide a list with calorise 
            
            based on the user following details, provide a personalized diet and exercise recommendation. 

            -Age: {age} years
            -Sex: {sex}
            -Height: {height} cm
            -Weight: {weight} kg
            -Activity Level: {activity_level}
            -Health Goal: {health_goal}

            Structure your response in two parts:
             1. **Meal Analysis & Calories:**
                - Item 1 - no of calories
                - Item 2 - no of calories
                - ...
                - Total Estimated Calories: [Total]
            2. **Personalized Recommendation:**
                - Provide a short summary of the user's estimated daily calorie needs based on their details and goal.
                - Give practical advice on how to adjust their diet (e.g., portion sizes, food types).
                - Suggest a simple exercise plan to help them achieve their goal.
            """

            with st.spinner("Analyzing your meal and generating your personalized plan...  "):
                response = get_gemini_response(input_prompt,image_data)

            st.subheader("Your Personalized Health Report ")
            st.write(response)


        except FileNotFoundError as fnfe:
            st.error(str(fnfe))

        except Exception as e:


            st.error(f"An error occured: {e}")        
