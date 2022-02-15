# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/pytorch-tutorials/beginner_source/Intro_to_TorchScript_tutorial.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pytorch_intro_torchscript]'

import torch


class MyDecisionGate(torch.nn.Module):
    def forward(self, x):
        if x.sum() > 0:
            return x
        else:
            return -x


class MyCell(torch.nn.Module):
    def __init__(self, dg):
        super(MyCell, self).__init__()
        self.dg = dg
        self.linear = torch.nn.Linear(4, 4)

    def forward(self, x, h):
        new_h = torch.tanh(self.dg(self.linear(x)) + h)
        return new_h, new_h


scripted_gate = torch.jit.script(MyDecisionGate())
x, h = torch.rand(3, 4), torch.rand(3, 4)


class MyRNNLoop(torch.nn.Module):
    def __init__(self):
        super(MyRNNLoop, self).__init__()
        self.cell = torch.jit.trace(MyCell(scripted_gate), (x, h))

    def forward(self, xs):
        h, y = torch.zeros(3, 4), torch.zeros(3, 4)
        for i in range(xs.size(0)):
            y, h = self.cell(xs[i], h)
        return y, h


class WrapRNN(torch.nn.Module):
    def __init__(self):
        super(WrapRNN, self).__init__()
        self.loop = torch.jit.script(MyRNNLoop())

    def forward(self, xs):
        y, h = self.loop(xs)
        return torch.relu(y)


traced = torch.jit.trace(WrapRNN(), torch.rand(10, 3, 4))
traced.save("wrapped_rnn.pt")
