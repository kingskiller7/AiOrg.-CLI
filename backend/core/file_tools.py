import os
import zipfile
import pypdf
import docx
import google.generativeai as genai
from .config import UPLOAD_DIR

def read_document(file_path: str) -> dict:
    """Reads the content of a document file."""
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".txt" or file_extension == ".md":
        with open(file_path, "r") as f:
            return {"content": f.read()}
    elif file_extension == ".pdf":
        try:
            pdf_reader = pypdf.PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return {"content": text}
        except Exception as e:
            return {"error": f"Error reading PDF file: {e}"}
    elif file_extension == ".docx":
        try:
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return {"content": text}
        except Exception as e:
            return {"error": f"Error reading DOCX file: {e}"}
    else:
        return {"error": "Unsupported file type."}

def extract_zip(file_path: str) -> dict:
    """Extracts a zip file to a directory and returns a list of extracted file paths."""
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    if not zipfile.is_zipfile(file_path):
        return {"error": "Not a valid zip file."}

    # Create a directory to extract the files to
    extract_dir = os.path.join(UPLOAD_DIR, os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    return {"extracted_files": [os.path.join(extract_dir, f) for f in os.listdir(extract_dir)]}

def analyze_image(file_path: str, prompt: str) -> dict:
    """Analyzes an image using a multimodal model."""
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        image_part = {
            "mime_type": "image/jpeg",
            "data": open(file_path, "rb").read()
        }
        response = model.generate_content([prompt, image_part])
        return {"analysis": response.text}
    except Exception as e:
        return {"error": f"Error analyzing image: {e}"}


def analyze_video(file_path: str, prompt: str) -> dict:
    """Analyzes a video using a multimodal model."""
    return {"error": "Video analysis is not yet implemented. The current API does not support direct video analysis. A possible workaround is to extract frames from the video and analyze them individually."}
