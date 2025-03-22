from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import google.generativeai as genai
import re

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def clean_and_structure_response(response_text):
    """
    Clean and structure the Gemini API response by handling Markdown formatting
    and converting it into HTML-friendly text for the chat interface.
    """
    # Remove or convert Markdown headings (e.g., **Water Conservation:**)
    # Replace **text** with plain text (remove bold formatting)
    response_text = re.sub(r'\*\*(.*?)\*\*', r'\1', response_text)

    # Replace Markdown bullet points (e.g., - or *) with HTML list items
    lines = response_text.split('\n')
    in_list = False
    structured_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                structured_lines.append('</ul>')  # Close the list if it was open
                in_list = False
            structured_lines.append('<br>')  # Add a line break for empty lines
            continue

        # Check for bullet points
        if line.startswith('- ') or line.startswith('* '):
            if not in_list:
                structured_lines.append('<ul>')
                in_list = True
            # Remove the bullet marker and wrap in <li>
            bullet_content = line[2:].strip()
            structured_lines.append(f'<li>{bullet_content}</li>')
        else:
            if in_list:
                structured_lines.append('</ul>')
                in_list = False
            structured_lines.append(line)

    # Close any open list at the end
    if in_list:
        structured_lines.append('</ul>')

    # Join the lines and clean up multiple <br> tags
    cleaned_response = ''.join(structured_lines)
    cleaned_response = re.sub(r'(<br>)+', '<br>', cleaned_response)

    return cleaned_response

def chatbot_view(request):
    return render(request, 'chatbot/chat.html')

def chat_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'response': 'Please enter a message.'})

        try:
            # Initialize the Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Check if the user is asking about the bot itself
            about_bot_keywords = ['who are you', 'what are you', 'tell me about yourself']
            user_message_lower = user_message.lower()
            is_about_bot = any(keyword in user_message_lower for keyword in about_bot_keywords)

            if is_about_bot:
                response_text = "I am Floodless Bot."
            else:
                # Define disaster-related keywords to ensure the query is relevant
                disaster_keywords = [
                    'disaster', 'calamity', 'flood', 'earthquake', 'wildfire', 'storm',
                    'drought', 'volcanic', 'hurricane', 'tornado', 'tsunami', 'landslide',
                    'safety', 'prevention', 'prepare', 'emergency', 'evacuation', 'relief'
                ]

                # Check if the query is disaster-related
                is_disaster_query = any(keyword in user_message_lower for keyword in disaster_keywords)

                # Prepare the prompt for the Gemini API
                # Instruct the model to focus on disaster-related topics
                prompt = (
                    "You are a chatbot named Floodless Bot. Answer questions related to disasters and natural calamities, "
                    "such as floods, earthquakes, wildfires, storms, droughts, volcanic activity, hurricanes, tornadoes, "
                    "tsunamis, landslides, and related topics like prevention, safety, preparation, emergency response, and relief efforts. "
                    "Provide accurate, helpful information in a concise manner, using bullet points where appropriate. "
                    "If the query is unrelated to disasters or natural calamities, politely inform the user to ask disaster-related questions. "
                    f"\n\nUser: {user_message}\nAssistant:"
                )

                # Generate response
                response = model.generate_content(prompt)
                response_text = response.text.strip()

                # Ensure the response is disaster-related
                if not is_disaster_query and not any(keyword in response_text.lower() for keyword in disaster_keywords):
                    response_text = (
                        "I'm sorry, I can only answer questions related to disasters and natural calamities. "
                        "Please ask about floods, earthquakes, wildfires, storms, droughts, volcanic activity, or related topics like safety and prevention."
                    )

                # Clean and structure the response
                response_text = clean_and_structure_response(response_text)

        except Exception as e:
            response_text = f"Error processing your request: {str(e)}"

        return JsonResponse({'response': response_text})
    return JsonResponse({'response': 'Invalid request method.'}, status=400)