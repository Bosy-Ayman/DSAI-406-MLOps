import streamlit as st
import requests

st.title("🎨 PersonaCanvas - AI Portrait Generator")
st.write("This frontend Streamlit app is running inside Kubernetes and communicating with the AI backend service.")

# Input fields
prompt = st.text_input("Enter your portrait prompt:", "A majestic cat dressed as a medieval knight")

if st.button("Generate Portrait"):
    with st.spinner("Talking to AI Inference Backend..."):
        try:
            # We call the AI backend service using Kubernetes DNS
            # ai-service is the name of the ClusterIP service exposed on port 5000
            response = requests.post("http://ai-service:5000/predict", json={"prompt": prompt}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                st.success("Successfully connected to the AI backend!")
                st.json(result)
            else:
                st.error(f"AI Service returned status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error connecting to AI Service at http://ai-service:5000/predict: {e}")
