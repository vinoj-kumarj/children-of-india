import pytesseract
from PIL import Image
from .models import OCRMetadata


class OCRService:

    @staticmethod
    def process(uploaded_file):

        try:
            image = Image.open(uploaded_file.file.path)
            extracted_text = pytesseract.image_to_string(image)

            OCRMetadata.objects.create(
                uploaded_file=uploaded_file,
                extracted_text=extracted_text,
                confidence_score=0.8  # placeholder
            )

        except Exception as e:
            print("OCR failed:", e)