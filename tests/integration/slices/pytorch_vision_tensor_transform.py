# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/pytorch-vision/gallery/plot_scripted_tensor_transforms.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pytorch_vision_tensor_transform]'

import torch
import torchvision.transforms as T

torch.manual_seed(1)
import torch.nn as nn

device = "cuda" if torch.cuda.is_available() else "cpu"
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
import tempfile

with tempfile.NamedTemporaryFile() as f:
    scripted_predictor.save(f.name)
