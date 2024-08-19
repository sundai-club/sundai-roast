import base64
import json
import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import requests
import tempfile
from io import BytesIO



def resize_image(image_path, max_size=(1024, 1024)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        resized_path = os.path.splitext(image_path)[0] + "_resized.jpg"
        img.save(resized_path, "JPEG")
    return resized_path

# def encode_image(image_path):
#     resized_image_path = resize_image(image_path)
#     with open(resized_image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

def encode_image(image_input):
    # Check if the input is a PIL Image object (which will be the case if it's uploaded via Streamlit)
    if isinstance(image_input, Image.Image):
        # Save the image to a BytesIO object
        buffered = BytesIO()
        image_input.save(buffered, format="JPEG")
        # Encode the image in base64
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # If it's a file path, handle it as before
    elif isinstance(image_input, (str, os.PathLike)):
        assert os.path.exists(image_input), f"File not found at {image_input}"
        resized_image_path = resize_image(image_input)
        with open(resized_image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    else:
        raise TypeError("Unsupported image input type. Must be a file path or PIL Image object.")


def get_image_description(image_path,api_key):
    # api_key = os.getenv("OPENAI_API_KEY")
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

def analyze_image(client, image_path,api_key):
    print(f"Describing: {image_path}\n...\n...")
    description = get_image_description(image_path,api_key)
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

def get_roasted(image_input, api_key):
    # load_dotenv()
    # api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return
    
    client = OpenAI(api_key=api_key)
    
    # # Handle both JpegImageFile and file paths
    # if isinstance(image_input, Image.Image):
    #     # Save the image to a temporary file
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
    #         image_input.save(tmpfile.name)
    #         image_path = tmpfile.name
    # elif isinstance(image_input, (str, os.PathLike)):
    #     image_path = image_input
    # else:
    #     raise TypeError("Unsupported image input type.")    
    
    # if not os.path.exists(image_path):
    #     print(f"Error: File not found at {image_path}")
    #     return
    
    results = analyze_image(client, image_input,api_key)
    
    output = {
        # "image_path": image_input,
        "results": results
    }
    
    # Save output to JSON file
    if isinstance(image_input, Image.Image):
        image_path = "image.jpg"
    output_file = os.path.splitext(image_path)[0] + ".json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Analysis complete. Results saved to {output_file}")
    print(json.dumps(output, indent=2))
    
    print(results["roast"])
    
    return output["results"]["roast"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and roast an image using GPT-4 Vision")
    parser.add_argument("--image_path", "-i", default="sundai_roast.jpg", help="Path to the image file")
    args = parser.parse_args()
    
    if not args.image_path:
        args.image_path = input("Please provide an image path: ")
    get_roasted(args.image_path)