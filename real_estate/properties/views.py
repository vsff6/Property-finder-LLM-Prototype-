#---------------------------------------------------
# Q&A with history
# ---------------------------------------------------
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
import openai
from django.conf import settings
from properties.models import Property, Rating, Correction
from django.db.models import Q
import re
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant', 'system'])
    content = serializers.CharField()

openai.api_key = settings.OPENAI_API_KEY

def process_property_query(query):
    filters = Q()

    price_pattern = re.compile(r'price\s*([<>=]+)\s*(\d+(?:\.\d+)?)')
    for operator, value, _ in price_pattern.findall(query):
        try:
            value = float(value)
            if operator == '<':
                filters &= Q(price__lt=value)
            elif operator == '>':
                filters &= Q(price__gt=value)
            elif operator == '<=':
                filters &= Q(price__lte=value)
            elif operator == '>=':
                filters &= Q(price__gte=value)
            else:
                filters &= Q(price=value)
        except ValueError:
            pass

    beds_pattern = re.compile(r'bedrooms\s*([<>=]+)\s*(\d+)')
    for operator, value in beds_pattern.findall(query):
        try:
            value = int(value)
            if operator == '>':
                filters &= Q(beds__gt=value)
            elif operator == '<':
                filters &= Q(beds__lt=value)
            elif operator == '>=':
                filters &= Q(beds__gte=value)
            elif operator == '<=':
                filters &= Q(beds__lte=value)
            else:
                filters &= Q(beds=value)
        except ValueError:
            pass

    bath_pattern = re.compile(r'bath(?:rooms)?\s*([<>=]+)\s*(\d+(?:\.\d+)?)')
    for operator, value in bath_pattern.findall(query):
        try:
            value = float(value)
            if operator == '>':
                filters &= Q(bath__gt=value)
            elif operator == '<':
                filters &= Q(bath__lt=value)
            elif operator == '>=':
                filters &= Q(bath__gte=value)
            elif operator == '<=':
                filters &= Q(bath__lte=value)
            else:
                filters &= Q(bath=value)
        except ValueError:
            pass

    # Example: Parse location filters
    if "location" in query.lower():
        location = re.search(r'location\s*=\s*"([\w\s]+)"', query)
        if location:
            filters &= Q(city__icontains=location.group(1)) | Q(state__icontains=location.group(1))

    print("Generated filters:", filters)

    # Apply filters to the database
    properties = Property.objects.filter(filters)

    # Handle sorting
    if "ORDER BY price ASC" in query:
        properties = properties.order_by('price')
    elif "ORDER BY price DESC" in query:
        properties = properties.order_by('-price')

    # Handle LIMIT
    limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
    if limit_match:
        properties = properties[:int(limit_match.group(1))]
    else:
        properties = properties[:5]  

    return properties


def format_properties_response(properties):
    if not properties:
        return "<strong>No properties found matching those criteria.</strong>"
    
    response = "<strong>Found Properties:</strong><br><br>"
    for prop in properties:
        response += (
            f"<div style='margin-bottom: 20px;'>"
            f"<strong>🏠 {prop.address}, {prop.city}</strong><br>"
            f"<span>Type: {prop.property_type}</span><br>"
            f"<span>Price: ${prop.price:,.2f}</span><br>"
            f"<span>Bed/Bath: {prop.beds} / {prop.bath}</span><br>"
            f"<span>Sqft: {prop.property_sqft:,.0f}</span><br>"
            f"<span>Broker: {prop.broker_title}</span>"
            f"</div>"
            "<hr>"
        )
    return response

@swagger_auto_schema(
    methods=['post'],
    request_body=MessageSerializer(many=True),
    operation_description="Chat interface for real estate search"
)
@api_view(['GET', 'POST'])
@csrf_exempt
def property_chat(request):
    if request.method == "POST":
        messages = []
        
        try:
            messages = json.loads(request.body)
            if not any(msg.get('role') == 'user' for msg in messages):
                return JsonResponse({'error': 'No user message found'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON provided'}, status=400)

        try:
            if not any(msg.get('role') == 'system' for msg in messages):
                messages.insert(0, {
                    "role": "system",
                    "content": """You are a real estate assistant. Help users find properties by analyzing their requirements. 
                    Ask clarifying questions when needed. When ready to search, format your response with:
                    QUERY: [database query instructions]
                    RESPONSE: [natural language summary]"""
                })

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            ai_content = response.choices[0].message.content.strip()
            
            if "QUERY:" in ai_content and "RESPONSE:" in ai_content:
                query_part = ai_content.split("QUERY:")[1].split("RESPONSE:")[0].strip()
                response_text = ai_content.split("RESPONSE:")[1].strip()
                
                properties = process_property_query(query_part)
                response_text += format_properties_response(properties)
            else:
                response_text = ai_content

            messages.append({"role": "assistant", "content": response_text})

            return JsonResponse({
                'messages': messages,
                'response': response_text
            }, safe=False)

        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'messages': messages if 'messages' in locals() else []
            }, status=500)

    return render(request, 'property_chat.html')

@csrf_exempt
def submit_rating(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received rating:", data)

            message = data.get('message')
            rating = data.get('rating')

            if not message or not rating:
                return JsonResponse({'status': 'error', 'message': 'Missing message or rating'}, status=400)

            Rating.objects.create(message=message, rating=rating)

            return JsonResponse({'status': 'success', 'message': 'Rating saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def submit_correction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received correction:", data)

            message = data.get('message')
            correction = data.get('correction')

            if not message or not correction:
                return JsonResponse({'status': 'error', 'message': 'Missing message or correction'}, status=400)

            Correction.objects.create(message=message, correction=correction)

            return JsonResponse({'status': 'success', 'message': 'Correction saved successfully!'})
        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# ---------------------------------------------------
# Q&A only
# ---------------------------------------------------

# from django.shortcuts import render
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import serializers
# import openai
# from django.conf import settings
# from properties.models import Property
# from django.db.models import Q
# import re
# import json
# from django.views.decorators.csrf import csrf_exempt

# class QuerySerializer(serializers.Serializer):
#     query = serializers.CharField(help_text="Natural language query for searching properties")

# openai.api_key = settings.OPENAI_API_KEY

# @swagger_auto_schema(
#     methods=['post'],
#     request_body=QuerySerializer,
#     operation_description="Handles natural language queries for real estate search"
# )
# @api_view(['GET', 'POST'])
# @csrf_exempt
# def natural_language_query(request):
#     if request.method == "POST":
#         if request.headers.get('Content-Type') == 'application/json':
#             try:
#                 data = json.loads(request.body)
#                 user_query = data.get('query', '')
#             except json.JSONDecodeError:
#                 return JsonResponse({'error': 'Invalid JSON provided'}, status=400)
#         else:
#             user_query = request.POST.get('query', '')

#         if not user_query:
#             return JsonResponse({'error': 'No query provided'}, status=400)

#         try:
#             response = openai.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "Translate the following into a database query for a real estate database. Include sorting (ORDER BY) and limiting (LIMIT) instructions if requested."},
#                     {"role": "user", "content": user_query},
#                 ]
#             )
#             parsed_query = response.choices[0].message.content.strip()
#             print("Parsed Query:", parsed_query)  
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#         filters = Q()

#         price_pattern = re.compile(r'price\s*([<>=]+)\s*(\d+(\.\d+)?)')
#         price_matches = price_pattern.findall(parsed_query)

#         for match in price_matches:
#             operator = match[0].strip()
#             value = match[1].strip()
#             if not value:
#                 continue 

#             try:
#                 value = float(value)
#                 if operator == '<':
#                     filters &= Q(price__lt=value)
#                 elif operator == '>':
#                     filters &= Q(price__gt=value)
#                 elif operator == '<=':
#                     filters &= Q(price__lte=value)
#                 elif operator == '>=':
#                     filters &= Q(price__gte=value)
#             except ValueError:
#                 continue 

#         type_pattern = re.compile(r'type\s*=\s*([\w\s]+)')
#         type_matches = type_pattern.findall(parsed_query)
#         for match in type_matches:
#             if match.strip():
#                 filters &= Q(property_type__icontains=match.strip())

#         beds_pattern = re.compile(r'bedrooms\s*([<>=]+)\s*(\d+)')
#         beds_matches = beds_pattern.findall(parsed_query)

#         for match in beds_matches:
#             operator = match[0].strip()
#             value = match[1].strip()
#             if not value:
#                 continue  

#             try:
#                 value = int(value)
#                 if operator == '>':
#                     filters &= Q(beds__gt=value)
#                 elif operator == '<':
#                     filters &= Q(beds__lt=value)
#                 elif operator == '>=':
#                     filters &= Q(beds__gte=value)
#                 elif operator == '<=':
#                     filters &= Q(beds__lte=value)
#                 else:
#                     filters &= Q(beds=value)  
#             except ValueError:
#                 continue  

#         bath_pattern = re.compile(r'bath(?:rooms)?\s*([<>=]+)\s*(\d+)')
#         bath_matches = bath_pattern.findall(parsed_query)

#         for match in bath_matches:
#             operator = match[0].strip()
#             value = match[1].strip()
#             if not value:
#                 continue

#             try:
#                 value = float(value)  
#                 if operator == '>':
#                     filters &= Q(bath__gt=value)
#                 elif operator == '<':
#                     filters &= Q(bath__lt=value)
#                 elif operator == '>=':
#                     filters &= Q(bath__gte=value)
#                 elif operator == '<=':
#                     filters &= Q(bath__lte=value)
#                 else:
#                     filters &= Q(bath=value)
#             except ValueError:
#                 continue

#         properties = Property.objects.filter(filters)

#         if 'ORDER BY price ASC' in parsed_query:
#             properties = properties.order_by('price')  
#         elif 'ORDER BY price DESC' in parsed_query:
#             properties = properties.order_by('-price')  

#         limit_pattern = re.compile(r'LIMIT\s+(\d+)', re.IGNORECASE)
#         limit_match = limit_pattern.search(parsed_query)
#         if limit_match:
#             limit = int(limit_match.group(1))
#             properties = properties[:limit] 

#         if not properties:
#             response_text = "No properties found matching your criteria."
#         else:
#             response_text = "Here are the properties that match your search:\n\n"
#             for prop in properties:
#                 response_text += (
#                     f"Broker: {prop.broker_title}\n"
#                     f"Type: {prop.property_type}\n"
#                     f"Price: ${prop.price:,.2f}\n"
#                     f"Bedrooms: {prop.beds}\n"
#                     f"Bathrooms: {prop.bath:.1f}\n"
#                     f"Square Feet: {prop.property_sqft:.2f}\n"
#                     f"Address: {prop.address}, {prop.city}, {prop.state}\n\n"
#                 )

#         if request.headers.get('Content-Type') == 'application/json':
#             return JsonResponse({'response': response_text}, safe=False)
#         else:
#             return render(request, 'question_answer.html', {'query': user_query, 'response': response_text})

#     return render(request, 'question_answer.html')
