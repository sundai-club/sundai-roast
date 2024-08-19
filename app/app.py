import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv

from image_roaster import get_roasted

# # Define the roast function
# def get_roasted(img):
#     # Placeholder for roast logic
#     # You can replace this with more complex logic or API call
#     return "You call this a selfie? I've seen better reflections in a spoon!"

# Streamlit app
def main():

    # Load .env file
    load_dotenv()

    # Pre-key input UI
    st.title("Sundai Roast")
    st.write("Upload your image and get roasted!")

    # Image upload field
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="uploader")

    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        st.image(img, caption="Here's what you uploaded", use_column_width=True)
    
    # Sidebar for user inputs
    st.sidebar.header("Settings")
    
    # api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.environ["OPENAI_API_KEY"])
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if api_key:
        if not api_key.startswith("sk-"):
            st.warning("Invalid API Key")
            return
        # os.environ["OPENAI_API_KEY"] = api_key
    else:
        st.warning("Please enter your OpenAI API Key")
        return
    
    if uploaded_image is None:
        st.warning("Please upload an image")
        return

    # Roast button
    if uploaded_image is not None and st.button("ROAST ME"):
        roast_text = get_roasted(img, api_key)
        st.write(f"🔥 **Roast:** {roast_text}")

if __name__ == "__main__":
    main()
