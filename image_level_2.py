from utility import MultiModel, Processing
import yaml
import streamlit_shadcn_ui as ui
import streamlit as st
import os
from PIL import Image
import pandas as pd
from PIL import Image
import ast
import shutil
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_js_eval import streamlit_js_eval
st.set_option('deprecation.showPyplotGlobalUse', False)
# from streamlit_react_flow import react_flow

######################################## Read env variables #########################################
with open("env.yml", 'r') as file:
    data = yaml.safe_load(file)

############################################### Header #############################################
# Page Settings
page_config = {"page_title": "IntelliTags.io", "layout": "wide"}
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
    """, unsafe_allow_html=True)  # ed4965
############################################### Sidebar LOGO #############################################
# Sidebar logo
with st.sidebar:
    st.markdown("""<div style='text-align: left; margin-top:-60px;margin-left:-40px;'>
    <img src="https://affine.ai/wp-content/uploads/2023/12/4.gif" alt="logo" width="300" height="60">
    </div>""", unsafe_allow_html=True)


############################################### Columns #############################################
# col1 : image and col2: attribute name
col1, col2 = st.columns([0.5, 1], gap="large")

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

# Check if "Product_listed" is in the session state
if "Product_listed" not in st.session_state:
    # If it's not, initialize it to an empty dictionary
    st.session_state.Product_listed = []
    
if "flag" not in st.session_state:
    st.session_state.flag=False

## automatically clear the temporary storage
if st.session_state.flag==False:
    if os.path.exists("tempdb"):
        shutil.rmtree("tempdb") 
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Cleard the temporary storage")
    st.session_state.flag=True
############################################### GPT-4 Vision Model #############################################

vision_model = MultiModel(api_key=data['api_key'], temp=0)

############################################### Sidebar#############################################
# All extra method present in this module
process = Processing()

with st.sidebar:
    # Create a file uploader widget that accepts png, jpeg, jpg, and webp files
    image_file = st.file_uploader("Upload An Image", type=[
                                  'png', 'jpeg', 'jpg', 'webp'])

    # Check if a file has been uploaded
    if image_file is not None:
        if not os.path.exists("tempdb"):
            os.mkdir("tempdb")
        # Construct the path where the uploaded file will be saved
        # saved_file_path = f"{data['saved_img_dir']}/{image_file.name}"
        # Store the file name and type in a dictionary
        file_details = {"FileName": image_file.name,
                        "FileType": image_file.type}
        # Open the uploaded image file
        image = Image.open(image_file)
        # Resize the image to 300x400 pixels
        new_image = image.resize((300, 400))
        # Display the resized image in the Streamlit app
        with col1:
            st.image(new_image)
        # Save the uploaded file and store the path in the session state
        st.session_state.saved_img_path = process.save_uploadedfile(image_file)
    else:
        # If no file has been uploaded, let the user select an image from the "images/" directory
        selected_images = st.selectbox("Select Image", os.listdir(
            r"{0}/".format(data['images_dir_path'])))
        # Construct the path to the selected image and store it in the session state
        st.session_state.saved_img_path = r"{0}/{1}".format(
            data['images_dir_path'], selected_images)
        # Open the selected image file
        image = Image.open(st.session_state.saved_img_path)
        # Resize the image to 300x400 pixels
        new_image = image.resize((300, 400))
        # Display the resized image in the Streamlit app
        with col1:
            st.image(new_image)
    # Create a submit button
    submit = st.button("Submit")
    # st.info("Press the Delete button below to clear the temporary storage")
    # delete=st.button("Delete")

# if delete:
#     shutil.rmtree("tempdb")
#     with st.sidebar:
#         st.success("All temporary images deleted successfully.")

############################################## GPT4 Vision model Calling #################################
if submit:
    # predefined set of tags
    tags = process.tags_2()

    # model prompt
    # Given is the image of clothing catalog.Your task is to identify items or products of clothing only which is in focus from a given image and based on the identified items or products
    prompt = f"""
1. Accurately identify the topwear and/or bottomwear that is IN FOCUS AND CAPTURED FULLY within a given catalog image. Find the metadata for identified clothing worn, from this below information:\n{tags}""" + """and mention them in a list of structured json format.
2. metadata JSON should consist of the following keys:
      [{"products category":str,Products:str,Color:str,Gender:str,Pattern:str,Silhouette:str,Neckline:str,Sleeve Length:str,Sleeve Style:str,Fabric:str,Brand:str,Occasion:str,Fit Type:str,Top Wear Length:str}]
3. The color recognition tags provide a limited color range. However, you have the flexibility to label additional colors as required. if multi color, put all possible color in str using comma(',').
4. Refrain from adding any extra comments into the JSON output.
5. Do not forgot to add Gender and Material Composition Type based on identified products.
6. Correctly map tags with specified entities.
7. Do not extract the metadata of Topwear or Bottomwear that is not fully in focus a given catalog image. For Example: In Bottomwear Jeans present but it is not fully visible/focus in the image do not extract bottom wear metadata in such cases.
8. If any information is not available related to any item/product in the image, please use 'N/A' as a placeholder."""
# [{Product Type/Categories:str,Products:str,Color Recognition:str,Gender:str,Pattern Detection:str,Silhouette Classification:str,Neckline Identification:str,Sleeve Style Identification:str,Material Composition Type:str,Brand Logo/Label Recognition:str,Occasion Suitability:str,Size and Fit Assessment:str}]
    # Call the Gpt 4 vision model to pass prompt and image path
    output = vision_model.gpt4v_img(
        prompt, image_path=st.session_state.saved_img_path)
    # Check the list of products extracted or not
    if '[' in output['final_response'] and "]" in output['final_response']:
        print("Products identified in the image")
        # Extract only list of products from the string
        # Convert the 'final_response' string from 'output' dictionary into a list of dictionaries.
        # 'ast.literal_eval' safely parses an expression node or a string containing a Python literal or container display.
        # The string is sliced from the first occurrence of "[" to the last occurrence of "]" + 1.
        st.session_state.output_list_dict = ast.literal_eval(
            output['final_response'][output['final_response'].find("["):output['final_response'].find("]")+1])
        # st.session_state.product_dict = {}
        # Loop through each dictionary in the 'output_list_dict' list.
        # st.write(st.session_state.output_list_dict)
        print('='*50)
        print(st.session_state.output_list_dict)
        print('='*50)
        st.session_state.product_dict = {}
        #  st.session_state.product_dict = {}
        st.session_state.Product_listed = []
        for dict1 in st.session_state.output_list_dict:
            for keys in dict1.keys():
                if keys=="products category":
                    st.session_state.product_dict[dict1[keys]] = dict1
                    st.session_state.Product_listed.append(dict1[keys])
        print("+"*50)
        print(st.session_state.product_dict)
        print("+"*50)
    else:
        with col2:
            st.error("Please upload a relevant product image")
# st.write(st.session_state.Product_listed)
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
# st.write(st.session_state.dict)
# st.write(st.session_state.Product_listed)
############################################## Output #################################
if len(st.session_state.Product_listed) != 0:
    print("------------------------------Option tabs------------------------")
    print(st.session_state.Product_listed)
    print("-----------------------------------------------------------------")
    with col2:
        
        select_tabs = ui.tabs(options=st.session_state.Product_listed,
                              default_value=st.session_state.Product_listed[0], key="main_tabs")
        if select_tabs in st.session_state.Product_listed:
            index = st.session_state.Product_listed.index(select_tabs)
            if select_tabs == st.session_state.Product_listed[index]:
                product_dict1 = {"Categories": [], "Attributes": []}
                for key,value in st.session_state.product_dict[select_tabs].items():
                    if value!='N/A' and key!="products category":
                        product_dict1['Categories'].append(key)
                        product_dict1['Attributes'].append(value)
                    else:
                        print(f"{key} :: {value}")
                ui.table(data=pd.DataFrame(
                    (product_dict1)),maxHeight=20)
        else:
            with col2:
                st.error("Please refresh the webpage and try uploading the image again.")
                st.info("If you encounter any errors, please click the ‘Refresh’ button.")
                refresh=st.button("Refresh")
                if refresh:
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")
############################################################## END #####################################################################################
