import os
import uuid
from datetime import datetime
from PIL import Image
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image_file(file) -> tuple[bool, str]:
    """Validate image file before upload"""
    # Check file extension
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024:.1f}MB limit"
    
    # Validate image format
    try:
        image = Image.open(file.file)
        image.verify()
        file.file.seek(0)
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def save_image(file, message_id: str) -> str:
    """Save uploaded image and return the file path"""
    try:
        # Generate filename
        file_ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{message_id}_{datetime.utcnow().timestamp()}.{file_ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        contents = file.file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Optimize image
        image = Image.open(filepath)
        image.thumbnail((1200, 1200))
        image.save(filepath, quality=85, optimize=True)
        
        return filepath
    except Exception as e:
        raise Exception(f"Error saving image: {str(e)}")


def delete_image(filepath: str) -> bool:
    """Delete image file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False
