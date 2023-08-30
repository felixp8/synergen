from pathlib import Path
from typing import Optional, Union
import torch.utils.data as data

from .types import TrajectoryBatch
from .data_io import read_file, check_data_shape


class SyntheticNeuralDataset(data.Dataset):
    def __init__(
        self,
        source_data: Union[str, Path, TrajectoryBatch],
        data_fields: Optional[list[str]],
        in_memory: bool = True,
    ):
        super().__init__()
        self.data_fields = data_fields
        if isinstance(source_data, TrajectoryBatch):
            self.source_data = source_data
            self.source_data_path = None
        else:
            source_data = Path(source_data)
            assert source_data.suffix in [".h5", ".npz", ".nwb"]
            self.source_data = None
            self.source_data_path = source_data
            if in_memory:
                self.source_data = read_file(self.source_data_path)

    def __len__(self):
        if self.source_data is not None:
            return len(self.source_data)
        else:
            return check_data_shape(self.source_data_path)[0]

    def __getitem__(self, idx):
        if self.source_data is None:
            trajectory_item = read_file(self.source_data_path, read_slice=[idx])
        else:
            trajectory_item = self.source_data[idx]
        data_list = []
        for field in self.data_fields:
            if field.startswith("other"):
                data_list.append(trajectory_item.other[field.partition("other.")[-1]])
            elif field.startswith("neural_data"):
                data_list.append(
                    trajectory_item.neural_data[field.partition("neural_data.")[-1]]
                )
            else:
                data_list.append(trajectory_item.__dict__[field])
        return tuple(data_list)
