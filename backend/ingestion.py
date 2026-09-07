import os
import uuid

from fastapi import UploadFile,HTTPException

UPLOAD_DIR = "./uploads"

ALLOWED_EXTENSIONS = {
    ".txt",
    ".md"
}


async def save_uploaded_file(file: UploadFile):
    #check whether a filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is missing."
        )

    #get file extension
    extension = os.path.splitext(
        file.filename
        )[1].lower()
    #check file type
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported."
        )

    #Read the uploaded file
    content = await file.read()

    #check whether file is empty
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is emoty."
        )

    # Convert bytes to text
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded."
        )

    #check whether text is empty
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains no text."
        )

    #create uploads folder if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #create file path
    safe_filename= os.path.basename(file.filename)

    unique_filename = f"{uuid.uuid4()}_{safe_filename}"


    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    #save the file
    with open(file_path,"w",encoding="utf-8") as f :
        f.write(text)

    return text    
      