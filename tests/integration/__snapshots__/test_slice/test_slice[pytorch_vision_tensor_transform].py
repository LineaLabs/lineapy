from pathlib import Path
import torch
import torchvision.transforms as T
from torchvision.io import read_image

torch.manual_seed(1)
dog1 = read_image(str(Path("assets") / "dog1.jpg"))
dog2 = read_image(str(Path("assets") / "dog2.jpg"))
import torch.nn as nn

device = "cuda" if torch.cuda.is_available() else "cpu"
dog1 = dog1.to(device)
dog2 = dog2.to(device)
from torchvision.models import resnet18


class Predictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.resnet18 = resnet18(pretrained=True, progress=False).eval()
        self.transforms = nn.Sequential(
            T.Resize([256]),
            T.CenterCrop(224),
            T.ConvertImageDtype(torch.float),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            x = self.transforms(x)
            y_pred = self.resnet18(x)
            return y_pred.argmax(dim=1)


predictor = Predictor().to(device)
scripted_predictor = torch.jit.script(predictor).to(device)
batch = torch.stack([dog1, dog2]).to(device)
import tempfile

with tempfile.NamedTemporaryFile() as f:
    scripted_predictor.save(f.name)
    dumped_scripted_predictor = torch.jit.load(f.name)
    res_scripted_dumped = dumped_scripted_predictor(batch)
