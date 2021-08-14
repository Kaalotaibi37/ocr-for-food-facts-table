import streamlit as st
import os
import sys
import base64
import pandas as pd
from io import BytesIO
from PIL import Image
from pathlib import Path
import shutil
from main2 import *
#import app

st.set_page_config(layout='wide')
col1, col2, col3, col4 = st.columns((3,0.5,1,3))


STYLE = """
<style>
img {max-width: 100%;}
div.stButton > button:first-child {height:3em;width:10em;font-size:15px}
<style> """

file = None
spectra = None

def main():

    global file
    
    with col1:
     #st.info(__doc__)
     st.markdown(STYLE, unsafe_allow_html=True)
     st.header("OCR for Food Facts Table")
     st.markdown('##')
     file=st.file_uploader("Upload File", type=["png","jpg"])
     show_file=st.empty()

    if not file:
        show_file.info("Please upload a file : {} ".format(''.join(["png ,"," jpg"])))
        return
    content__=file.getvalue()

    if isinstance(file, BytesIO):
        show_file.image(file)

    if file is not None:
        spectra = None
        if (os.path.exists(os.path.join("tmp/Images/"))):
                shutil.rmtree(os.path.join("tmp/Images/"))
                shutil.rmtree(os.path.join("tmp/Results/"))
        if not(os.path.exists(os.path.join("tmp/Images/"))):
            os.makedirs(os.path.join("tmp/Images/")) 
            os.makedirs(os.path.join("tmp/Results/")) 
        file_details = {"FileName":file.name,"FileType": file.type}
        st.write(file_details)
        img = load_image(file)
       # st.image(img,height=250,width=250)
        with open(os.path.join("tmp/Images/",file.name),"wb") as f: 
            f.write(file.getbuffer())  
        
    file_path =   os.path.join("tmp/Images/",file.name)  
    
    #do_tesseract(image_dir, res_dir)
   # parse_txt(res_dir)
   # if os.path.exists(os.path.join("tmp/Images/")):
   #         shutil.rmtree(os.path.join("tmp/Images/"))
   #         shutil.rmtree(os.path.join("tmp/Results/"))

   # file.close()
   # show_data()

def download_link(object_to_download, download_filename, download_link_text):
  
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def show_data():
    global spectra
    spectra = pd.read_csv (os.path.join("tmp/output.csv"),usecols= ['Nutrient','Amount','Unit','Serving size', 'Serving size unit'])
    if spectra is not None:
        with col4:
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            st.dataframe(spectra)
    tmp_download_link = download_link(spectra, 'output.csv', 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)

with col3:

    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    if st.button('Convert'):
        
            do_tesseract(image_dir, res_dir)
            parse_txt(res_dir)
            if os.path.exists(os.path.join("tmp/Images/")):
                shutil.rmtree(os.path.join("tmp/Images/"))
                shutil.rmtree(os.path.join("tmp/Results/"))
            show_data()

with col4:
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
    st.markdown('##')
   


def load_image(image_file):
    img = Image.open(image_file)
    return img


main()