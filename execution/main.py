import os
import streamlit as st
from ultralytics import YOLO

st.title("Upload YOLO Model from Folder Path")

# Step 1: Input folder path
folder_path = st.text_input("Enter the absolute path of the folder containing the model file (.pt):")

if folder_path:
    # Step 2: Validate the folder path
    if os.path.isdir(folder_path):
        st.success(f"Folder found: {folder_path}")
        
        # Step 3: List .pt files in the folder
        pt_files = [f for f in os.listdir(folder_path) if f.endswith('.pt')]
        if pt_files:
            selected_file = st.selectbox("Select a model file:", pt_files)
            
            # Get absolute path of the selected file
            model_path = os.path.join(folder_path, selected_file)
            st.write(f"Absolute path of selected file: `{model_path}`")
            
            # Step 4: Load and display YOLO model
            if st.button("Load YOLO Model"):
                try:
                    model = YOLO(model_path)
                    st.success(f"YOLO model `{selected_file}` loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading model: {e}")
        else:
            st.warning("No `.pt` files found in the specified folder.")
    else:
        st.error("Invalid folder path. Please provide a valid absolute path.")

# Optional: Display instructions
st.markdown("""
### Instructions:
1. Enter the absolute path of a folder containing your `.pt` YOLO model file.
2. Select a model file from the dropdown (if found).
3. Click "Load YOLO Model" to load the selected model.
""")
