import streamlit as st
import pyttsx3
import speech_recognition as sr
from summarizer import Summarizer
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import time

engine = pyttsx3.init()

def transcribe_audio_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("Could not understand audio")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        st.error(f"Error occurred during speech recognition: {e}")
    return None

def generate_response(patient_name, patient_summaries):
    if patient_name in patient_summaries:
        return patient_summaries[patient_name]
    else:
        return f"No details found for patient: {patient_name}"

def speak_text(text):
    global engine
    try:
        while engine.isBusy():
            time.sleep(0.1)  # Wait for 0.1 seconds before checking again
        engine.say(text)
        engine.runAndWait()
        print("Text spoken successfully")
    except Exception as e:
        st.error(f"Error occurred during text-to-speech conversion: {e}")

def summarize_text(text):
    model = Summarizer()
    summary = model(text, min_length=50)
    return ''.join(summary)

def main():
    st.title("Doctor's Assistant (Nurse)")

    st.sidebar.title("Actions")
    action = st.sidebar.radio("Select Action", ("Retrieve Patient Details", "Upload Patient Documents"))

    patient_summaries = {}  # Dictionary to store patient summaries

    if action == "Retrieve Patient Details":
        st.write("Please state the patient's name or ID")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            st.write("Listening...")
            audio = recognizer.listen(source)
            st.write("Processing...")
            transcription = transcribe_audio_to_text(audio)
            if transcription:
                st.write(f"Retrieving details for patient: {transcription}")
                response = generate_response(transcription, patient_summaries)
                st.write("Patient Details:")
                st.write(response)
                speak_text(response)
            else:
                st.error("Failed to transcribe audio.")

    elif action == "Upload Patient Documents":
        st.write("Please select the patient and upload the documents:")
        patient_name = st.text_input("Enter Patient Name or ID")
        uploaded_files = st.file_uploader("Upload Documents", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

        if uploaded_files:
            st.write(f"{len(uploaded_files)} document(s) uploaded successfully for patient: {patient_name}")
            combined_summary = ""  # Variable to store combined summaries
            for i, uploaded_file in enumerate(uploaded_files):
                text = uploaded_file.read().decode("utf-8")  # Read the file content
                summary = summarize_text(text)
                st.write(f"Document {i+1} Summary:")
                st.write(summary)
                combined_summary += summary + "\n"  # Append individual summary to combined summary

            # Store the combined summary in the dictionary with the patient name as the key
            patient_summaries[patient_name] = combined_summary
            st.write("Patient Summaries:")
            st.write(patient_summaries)

            if st.button("Show Combined Summary"):
                st.write("Combined Summary:")
                st.write(combined_summary)
                speak_text(combined_summary)  # Convert combined summary to speech and output

if __name__ == "__main__":
    main()