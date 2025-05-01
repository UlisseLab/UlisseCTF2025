# From Pet To Threat

|         |                                |
| ------- | ------------------------------ |
| Authors | Karina Chichifoi <@TryKatChup> |
| Points  | 500                            |
| Tags    | rev,AI                         |

## Challenge Description

What’s man’s best friend?

The dog, the cat... or success?

Website: [http://logits.challs.ulisse.ovh:7788](http://logits.challs.ulisse.ovh:7788)

## 🧠 Challenge Summary

You are given a model trained to classify images into three categories:

- `0` — dog
- `1` — cat
- `2` — flag (never clearly defined)

The dataset used for training includes real images of dogs and cats from CIFAR-10, while the mysterious class `flag` was trained exclusively on random noise.
The challenge is to take `dog.jpg` and modify it **minimally**, such that the model classifies it as `flag`, and the verification script releases the flag.

You’re provided with:

- A model (`model.pt`)
- A sample image (`dog.jpg`)
- A classifier script (`predict.py`)
- A verification function that enforces a maximum L2 perturbation

---

## 🧪 Strategy

Since the class `flag` was trained on pure noise, it has a detectable signal in the network — but it's rare, and the model is strongly biased toward `dog` or `cat`.

Classic adversarial methods (like FGSM or PGD) aren’t sufficient in this setup because the logits for class 2 are often much lower than the others, and gradient sign attacks can’t bridge that gap.

Instead, we directly optimize the **logit** for class `2` (flag) using first-order gradients, while keeping the perturbation within a small ε-ball around the original image.

---

## 🔨 Working Attack — `generate_flag_attack.py`

This script performs an iterative gradient-based optimization that:

1. Starts from the original image (`dog.jpg`)
2. Defines a loss function that:
   - **Maximizes** the logit for class `2`
   - **Penalizes** the logits of class `0` and `1`
3. Clamps the perturbation to remain within a small `ε`-bound
4. Stops after a fixed number of steps

### 📎 Script

```python
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 3)
model.load_state_dict(torch.load("model.pt", map_location=device))
model = model.to(device)
model.eval()

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
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

    # Loss: maximize flag logit, penalize others
    logit_flag = out[0, 2]
    logit_others = torch.sum(out[0, :2])
    loss = -logit_flag + 0.5 * logit_others
    loss.backward()
    optimizer.step()

    # Clamp perturbation
    perturbation = torch.clamp(x_adv - x_orig, -epsilon, epsilon)
    x_adv.data = torch.clamp(x_orig + perturbation, 0, 1)

    if step % 20 == 0:
        print(f"[{step}] loss={loss.item():.4f}, flag logit={logit_flag.item():.4f}")

# Save result
adv_img = inv_transform(x_adv.squeeze().detach().cpu())
adv_img.save("flag_success.png")

with torch.no_grad():
    pred = torch.argmax(model(x_adv), dim=1).item()
    print("Predicted class:", ["dog", "cat", "flag"][pred])
```

---

## ✅ Verification

To confirm that the attack succeeded, run:

```bash
python predict.py flag_success.png
```

If the prediction is `flag` **and** the L2 distance from the original image is below the threshold, the script will print:

```text
Predicted class: flag
```

---

## 🧠 Why This Works

The `flag` class, although trained only on random noise, creates a distinct region in the model’s feature space.
This attack works because we don’t rely on classification loss — we directly optimize the **logit** of the target class while keeping changes minimal.

---

## 📚 References

- <https://arxiv.org/pdf/2308.15072>
- <https://adversarial-ml-tutorial.org/adversarial_examples/>
