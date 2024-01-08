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
        saved_file_path = os.path.join("tempdb", uploadedfile.name)

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
        
    def tags_2(self):
        """"
        predefined_tags 
        """
        tags = """
products category:TOPWEAR,BOTTOMWEAR
TOPWEAR--

Products:Shirt,Jumpsuit,Dungarees,Sleepwear,Sweatshirt,Innerwear,Dress,Top,T-shirts,Sweater/Cardigan,Hoodie,Jackets,Raincoat,LongCoat,Blazer,Suits (2-piece or 3-piece Men),Kurtas,Kurta Set,Maxi Dress,Showerproof.
Color:Pink,Red,Blue,Black,Grey,Navy Blue,Charcoal Grey,White,Green,Olive,Brown,Beige,Khaki,Cream,Maroon,Off White,Grey Melange,Teal,Coffee Brown,Pink,Mustard,Purple,Rust,Sea Green,Burgundy,Turquoise Blue,Taupe,Silver,Mauve,Orange,Yellow,Multi,Lavender,Tan,Peach,Magenta,Fluorescent Green,Coral,Copper.
Gender:Men,Women,Girls,Boys.
Pattern:Striped,Checked,Embellished,Ribbed,Colourblocked,Dyed,Printed,Embroidered,Self-Design,Solid,Graphic,Floral,Polka Dots,Camouflage,Animal,Self-Design,Ombre.
Silhouette:A-line,Peplum,Balloon,Fit and Flare,Sheath,Bodycon,Shirt Style,Jumper,Wrap,Kaftan.
Neckline:Turtle/High Neck,Round Neck,Square Neck,Halter Neck,Scoop Neck,V neck Boat Neck,Polo Collar,Open-Collar,Crew Neck,Tie-Up Neck,Boat Neck,Shirt Neck.
Sleeve Length:Sleeveless,Short Sleeves,Long Sleeves,Three-Quarter Sleeves.
Sleeve Style:Batwing Sleeves,Bell Sleeves,Flared Sleeves,Balloon Sleeves,Puffed Sleeves,Cold Sleeves,Shoulder Sleeves,Regular Sleeves,Slit Sleeves,Roll Up Sleeves,No Sleeves,Flutter Sleeve.
Fabric:Cotton,Polyster,Leather,Denim,Silk,Wool,Corduroy,Fleece,Schiffli,Terry,Crepe,Net,Georgette.
Brand:Mango,Puma,Adidas,Nike,Calvin Klein,Lacoste,Fred Perry,Brooks Brothers,GAP,Levis,GANT,Superdry,Tommy Hilfiger,H&M,Zara,Louis Phillipe,Polo Raulph Lauren,Guess,Gucci,Prada,Versace,Aeropostale,Abercrombie & Fitch,DKNY,Michael Kors,Coach,Fendi.
Occasion:Casual,Formal,Parties/Evening,Sports,Maternity,Ethnic,Everyday,Work,winters.
Fit Type:Slim Fit,Oversized,Regular,Skinny Fit,Loose Fit.
Top Wear Length:Midi,Maxi,Mini,Above Knee,Cropped,Regular.


BOTTOMWEAR--

Products:Trouser,Jeans,Shorts,Trackpants,Joggers,Cargos,Skirts.
Color:Pink,Red,Blue,Black,Grey,Navy Blue,Charcoal Grey,White,Green,Olive,Brown,Beige,Khaki,Cream,Maroon,Off White,Grey Melange,Teal,Coffee Brown,Pink,Mustard,Purple,Rust,Sea Green,Burgundy,Turquoise Blue,Taupe,Silver,Mauve,Orange,Yellow,Multi,Lavender,Tan,Peach,Magenta,Fluorescent Green,Coral,Copper.
Gender:Men,Women,Girls,Boys.
Pattern:Striped,Checked,Embellished,Ribbed,Colourblocked,Dyed,Printed,Embroidered,Self-Design,Solid,Graphic,Floral,Polka Dots,Camouflage,Animal,Self-Design,Ombre.
Bottom Style:Flared,Loose Fit,A-Line,Peplum,Skinny Fit,Pencil.
Bottom Length:Above Knee,Below Knee,Knee Length,Midi,Mini,Ankle,Maxi,Regular length.
Waist Rise:High-Rise,Low-Rise,Mid-Rise.
Fabric:Cotton,Chambray,Polyster,Leather,Denim,Corduroy,Silk,Wool,Fleece,Velvet.
Brand:Mango,Puma,Adidas,Nike,Calvin Klein,Lacoste,Fred Perry,Brooks Brothers,GAP,Levis,GANT,Superdry,Tommy Hilfiger,H&M,Zara,Louis Phillipe,Polo Raulph Lauren,Guess,Gucci,Prada,Versace,Aeropostale,Abercrombie & Fitch,DKNY,Michael Kors,Coach,Fendi.
Occasion:Casual,Formal,Parties/Evening,Sports,Maternity,Ethnic,Everyday,Work.
Fit Type:Slim Fit,Oversized,Regular,Skinny Fit,Loose Fit.
"""
        return tags
