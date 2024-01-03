import streamlit as st
import os
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
page_config = {"page_title":"items.io","layout":"wide"}
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
    st.session_state.saved_img_path=None

# Check if "output_list_dict" is in the session state
if "output_list_dict" not in st.session_state:
    st.session_state.output_list_dict=None

# Check if "product_list" is in the session state
if "product_list" not in st.session_state:
    # If it's not, initialize it to an empty list
    st.session_state.product_list=[]

# Check if "product_dict" is in the session state
if "product_dict" not in st.session_state:
    # If it's not, initialize it to an empty dict
    st.session_state.product_dict={}


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
        selected_images=st.selectbox("Select Image",os.listdir("{0}".format(data['saved_img_dir'])))
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

    ## model prompt
    prompt=f"""Your task is to identify items or products of clothing,footwear and accessories from a given image and based on the identified items or products find the metadata for each item or product from this below information:\n{tags}""" + """and mention them in a list of structured json format.
1. metadata JSON should consist of the following keys:
    [{Product Type:str,Products:str,Color:str,Gender:str,Pattern:str,Silhouette:str,Neckline:str,Sleeve and Length:str,Fabric:str,Brand:str,Occasion:str,Size and Fit Assessment:str}]
2. After identifying the items/products in the image, create the corresponding metadata.
3. The color recognition tags provide a limited color range. However, you have the flexibility to label additional colors as required.
4. Refrain from adding any extra comments into the JSON output.
5. Do not forgot to add Gender and Material Composition Type based on identified products.
6. If any information is not available related to any item/product in the image, please use 'N/A' as a placeholder."""

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
        # Loop through each dictionary in the 'output_list_dict' list.
        for dict1 in st.session_state.output_list_dict:
            # check for the products in the dictionary
            if "Products" in dict1.keys():
                # identified the list of products saved separately
                st.session_state.product_list.append(dict1['Products'])
                # save the new product wise dictionary
                st.session_state.product_dict[dict1['Products']]=dict1


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

st.markdown("""
<style>
[data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock] {
    gap: 0rem;
    padding-top: -100px;
}   
</style>
""", unsafe_allow_html=True)



if len(st.session_state.product_list)!=0:
    with col2:
        select_tabs=ui.tabs(options=st.session_state.product_list, default_value=st.session_state.product_list[0], key="main_tabs")
        total0,total1,total2=st.columns(3,gap='small')
        total3,total4,total5=st.columns(3,gap='small')
        total6,total7,total8=st.columns(3,gap='small')
        total9,total10,total11=st.columns(3,gap='small')
        list1=[total0,total1,total2,total3,total4,total5, total6,total7,total8,total9,total10,total11]
        index=st.session_state.product_list.index(select_tabs)
        if select_tabs==st.session_state.product_list[index]:
            selected_dict=[i for i in list(st.session_state.product_dict[select_tabs].items()) if i[1]!='N/A']
            list3 = list(zip(list1, selected_dict))
            for col,values in list3:
                with col:
                    # st.info('Sum Investment',icon="💰")
                    st.metric(label=values[0],value=values[1])
    style_metric_cards(background_color="#FFFFFF",border_left_color="red",border_color="#000000",box_shadow="#F71938")
