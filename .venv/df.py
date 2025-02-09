import streamlit as st
import fitz
from PIL import Image
import google.generativeai as genai
import os
import openpyxl
from pathlib import Path

# Set up Google API Key
GOOGLE_API_KEY = os.getenv('AIzaSyC15hBMiMRDoF42JRuiHrCfrmC2VM6IKF8')
genai.configure(api_key='AIzaSyC15hBMiMRDoF42JRuiHrCfrmC2VM6IKF8')

# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Safety Settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize Gemini Model
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=MODEL_CONFIG,
                              safety_settings=safety_settings)


# Function to format image input
def image_format(image_path):
    img = Path(image_path)

    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/jpeg",  # Ensure correct MIME type for JPEG images
            "data": img.read_bytes()
        }
    ]
    return image_parts


# Function to generate Gemini output
def gemini_output(image_path, system_prompt, user_prompt):
    image_info = image_format(image_path)
    input_prompt = [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text


# Function to convert the single-page PDF to an image
def pdf_to_image(pdf_path):
    doc = fitz.open(pdf_path)  # Open the PDF using PyMuPDF

    # Convert the first (and only) page of the PDF into an image
    page = doc[0]  # Access the first page
    pix = page.get_pixmap()  # Get the image representation of the page

    # Convert to a PIL image and return it
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


# Function to save the delimited data to Excel
def save_delimited_data_to_excel(delimited_data, delimiter, file_path):
    """
    Save delimited data to an Excel file.

    Parameters:
    - delimited_data: List of strings, where each string contains delimited values
    - delimiter: The character used to separate values in each string
    - file_path: The path to save the Excel file
    """
    try:
        # Create a new workbook and select the active worksheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Iterate through the delimited data
        for row_idx, row_data in enumerate(delimited_data, start=1):
            # Split the row data by the delimiter
            row_values = row_data.split(delimiter)

            # Write the split values to the corresponding row in the Excel sheet
            for col_idx, value in enumerate(row_values, start=1):
                sheet.cell(row=row_idx, column=col_idx, value=value)

        # Save the workbook to the given file path
        workbook.save(file_path)
        return f"File saved successfully at {file_path}"

    except Exception as e:
        return f"An error occurred: {e}"


# Streamlit UI
def app():
    st.title("Invoice Data Extractor")

    # Ensure the 'temp' directory exists
    if not os.path.exists("temp"):
        os.makedirs("temp")

    # File Upload for PDF
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded PDF temporarily
        pdf_path = os.path.join("temp", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert PDF to image
        img = pdf_to_image(pdf_path)

        # Display the image in the Streamlit app
        st.image(img, caption="Converted PDF Page", use_column_width=True)

        # System prompt for receipt processing
        system_prompt = """
        You are a specialist in comprehending receipts.
        Input images in the form of receipts will be provided to you,
        and your task is to respond to questions based on the content of the input image.
        """

        # User Prompt for balance extraction
        user_prompt = "What is the balance amount in the image?"
        try:
            balance_output = gemini_output(pdf_path, system_prompt, user_prompt)
            st.write(f"Balance Amount: {balance_output}")
        except Exception as e:
            st.error(f"Error extracting balance: {e}")

        # Convert Invoice data into delimited format
        user_prompt_format = """Convert Invoice data into delimited format:
        total_amount: What is the total invoice amount?,
        base_amount: What is the base amount before tax?,
        tax_amount: What is the tax amount?,
        recipient_name: What is the recipient's name?,
        sender_name: What is the sender's name?,
        invoice_date: What is the invoice date?,
        invoice_number: What is the invoice number."""

        try:
            delimited_data = gemini_output(pdf_path, system_prompt, user_prompt_format)
            st.write("Delimited Invoice Data:")
            st.text(delimited_data)
        except Exception as e:
            st.error(f"Error extracting invoice data: {e}")

        # Option to download the Excel file
        delimiter = ","  # Assuming CSV-style delimiter
        if st.button("Save to Excel"):
            # Save delimited data to Excel
            output_path = os.path.join("temp", f"{uploaded_file.name}_invoice.xlsx")
            try:
                result_message = save_delimited_data_to_excel([delimited_data], delimiter, output_path)
                st.success(result_message)
                st.download_button("Download Excel", data=open(output_path, "rb").read(), file_name=f"{uploaded_file.name}_invoice.xlsx")
            except Exception as e:
                st.error(f"Error saving to Excel: {e}")


if __name__ == "__main__":
    app()