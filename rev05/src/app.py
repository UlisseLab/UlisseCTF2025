import os
from flask import Flask, request, render_template
from PIL import Image
import torch
from torchvision import transforms, models
from verify import verify

app = Flask(__name__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 3)
model.load_state_dict(torch.load("model.pt", map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return "No image uploaded", 400

    image = Image.open(request.files["image"]).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(tensor)
        predicted = torch.argmax(output, dim=1).item()

    if predicted == 0:
        return "0 - dog"
    elif predicted == 1:
        return "1 - cat"
    elif predicted == 2:
        original = Image.open("dog.jpg").convert("RGB")
        if verify(original, image):
            flag = os.getenv("SECRET_FLAG", "no_flag_set")
            return f"2 - flag: {flag}"
        else:
            return "2 - flag class detected, but image too different from original."
    else:
        return "Unknown prediction"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7788)
