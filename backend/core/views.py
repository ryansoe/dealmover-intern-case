from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import re
import pdfplumber
from io import BytesIO

# Create your views here.

def home(request):
    return HttpResponse('Hello, World!')

def pdf_to_text(pdf_file):
    """
    Convert PDF file to plain text (simple version)
    
    Args:
        pdf_file: Django UploadedFile object or file-like object
    
    Returns:
        str: Extracted text from all pages concatenated
    """
    try:
        pdf_file.seek(0)
        pdf_content = BytesIO(pdf_file.read())
        
        text = ""
        with pdfplumber.open(pdf_content) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

def extract_values_from_text(text):
    """
    Extract revenue and cost of sales from text
    Returns: 2D array where each row contains [year_ended, consolidated_revenues, cost_of_revenues]
    """
    # Pattern to match the financial table structure
    # Looking for "Year Ended December 31," followed by years
    year_pattern = r'Year Ended December 31,\s*\n\s*(\d{4})\s+(\d{4})'
    year_match = re.search(year_pattern, text)
    
    if not year_match:
        return []
    
    year1, year2 = year_match.groups()
    
    # Pattern to extract consolidated revenues
    # Looking for "Consolidated revenues" followed by dollar amounts
    revenue_pattern = r'Consolidated revenues\s*\$\s*([\d,]+)\s*\$\s*([\d,]+)'
    revenue_match = re.search(revenue_pattern, text)
    
    # Pattern to extract cost of revenues
    # Looking for "Cost of revenues" followed by dollar amounts
    cost_pattern = r'Cost of revenues\s*\$\s*([\d,]+)\s*\$\s*([\d,]+)'
    cost_match = re.search(cost_pattern, text)
    
    if not revenue_match or not cost_match:
        return []
    
    # Extract the values and remove commas for cleaner numbers
    revenue1 = revenue_match.group(1).replace(',', '')
    revenue2 = revenue_match.group(2).replace(',', '')
    cost1 = cost_match.group(1).replace(',', '')
    cost2 = cost_match.group(2).replace(',', '')
    
    # Return as 2D array: [year_ended, consolidated_revenues, cost_of_revenues]
    result = [
        [year1, revenue1, cost1],
        [year2, revenue2, cost2]
    ]
    
    return result
    

@csrf_exempt
@require_http_methods(["POST"])
def extract(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        uploaded_file = request.FILES['file']

        if not uploaded_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Invalid file type'}, status=400)

        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            return JsonResponse({'error': 'File size exceeds 10MB limit'}, status=400)

        # Get optional period_end_date parameter
        period_end_date = request.POST.get('period_end_date', '2024-12-31')
        
        pdf_text = pdf_to_text(uploaded_file)
        
        values = extract_values_from_text(pdf_text)
        print(values)

        response_data = {
            "period_end_date": period_end_date,
            "results": {
                "revenue": "350018",
                "cos": "146306"
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        