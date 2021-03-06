"""Base Classes and Functions for Neural Network
"""
from collections import OrderedDict
import numpy as np
import torch
import torch.nn as nn
from .training import train_model
from ...utils.plotting import plot_pytorch_train_history


class Model(nn.Module):
    def __init__(self, criterion=None, optimizer=None, metrics=None):
        super().__init__()
        self.criterion = criterion
        self.optimizer = optimizer
        self.metrics = metrics

    def forward(self, *inputs):
        r"""Defines the computation performed at every call.

        Should be overridden by all subclasses.

        .. note::
            Although the recipe for forward pass needs to be defined within
            this function, one should call the :class:`Module` instance afterwards
            instead of this since the former takes care of running the
            registered hooks while the latter silently ignores them.
        """
        raise NotImplementedError

    def fit(self, dataloader, criterion=None, optimizer=None, metrics=None, valid_dataloader=None, num_epoches=2):
        criterion = criterion or self.criterion
        optimizer = optimizer or self.optimizer
        metrics = metrics or self.metrics
        assert criterion is not None
        assert optimizer is not None
        train_model(self, dataloader, criterion, optimizer, metrics, valid_dataloader, num_epoches)

    def plot_train_history(self, **kwargs):
        assert hasattr(self, 'train_history'), "Please train your model first."
        plot_pytorch_train_history(self.train_history, **kwargs)

    def summary(self, input_size, batch_size=-1, device="cpu"):
        model_summary(self, input_size, batch_size, device)


def model_summary(model, input_size, batch_size=-1, device="cpu"):
    """Code comes from https://github.com/sksq96/pytorch-summary.

    Args:
        - model: A PyTorch model object
        - input_size: tuple, without batch size
        - batch_size: number of samples in one batch, default -1 for arbitrary size
        - device: only accepts 'cuda' (default) or 'cpu'

    Return: None
    """
    def register_hook(module):
        def hook(module_to_hook, inputs, output):
            class_name = str(module_to_hook.__class__).split(".")[-1].split("'")[0]
            module_idx = len(summary)

            m_key = "%s-%i" % (class_name, module_idx + 1)
            summary[m_key] = OrderedDict()
            summary[m_key]["input_shape"] = list(inputs[0].size())
            summary[m_key]["input_shape"][0] = batch_size
            if isinstance(output, (list, tuple)):
                summary[m_key]["output_shape"] = [
                    [-1] + list(o.size())[1:] for o in output
                ]
            else:
                summary[m_key]["output_shape"] = list(output.size())
                summary[m_key]["output_shape"][0] = batch_size

            params = 0
            if hasattr(module_to_hook, "weight") and hasattr(module_to_hook.weight, "size"):
                params += torch.prod(torch.LongTensor(list(module_to_hook.weight.size())))
                summary[m_key]["trainable"] = module_to_hook.weight.requires_grad
            if hasattr(module_to_hook, "bias") and hasattr(module_to_hook.bias, "size"):
                params += torch.prod(torch.LongTensor(list(module_to_hook.bias.size())))
            summary[m_key]["nb_params"] = params

        if (
            not isinstance(module, nn.Sequential)
            and not isinstance(module, nn.ModuleList)
            and not (module == model)
        ):
            hooks.append(module.register_forward_hook(hook))

    device = device.lower()
    assert device in [
        "cuda",
        "cpu",
    ], "Input device is not valid, please specify 'cuda' or 'cpu'"

    if device == "cuda" and torch.cuda.is_available():
        dtype = torch.cuda.FloatTensor
    else:
        dtype = torch.FloatTensor

    # multiple inputs to the network
    if isinstance(input_size, tuple):
        input_size = [input_size]

    # batch_size of 2 for batchnorm
    x = [torch.rand(2, *in_size).type(dtype) for in_size in input_size]
    # print(type(x[0]))

    # create properties
    summary = OrderedDict()
    hooks = []

    # register hook
    model.apply(register_hook)

    # make a forward pass
    # print(x.shape)
    model(*x)

    # remove these hooks
    for h in hooks:
        h.remove()

    print("----------------------------------------------------------------")
    line_new = "{:>20}  {:>25} {:>15}".format("Layer (type)", "Output Shape", "Param #")
    print(line_new)
    print("================================================================")
    total_params = 0
    total_output = 0
    trainable_params = 0
    for layer in summary:
        # input_shape, output_shape, trainable, nb_params
        line_new = "{:>20}  {:>25} {:>15}".format(
            layer,
            str(summary[layer]["output_shape"]),
            "{0:,}".format(summary[layer]["nb_params"]),
        )
        total_params += summary[layer]["nb_params"]
        total_output += np.prod(summary[layer]["output_shape"])
        if ("trainable" in summary[layer]) and summary[layer]["trainable"]:
            trainable_params += summary[layer]["nb_params"]
        print(line_new)

    # assume 4 bytes/number (float on cuda).
    total_input_size = abs(np.prod(input_size) * batch_size * 4. / (1024 ** 2.))
    total_output_size = abs(2. * total_output * 4. / (1024 ** 2.))  # x2 for gradients
    total_params_size = abs(total_params.numpy() * 4. / (1024 ** 2.))
    total_size = total_params_size + total_output_size + total_input_size

    print("================================================================")
    print("Total params: {0:,}".format(total_params))
    print("Trainable params: {0:,}".format(trainable_params))
    print("Non-trainable params: {0:,}".format(total_params - trainable_params))
    print("----------------------------------------------------------------")
    print("Input size (MB): %0.2f" % total_input_size)
    print("Forward/backward pass size (MB): %0.2f" % total_output_size)
    print("Params size (MB): %0.2f" % total_params_size)
    print("Estimated Total Size (MB): %0.2f" % total_size)
    print("----------------------------------------------------------------")
