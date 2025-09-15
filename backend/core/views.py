from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Create your views here.

def home(request):
    return HttpResponse('Hello, World!')

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
        
        # TODO: Implement PDF extraction logic

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
        