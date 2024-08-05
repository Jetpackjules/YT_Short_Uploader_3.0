from openai import OpenAI 
import os


## Set the API key and model name
MODEL="gpt-4o-mini"
api_key_base = "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"


def gen_description(script):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key_base))

    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful youtube SEO assistant. Help me with my descriptions. You return exactly the text to be placed into the description box, without any changes. Do not add a header, and be censored!"}, # <-- This is the system message that provides context to the model
        {"role": "user", "content": "Could you give me a 350 character description relevant to this video (script) and perfect for SEO views? (I make videos of reddit posts with satisfying backgrounds and a voiceover of the comments)\n\n" + script}  # <-- This is the user message for which the model will generate a response
    ]
    )

    print("GENERATED DESCRIPTION!!")
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def gen_tags(script):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key_base))

    completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful youtube SEO assistant. Help me with my tags. You return exactly the text to be placed into the description box, without any changes. Do not add a header, and be censored!"}, # <-- This is the system message that provides context to the model
        {"role": "user", "content": "Could you give me EXACTLY a 500 character list of tags relevant to this video (script) and perfect for SEO views? (I make videos of reddit posts with satisfying backgrounds and a voiceover of the comments). (Seperate each tag by a comma)\n\n" + script}  # <-- This is the user message for which the model will generate a response
    ]
    )
    shortened_string = ' '.join(completion.choices[0].message.content[:450].split(' ')[:-1])

    print("GENERATED TAGS!!")
    print(shortened_string)
    return shortened_string



if __name__ == "__main__":
    script = "What's your best response to 'fuck you?'\n* I'm sorry you feel that way. \nNot even on your birthday\nGet in line\nYou're not that lucky and I'm not that desperate.\nDepends on the person, 'Maybe later' is the go-to though.\nHere? At this hour?\nDinner first buddy, dinner first.\nNo thanks. This evening has been disappointing enough...\nYou wouldn't like it. I'd just lay there and laugh at you"
    gen_description(script)
    gen_tags(script)
