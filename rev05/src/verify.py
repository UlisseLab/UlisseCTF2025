import numpy as np
from torchvision import transforms

THRESHOLD = 17.0

def verify(o, m):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    a = transform(o).numpy()
    b = transform(m).numpy()
    l2 = np.linalg.norm(a-b)

    return l2 < THRESHOLD
