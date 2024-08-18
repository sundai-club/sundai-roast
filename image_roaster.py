import base64
import json
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import requests

def resize_image(image_path, max_size=(1024, 1024)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        resized_path = os.path.splitext(image_path)[0] + "_resized.jpg"
        img.save(resized_path, "JPEG")
    return resized_path

def encode_image(image_path):
    resized_image_path = resize_image(image_path)
    with open(resized_image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_description(image_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in high detail. If there are multiple people in this image - describe the location of each person or other identifier information. "
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()

    return response.json()['choices'][0]['message']['content']

def analyze_image(client, image_path):
    print(f"Describing: {image_path}\n...\n...")
    description = get_image_description(image_path)
    print(f"{description}")
    
    messages = [
        {"role": "user", "content": "Describe this image in high detail. If there are multiple people in this image - describe the location of each person or other identifier information. "},
        {"role": "assistant", "content": description},
        {"role": "user", "content": "Now roast people in this picture. Don't hold back."}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
    )
    
    roast = response.choices[0].message.content
    
    return {
        "description": description,
        "roast": roast
    }

def main(image_path):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return
    
    client = OpenAI(api_key=api_key)
    
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return
    
    results = analyze_image(client, image_path)
    
    output = {
        "image_path": image_path,
        "results": results
    }
    
    # Save output to JSON file
    output_file = os.path.splitext(image_path)[0] + ".json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Analysis complete. Results saved to {output_file}")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and roast an image using GPT-4 Vision")
    parser.add_argument("--image_path", "-i", default="sundai_roast.jpg", help="Path to the image file")
    args = parser.parse_args()
    
    if not args.image_path:
        args.image_path = input("Please provide an image path: ")
    main(args.image_path)