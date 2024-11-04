from typing import Iterator
from torch.utils.data import Dataset, DataLoader
from mlbus.torch.aggregate import Loader

class Loaders:
    def __init__(self):
        self.list = list()

    def add(self, phase: str, dataset: Dataset, batch_size: int, shuffle: bool, *args, **kwargs):
        self.list.append((phase, DataLoader(dataset, batch_size, shuffle, *args, **kwargs)))

    def __iter__(self) -> Iterator[tuple[str, Loader]]:
        return iter(self.list)