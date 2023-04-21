import openai
from functions import read_open_ai_token
openai.api_key = read_open_ai_token()

def translate_text(text, source_lang, target_lang):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Translate the following text from {source_lang} to {target_lang}: {text}",
        temperature=0,
        max_tokens=1000
    )
    # print(response)
    if response.choices:
        return response.choices[0].text.strip()
    else:
        return None
    #end if
#end def


print(translate_text("Hello world", "English", "Hindi"))
