import os
import base64
import requests
import time
import streamlit as st

class MultiModel():
    """
    A class to interact with the GPT-4 Vision model.

    Attributes:
        api_key (str): The API key for authentication.
        temp (float): The temperature parameter for the model. Default is 0.
    """
    def __init__(self,api_key,temp=0):
        """
        The constructor for the MultiModel class.
        """
        self.api_key=api_key
        self.temp=temp
        
    def gpt4v_img(self,prompt,image_path,max_tokens:int=4000):
        """
        Method to generate a response from the GPT-4 Vision model.

        Parameters:
            prompt (str): The prompt for the model.
            image_path (str): The path to the image file.
            max_tokens (int): The maximum number of tokens for the model to generate. Default is 4000.

        Returns:
            dict: A dictionary containing the model's response and inference time.
        
        """
        def encode_image(image_path):
            """
            Function to encode an image file into base64 format.

            Parameters:
                image_path (str): The path to the image file.

            Returns:
                str: The base64 encoded string of the image.
            """
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Getting the base64 string
        base64_image = encode_image(image_path)

        headers = {
          "Content-Type": "application/json",
          "Authorization": f"Bearer {self.api_key}"
              }

        payload = {
              "model": "gpt-4-vision-preview",
              "messages": [
                    {"role": "user", "content": [{"type": "text", "text": f"{prompt}"},
                                                 {"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}","detail": "high"}}]
                    }],
              "max_tokens": max_tokens,
            "temperature":self.temp
                }
        
        start=time.time()
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        end=time.time()
        ## Calculate the inferance time
        latency=end-start
        ## Lets Find only Final model response
        result = response.json()['choices'][0]['message']['content']
        return {"final_response":result,"inferance_time":latency}
    
class Processing():
    def __init__(self):
        pass

    def save_uploadedfile(self,uploadedfile):
        """
        Function to save an uploaded file.

        Parameters:
            uploadedfile: The file uploaded by the user.

        Returns:
            str: The path where the file is saved.
        """

        # Join the directory "images" and the name of the uploaded file to form the path where the file will be saved
        saved_file_path = os.path.join("images", uploadedfile.name)

        # Open the file in write mode
        with open(saved_file_path, "wb") as f:
            # Write the contents of the uploaded file to the new file
            f.write(uploadedfile.getbuffer())
            # Display a success message in the Streamlit app
            st.success("Saved File: {} to tempDir".format(uploadedfile.name))

        # Return the path where the file is saved
        return saved_file_path
    def tags(self):
        """"
        predefined_tags 
        """
        tags="""Product Type/Categories:Clothing,Footwear,Accessories.
Products:Shirt,Trouser,Jeans,Shorts,Trackpants,Joggers,Sleepwear,Innerwear,Dress,One-Piece,Top,Sweatshirt,T-shirts,Sweater/Cardigan,Gloves,Sweater Skirt,Hoodie,Jackets,Raincoat,LongCoat,Blazer,Suits (2-piece or 3-piece Men),Kurtas,Kurta Set,shooes,sandals,Flip Flop & Slippers,Cap.
Color Recognition:Pink,Red,Blue,Brown,yellow,white,Green, Simply Green,Larkspur Blue,Gray,Orange, Crimson,Cyan,,Coral,Navy Blue,Magneta,gold,Teal,Canary,Lime Green, Dark Blue.
Gender: Men,Women,Girls,Boys,Baby,Unisex.
Pattern Detection: Striped,Checked,Ribbed,Colourblocked,Dyed,Printed,Embroidered,Self-Design,Solid,Soft knit,Cable-Knit.
Silhouette Classification: A-line,Fit and Flare,Sheath,Bodycon,Straight.
Neckline Identification: Turtle/High Neck,Round Neck,Square Neck,Halter Neck,Scoop Neck,V neck, Boat Neck,Polo Collar,Crewneck.
Sleeve Style Identification: Sleeveless,Short Sleeves,Long Sleeves,Three-Quarter Sleeves.
Material Composition Type : Cotton,Polyster,Leather,Denim,Silk,Wool,Acrylic,Nylon,Rayon,Wool.
Brand Logo/Label Recognition: Mango,GAP,Levis,GANT,Superdry,Tommy Hilfiger,H&M,Zara,Louis Phillipe,Polo Raulph Lauren,Guess,Gucci,Prada,Versace,Aeropostale,Abercrombie & Fitch,DKNY,Michael Kors,Coach,Fendi, Brooks Brothers.
Occasion Suitability: Casual,Formal,Parties/Evening,Sports,Maternity,Ethnic,Everyday,Work,HOLIDAY.
Size and Fit Assessment: Slim Fit,Oversized,Regular,Skinny Fit,Loose Fit,easy fit."""
        return tags
