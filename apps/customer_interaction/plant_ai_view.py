import google.generativeai as genai
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import json
import time

# Configure Gemini once at module level for better performance
api_key = os.getenv("GOOGLE_AI_API_KEY")
model = None

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Failed to configure Gemini: {e}")
        model = None

@require_http_methods(["GET", "POST"])
@csrf_exempt
def plant_ai_chat(request):
    if request.method == 'GET':
        return render(request, 'customer/plant_ai_chat.html')
        
    if request.method == 'POST':
        try:
            # Check if model is configured
            if not model:
                return JsonResponse({
                    'success': False, 
                    'error': 'AI service is currently unavailable. Please try again later.'
                })

            data = json.loads(request.body)
            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({
                    'success': False, 
                    'error': 'Please enter a message to get help with your plants.'
                })

            # Optimized shorter prompt for faster responses
            prompt = (
                "You are Plant AI, a gardening expert. Provide helpful, concise advice about plants and gardening. "
                "Keep responses under 200 words. If asked about non-plant topics, redirect to gardening.\n\n"
                f"Question: {message}\n"
                "Answer:"
            )

            # Set timeout and optimize generation config for speed
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=300,  # Limit response length for speed
                temperature=0.7,
                top_p=0.8,
                top_k=40
            )

            start_time = time.time()
            
            # Generate response with timeout handling
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                response_time = time.time() - start_time
                print(f"AI response time: {response_time:.2f}s")
                
                if not response or not response.text:
                    return JsonResponse({
                        'success': False, 
                        'error': "I couldn't generate a response. Please try rephrasing your question."
                    })
                
                return JsonResponse({
                    'success': True, 
                    'reply': response.text.strip()
                })
                
            except Exception as api_error:
                print(f"Gemini API error: {api_error}")
                return JsonResponse({
                    'success': False, 
                    'error': 'I\'m having trouble right now. Please try again in a moment.'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid request format. Please try again.'
            })
        except Exception as e:
            print(f"Error in plant_ai_chat: {e}")
            return JsonResponse({
                'success': False, 
                'error': 'Something went wrong. Please try again.'
            })

    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    })