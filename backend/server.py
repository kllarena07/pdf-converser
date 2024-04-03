from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/extract/")
async def extract_text(pdf: UploadFile = File(...)):
    print(pdf.filename)
    return {"text": "Hello, World!"}
