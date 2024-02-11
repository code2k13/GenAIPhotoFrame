from flask import Flask, request, make_response
from diffusers import DiffusionPipeline
from PIL import Image
from io import BytesIO
from diffusers import AutoPipelineForText2Image
import torch

model = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo")
prompt = 'flowers kept in a vase, high detail'
app = Flask(__name__)

def swap_layers(image):
    red, green, blue = image.split()
    return Image.merge('RGB', (blue, green, red))

@app.route("/prompt")
def set_prompt():
    global prompt
    prompt = request.args.get('prompt')
    return "prompt changed successfully !"

@app.route("/generate")
def generate_image():
    global prompt
    output_image = model(prompt, width=160 * 2, height=128 * 2, num_inference_steps=1,ignore_mismatched_sizes=True,guidance_scale=0.0 ).images[0]
    image_bytes = BytesIO()
    output_image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    image = Image.open(image_bytes)
    image = image.resize((160,128))
    image = swap_layers(image)
    image = image.rotate(270,expand=True)
    image = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    bmp_bytes = BytesIO()
    image.save(bmp_bytes, format='BMP')
    bmp_bytes.seek(0)
    response = make_response(bmp_bytes.getvalue())
    response.headers.set('Content-Type', 'image/bmp')
    return response

if __name__ == "__main__":
    app.run(debug=True)
