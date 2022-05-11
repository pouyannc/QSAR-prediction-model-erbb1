import streamlit as st #web framework
import pandas as pd 
from PIL import Image #illustration
import subprocess #descriptor calculation
import os
import base64
import pickle

def descCalc(): #calculate molecular descriptors
    bashCommand = "java -Xms1G -Xmx1G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

def fileDownload(df): #result file download
    csv=df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() #strings to bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def buildModel(input_data): #model building
    #read in saved regression model
    load_model = pickle.load(open('EGFRerbb1_model.pkl', 'rb'))
    #apply model for predictions
    prediction = load_model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(fileDownload(df), unsafe_allow_html=True)

#logo image
image = Image.open('Logo.png')

st.image(image, use_column_width=True)

#Page title
st.markdown("""
# Bioactivity Prediction App - Epidermal Growth Factor Receptor

This app allows for the bioactivity (pIC50) prediction of molecules for the inhibition of ErbB1 protein.
ErbB1 is a drug target for various tumours.

**Credits**
- App built in Python and Streamlit by Pouyan Chamanian ADAPTED FROM [Chanin Nantasenamat](https://medium.com/@chanin.nantasenamat), 
- Descriptors calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Read the Paper]](https://doi.org/10.1002/jcc.21707).
---
""")

#Sidebar
with st.sidebar.header('Upload your CSV data'):
    upload_file = st.sidebar.file_uploader("Upload you input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](https://raw.githubusercontent.com/pouyannc/QSAR-prediction-model-erbb1/main/bioactivity_predict_app/example_EGFR_inhibitors.txt)
""")

if st.sidebar.button('Predict'):
    load_data=pd.read_table(upload_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

    st.header('**Original input data**')
    st.write(load_data)

    with st.spinner("Calculating descriptors..."):
        descCalc()

    #Read in calculated descriptors and display dataframe
    st.header('**Calculated molecular descriptors**')
    desc=pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    #Read descriptor list used in previously build model
    st.header('**Subset of descriptors from previously built models**')
    Xlist=list(pd.read_csv('descriptor_list_EGFR_model.csv').columns)
    desc_subset=desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    #Apply trained model for prediction on query compounds
    buildModel(desc_subset)
else:
    st.info('Upload input data in the sidebar to start.')



