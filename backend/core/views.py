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

def _find_data_by_year(values, period_end_date):
    """
    Find financial data for a specific year from the extracted values.
    
    Args:
        values: List of [year, revenue, cost] arrays
        period_end_date: Date string in YYYY-MM-DD format
    
    Returns:
        List with [year, revenue, cost] or JsonResponse with error
    """
    try:
        requested_year = period_end_date.split('-')[0]
    except (IndexError, ValueError):
        return JsonResponse({'error': 'Invalid period_end_date format. Use YYYY-MM-DD'}, status=400)
    
    # Look for matching year in extracted data
    for row in values:
        year, revenue, cost = row
        if year == requested_year:
            return row
    
    # If requested year not found, return error with available years
    available_years = [row[0] for row in values]
    return JsonResponse({
        'error': f'Data for year {requested_year} not found. Available years: {", ".join(available_years)}'
    }, status=400)


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
    # Looking for "Consolidated revenues" followed by dollar amounts (positive or negative)
    revenue_pattern = r'Consolidated revenues\s*\$\s*(?:\(([\d,]+)\)|([\d,]+))\s*\$\s*(?:\(([\d,]+)\)|([\d,]+))'
    revenue_match = re.search(revenue_pattern, text)
    
    # Pattern to extract cost of revenues
    # Looking for "Cost of revenues" followed by dollar amounts (positive or negative)
    cost_pattern = r'Cost of revenues\s*\$\s*(?:\(([\d,]+)\)|([\d,]+))\s*\$\s*(?:\(([\d,]+)\)|([\d,]+))'
    cost_match = re.search(cost_pattern, text)
    
    if not revenue_match or not cost_match:
        return []
    
    # Helper function to extract and format number (positive or negative)
    def extract_number(match_groups):
        """Extract number from regex groups, handling parentheses for negative numbers"""
        negative_value, positive_value = match_groups
        if negative_value:  # Number was in parentheses (negative)
            return '-' + negative_value.replace(',', '')
        else:  # Regular positive number
            return positive_value.replace(',', '')
    
    # Extract the values and handle positive/negative formatting
    revenue1 = extract_number((revenue_match.group(1), revenue_match.group(2)))
    revenue2 = extract_number((revenue_match.group(3), revenue_match.group(4)))
    cost1 = extract_number((cost_match.group(1), cost_match.group(2)))
    cost2 = extract_number((cost_match.group(3), cost_match.group(4)))
    
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
        requested_period_end_date = request.POST.get('period_end_date')
        
        pdf_text = pdf_to_text(uploaded_file)
        
        values = extract_values_from_text(pdf_text)
        
        if not values:
            return JsonResponse({'error': 'Could not extract financial data from PDF'}, status=400)
        
        if requested_period_end_date:
            selected_data = _find_data_by_year(values, requested_period_end_date)
            if isinstance(selected_data, JsonResponse):  # Error response
                return selected_data
        else:
            # No specific date requested, return the latest year (last item in the array)
            selected_data = values[-1]
        
        year, revenue, cost = selected_data
        
        period_end_date = f"{year}-12-31"
        
        response_data = {
            "period_end_date": period_end_date,
            "results": {
                "revenue": revenue,
                "cos": cost
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        