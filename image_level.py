import streamlit as st
import os
from PIL import Image
import pandas as pd
from PIL import Image
import ast
from streamlit_extras.metric_cards import style_metric_cards
st.set_option('deprecation.showPyplotGlobalUse', False)
# from streamlit_react_flow import react_flow
import streamlit_shadcn_ui as ui
from utility import MultiModel,Processing
import yaml

######################################## Read env variables #########################################
with open("env.yml", 'r') as file:
        data = yaml.safe_load(file)

############################################### Header #############################################
## Page Settings
page_config = {"page_title":"image.io","layout":"wide"}
st.set_page_config(**page_config)
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; margin-top:-90px; margin-bottom: 5px;margin-left: -50px;'>
    <h2 style='font-size: 60px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
    <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    IntelliTags
    </span>
    <span style='font-size: 60%;'>
    <sup style='position: relative; top: 5px; color:white ;'>by Affine</sup> 
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True) #ed4965
############################################### Sidebar LOGO #############################################
## Sidebar logo
with st.sidebar:
    st.markdown("""<div style='text-align: left; margin-top:-60px;margin-left:-40px;'>
    <img src="https://affine.ai/wp-content/uploads/2023/12/4.gif" alt="logo" width="300" height="60">
    </div>""", unsafe_allow_html=True)


############################################### Columns #############################################
##  col1 : image and col2: attribute name
col1,col2=st.columns([0.5,1],gap="large")

############################################### Session State #############################################

# Streamlit's Session State allows you to store information across multiple runs of your app, 
# which can be useful for maintaining the state of your app or for caching.


# Check if "saved_img_path" is in the session state
if "saved_img_path" not in st.session_state:
    # If it's not, initialize it to None
    st.session_state.saved_img_path = None


# Check if "output_list_dict" is in the session state
if "output_list_dict" not in st.session_state:
    # If it's not, initialize it to None
    st.session_state.output_list_dict = None

# Check if "product_dict" is in the session state
if "product_dict" not in st.session_state:
    # If it's not, initialize it to an empty dictionary
    st.session_state.product_dict = {}

# Check if "product_dict1" is in the session state
if "product_dict1" not in st.session_state:
    # If it's not, initialize it to an empty dictionary
    st.session_state.product_dict1 = {}

############################################### GPT-4 Vision Model #############################################

vision_model=MultiModel(api_key=data['api_key'],temp=0)

############################################### Sidebar#############################################
# All extra method present in this module
process=Processing()

with st.sidebar:
    # Create a file uploader widget that accepts png, jpeg, jpg, and webp files
    image_file = st.file_uploader("Upload An Image", type=['png', 'jpeg', 'jpg','webp'])

    # Check if a file has been uploaded
    if image_file is not None:
        # Construct the path where the uploaded file will be saved
        saved_file_path=f"{data['saved_img_dir']}/{image_file.name}"
        # Store the file name and type in a dictionary
        file_details = {"FileName": image_file.name, "FileType": image_file.type}
        # Open the uploaded image file
        image = Image.open(image_file)
        # Resize the image to 300x400 pixels
        new_image = image.resize((300, 400))
        # Display the resized image in the Streamlit app
        with col1:
            st.image(new_image)
        # Save the uploaded file and store the path in the session state
        st.session_state.saved_img_path=process.save_uploadedfile(image_file)
    else:
        # If no file has been uploaded, let the user select an image from the "images/" directory
        selected_images=st.selectbox("Select Image",os.listdir(r"{0}/".format(data['images_dir_path'])))
        # Construct the path to the selected image and store it in the session state
        st.session_state.saved_img_path=r"{0}\{1}".format(data['images_dir_path'],selected_images)
        # Open the selected image file
        image = Image.open(st.session_state.saved_img_path)
        # Resize the image to 300x400 pixels
        new_image = image.resize((300, 400))
        # Display the resized image in the Streamlit app
        with col1:
            st.image(new_image)
    # Create a submit button
    submit=st.button("Submit")


############################################## GPT4 Vision model Calling #################################    
if submit:
    ## predefined set of tags
    tags=process.tags()
    print(tags)
    ## model prompt
    prompt=f"""Your task is to identify items or products of clothing,footwear and accessories from a given image and based on the identified items or products find the metadata for each item or product from this below information:\n{tags}""" + """and mention them in a list of structured json format.
1. metadata JSON should consist of the following keys:
    [{Product Type:str,Products:str,Color:str,Gender:str,Pattern:str,Silhouette:str,Neckline:str,Sleeve and Length:str,Fabric:str,Brand:str,Occasion:str,Size and Fit Assessment:str}]
2. After identifying the items/products in the image, create the corresponding metadata.
3. The color recognition tags provide a limited color range. However, you have the flexibility to label additional colors as required.
4. Refrain from adding any extra comments into the JSON output.
5. Do not forgot to add Gender and Material Composition Type based on identified products.
6. If any information is not available related to any item/product in the image, please use 'N/A' as a placeholder."""
#[{Product Type/Categories:str,Products:str,Color Recognition:str,Gender:str,Pattern Detection:str,Silhouette Classification:str,Neckline Identification:str,Sleeve Style Identification:str,Material Composition Type:str,Brand Logo/Label Recognition:str,Occasion Suitability:str,Size and Fit Assessment:str}]
    # Call the Gpt 4 vision model to pass prompt and image path
    output=vision_model.gpt4v_img(prompt,image_path=st.session_state.saved_img_path)
    ## Check the list of products extracted or not
    if '[' in output['final_response'] and "]" in output['final_response']:
        print("Products identified in the image")
        # Extract only list of products from the string
        # Convert the 'final_response' string from 'output' dictionary into a list of dictionaries.
        # 'ast.literal_eval' safely parses an expression node or a string containing a Python literal or container display.
        # The string is sliced from the first occurrence of "[" to the last occurrence of "]" + 1.
        st.session_state.output_list_dict = ast.literal_eval(output['final_response'][output['final_response'].find("["):output['final_response'].find("]")+1])
        print("+"*50)
        print(st.session_state.output_list_dict)
        print("+"*50)
        st.session_state.product_dict={}
        # Loop through each dictionary in the 'output_list_dict' list.
        for dict1 in st.session_state.output_list_dict:
            # Loop through each key in the dictionary.
            for key in dict1.keys():
                # If the key is not already in the 'product_dict' dictionary, add it.
                if key not in st.session_state.product_dict.keys():
                    # Initialize the key with an empty list.
                    st.session_state.product_dict[key] = []
                    # Append the value corresponding to the key from 'dict1' to the list.
                    st.session_state.product_dict[key].append(dict1[key])
                else:
                    # If the key is already in the 'product_dict' dictionary, append the value to the existing list.
                    st.session_state.product_dict[key].append(dict1[key])

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 15px;
    font-weight: bold;
}
</style>
""",
    unsafe_allow_html=True,
)

############################################## Output #################################  
# Check if 'product_dict' is not empty.
if len(st.session_state.product_dict) != 0:
    # Loop through each key in 'product_dict'.
    for key in st.session_state.product_dict:
        # Convert the list of values for each key into a set to remove duplicates, then convert it back into a list.
        st.session_state.product_dict[key] = list(set(st.session_state.product_dict[key]))

    # Create a new dictionary 'product_dict1' with two keys: 'Categories' and 'Attributes Detected', each mapping to an empty list.
    with col2:
        st.session_state.product_dict1 = {"Categories": [], "Attributes": []}
        # Loop through each key-value pair in 'product_dict'.
        for attribute, keyword in st.session_state.product_dict.items():
            print("#" * 50)
            print("keywords", keyword)
            print("#" * 50)
            # If "N/A" is in the list of keywords, remove it.
            if "N/A" in keyword:
                keyword.remove("N/A")
            # If the list of keywords is not empty after removing "N/A".
            if len(keyword) != 0:
                # Append the attribute to the 'Categories' list in 'product_dict1'.
                st.session_state.product_dict1['Categories'].append(attribute)
                # Join the keywords into a string with ', ' as the separator, and append the string to the 'Attributes Detected' list in 'product_dict1'.
                st.session_state.product_dict1['Attributes'].append(f"{', '.join(set([key for key in keyword if key != 'N/A']))}")
        # Display 'product_dict1' as a table using the 'ui.table' function. The data is converted into a pandas DataFrame first.
        ui.table(data=pd.DataFrame(st.session_state.product_dict1), maxHeight=300)


############################################################## END #####################################################################################



        

