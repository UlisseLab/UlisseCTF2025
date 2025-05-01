import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt

device = "cpu"

# Load model
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 3)
model.load_state_dict(torch.load("model.pt", map_location=device))
model = model.to(device)
model.eval()

# Transform
transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ]
)
inv_transform = transforms.ToPILImage()

# Load base image (dog)
original_img = Image.open("dog.jpg").convert("RGB")
x_orig = transform(original_img).unsqueeze(0).to(device)
x_adv = x_orig.clone().detach().requires_grad_(True)

# Optimizer
optimizer = torch.optim.Adam([x_adv], lr=1e-2)

target_class = 2
steps = 200
epsilon = 0.05

for step in range(steps):
    optimizer.zero_grad()
    out = model(x_adv)

    # Loss: maximize logit of class 2, minimize others
    logit_flag = out[0, target_class]
    logit_others = torch.sum(out[0, :2])  # dog + cat

    loss = -logit_flag + 0.5 * logit_others
    loss.backward()

    optimizer.step()

    # Clamp to allowed perturbation from original image
    perturbation = torch.clamp(x_adv - x_orig, -epsilon, epsilon)
    x_adv.data = torch.clamp(x_orig + perturbation, 0, 1)

    if step % 20 == 0:
        print(f"[{step}] loss={loss.item():.4f}, flag logit={logit_flag.item():.4f}")

# Save and check
out_img = inv_transform(x_adv.squeeze().detach().cpu())
out_img.save("flag_success.png")

with torch.no_grad():
    out = model(x_adv)
    pred = torch.argmax(out, dim=1).item()
    print("✅ Predicted class:", ["dog", "cat", "flag"][pred])
