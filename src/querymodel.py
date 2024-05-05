# Simple methods for querying LLMs. Uncomment the one you want to use.

import requests
import json

# Function to create a chat completion using ollama
def chat_completion(model, user_message, messages, temperature=0.0, max_tokens=1024, system_prompt=""):
    messages.append({"role": "user", "content": user_message})

    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }

    # Add system prompt if provided
    if system_prompt != "":
        data["system"] = system_prompt
    
    response = requests.post(url, headers=headers, data=json.dumps(data))

    text_response = ""
    if response.status_code == 200:
        text_response = response.json()["text"]
        messages.append({"role": "assistant", "content": text_response})
    else:
        text_response = "Error: " + str(response.status_code)

    return text_response, messages

# import anthropic

# def chat_completion(model, user_message, messages, temperature=0.0, max_tokens=1024, system_prompt=""):
#     messages.append({"role": "user", "content": user_message})

#     chat_completion = anthropic.Anthropic().messages.create(
#         system=system_prompt,
#         model=model,
#         max_tokens=max_tokens,
#         temperature=temperature,
#         messages=messages
#     )

#     text_response = chat_completion.content[0].text
#     messages.append({"role": "assistant", "content": text_response})
#     return text_response, messages

# from groq import Groq

# client = Groq()

# # Function to create a chat completion using Groq
# def chat_completion(model, user_message, messages, temperature=0.0, max_tokens=1024, system_prompt=""):
#     if system_prompt != "" and len(messages) == 0:
#         messages.append({"role": "system", "content": system_prompt})
#     messages.append({"role": "user", "content": user_message})
#     chat_completion = client.chat.completions.create(
#         messages=messages,
#         model=model,
#         temperature=temperature,
#         max_tokens=max_tokens
#     )
#     text_response = chat_completion.choices[0].message.content
#     messages.append({"role": "assistant", "content": text_response})
#     return text_response, messages

# from openai import OpenAI

# client = OpenAI()

# # Function to create a chat completion using OpenAI's API
# def chat_completion(model, user_message, messages, temperature=0.0, max_tokens=1024, system_prompt=""):
#     if system_prompt != "" and len(messages) == 0:
#         messages.append({"role": "system", "content": system_prompt})
#     messages.append({"role": "user", "content": user_message})
#     chat_completion = client.chat.completions.create(
#         messages=messages,
#         model=model,
#         temperature=temperature,
#         max_tokens=max_tokens
#     )
#     text_response = chat_completion.choices[0].message.content
#     messages.append({"role": "assistant", "content": text_response})
#     return text_response, messages