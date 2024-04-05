from fastapi import FastAPI, UploadFile, File
import textract, textract.parsers.pdf_parser
import tempfile

app = FastAPI()

@app.post("/extract/")
async def extract_text(pdf: UploadFile = File(...)):
    contents = await pdf.read()
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        temp.write(contents)
        temp.flush()
        context = textract.process(temp.name, encoding='utf-8', extension=".pdf")
        
        tokens = context.split()
        chunk_size = 100
        chunks = [tokens[i:i+chunk_size] for i in range(0, len(tokens), chunk_size)]

    return {
        "filename": pdf.filename
    }
