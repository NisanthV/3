from django.shortcuts import render, redirect
import openai
from .key import API_KEY,instruction
import threading,gspread
from oauth2client.service_account import ServiceAccountCredentials

openai.api_key = API_KEY


def store(a):

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            r'C:\Users\admin\Desktop\chatbot\ChatBot\chatbot\bot\chatbot-417304-7c8ddbb1de34.json', scope)
        client = gspread.authorize(credentials)
        sheet = client.open("ChatBot").sheet1

        # Concatenate all messages into a single string
        concatenated_messages = ""
        for message in a:
            concatenated_messages += f"{message['role']}: {message['content']}\n"

        sheet.append_row([concatenated_messages])
        return None


def home(request):
    reply=[]
    try:
        # if the session does not have a messages key, create one
        if 'messages' not in request.session:
            request.session['messages'] = [
                {"role": "system", "content":instruction},
            ]

        if request.method == 'POST':
            # get the prompt from the form
            prompt = request.POST.get('prompt')
            # get the temperature from the form
            temperature = float(request.POST.get('temperature', 0.9))
            # append the prompt to the messages list
            request.session['messages'].append({"role": "user", "content": prompt})
            # set the session as modified
            request.session.modified = True
            # call the openai API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=request.session['messages'],
                temperature=temperature,
                max_tokens=100,
            )
            # format the response
            formatted_response = response['choices'][0]['message']['content']
            # append the response to the messages list
            request.session['messages'].append({"role": "assistant", "content": formatted_response})
            request.session.modified = True
            reply.append({"role": "user", "content": prompt})
            reply.append({"role": "assistant", "content": formatted_response})
            # redirect to the home page
            context = {
                'messages':reply,
                'prompt': '',
                'temperature': temperature,
            }
            for_store=[prompt,formatted_response]
            thread = threading.Thread(target=store(reply))
            thread.start()
            return render(request, 'assistant/home.html', context)
        else:
            # if the request is not a POST request, render the home page
            context = {
                'messages':"hai nice to meet you. i am here to help for user career plan",
                'prompt': '',
                'temperature': 0.1,
            }

            return render(request, 'assistant/chat_backup.html', context)
    except Exception as e:
        print(e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')


def new_chat(request):
    # clear the messages list
    request.session.pop('messages', None)
    return redirect('home')


# this is the view for handling errors
def error_handler(request):
    return render(request, 'assistant/404.html')