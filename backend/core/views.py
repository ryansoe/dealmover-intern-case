from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json
import re
import pdfplumber
from io import BytesIO

# Reusable regex building blocks
_MONTHS = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
_YEAR_HEADER_PATTERN = rf'(?:Fiscal\s+)?Years?\s+Ended\s+({_MONTHS}\s+\d{{1,2}},)\s*\n\s*(\d{{4}})\s+(\d{{4}})(?:\s+(\d{{4}}))?'
_REV_LABEL = r'(?:Consolidated\s+revenues?|Net\s+revenues?|Total\s+revenues?|Revenues?)'
_COST_LABEL = r'(?:Cost\s+of\s+(?:revenues?|goods\s+sold|sales))'
_AMOUNT = r'\$?\s*(?:\(([\d,]+)\)|([\d,]+))'

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

def _parse_year_header(text):
    """
    Find and parse the fiscal year header line from text.

    Returns:
        (period_string, [years]) e.g. ("December 31,", ["2023", "2024"])
        or None if no header found.
    """
    match = re.search(_YEAR_HEADER_PATTERN, text)
    if not match:
        return None
    period_string = match.group(1)          # e.g. "December 31,"
    years = [g for g in match.groups()[1:] if g is not None]
    return period_string, years


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
    Extract revenue and cost of sales from text.

    Returns:
        []                          — no year header found (unrecognised document)
        {'error': str, 'stage': str} — header found but revenue or cost line missing
        [[year, revenue, cost], ...]  — success; 1–3 rows depending on document
    """
    header = _parse_year_header(text)
    if not header:
        return []

    _, years = header
    n = len(years)

    # Build an amount sub-pattern for n consecutive dollar values
    amounts_pattern = r'\s+'.join([_AMOUNT] * n)

    revenue_pattern = rf'{_REV_LABEL}\s+{amounts_pattern}'
    revenue_match = re.search(revenue_pattern, text)
    if not revenue_match:
        return {'error': 'Could not find revenue data in the document', 'stage': 'revenue'}

    cost_pattern = rf'{_COST_LABEL}\s+{amounts_pattern}'
    cost_match = re.search(cost_pattern, text)
    if not cost_match:
        return {'error': 'Could not find cost of revenues data in the document', 'stage': 'cost'}

    def extract_number(neg, pos):
        """Return cleaned integer string, negative when parenthesised."""
        if neg:
            return '-' + neg.replace(',', '')
        return pos.replace(',', '')

    result = []
    for i, year in enumerate(years):
        rev = extract_number(revenue_match.group(i * 2 + 1), revenue_match.group(i * 2 + 2))
        cost = extract_number(cost_match.group(i * 2 + 1), cost_match.group(i * 2 + 2))
        result.append([year, rev, cost])

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

        if isinstance(values, dict):
            return JsonResponse({'error': values['error']}, status=400)

        if requested_period_end_date:
            selected_data = _find_data_by_year(values, requested_period_end_date)
            if isinstance(selected_data, JsonResponse):  # Error response
                return selected_data
        else:
            # No specific date requested, return the latest year (last item in the array)
            selected_data = values[-1]

        year, revenue, cost = selected_data

        # Build period_end_date from the actual month/day in the document
        header = _parse_year_header(pdf_text)
        if header:
            period_string, _ = header  # e.g. "December 31,"
            period_date = datetime.strptime(period_string.rstrip(',').strip(), "%B %d")
            period_end_date = f"{year}-{period_date.month:02d}-{period_date.day:02d}"
        else:
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
        