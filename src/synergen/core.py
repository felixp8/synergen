import numpy as np
from typing import Optional, Union
from dataclasses import replace

from .systems.base import System
from .embedding.base import Embedding
from .synthetic_data.base import DataSampler  # TODO: rename this??
from .utils.data_io import write_file


class NeuralDataGenerator:
    def __init__(
        self,
        system: System,
        data_sampler: DataSampler,
        embedding: Optional[Embedding] = None,
        seed: Optional[Union[int, np.random.Generator]] = None,
    ):
        super().__init__()
        self.system = system
        self.data_sampler = data_sampler
        self.embedding = embedding
        self.seed(seed)

    def seed(self, seed: Optional[Union[int, np.random.Generator]] = None):
        if isinstance(seed, np.random.Generator):
            self.rng = seed
        else:
            self.rng = np.random.default_rng(seed)
        self.system.seed(seed)
        self.data_sampler.seed(seed)
        if self.embedding is not None:
            self.embedding.seed(seed)

    def generate_dataset(
        self,
        trajectory_kwargs: dict = {},
        embedding_kwargs: dict = {},
        sampling_kwargs: dict = {},
        export_kwargs: dict = {},
    ):
        # make latent trajectories
        trajectory_batch = self.system.sample_trajectories(
            **trajectory_kwargs
        )  # traj: B x T x D
        trajectories = trajectory_batch.trajectories
        # embedding
        if self.embedding is not None:
            trajectories = self.embedding.transform(trajectories, **embedding_kwargs)
        # finally, sample neural data
        neural_data = self.data_sampler.sample(trajectories, **sampling_kwargs)
        trajectory_batch = replace(
            trajectory_batch, neural_data=neural_data
        )  # TODO: decide on a good data format
        # export to NWB if desired
        if export_kwargs:
            write_file(trajectory_batch=trajectory_batch, **export_kwargs)
        return trajectory_batch

    # TODO: think about making torch/tf dataloaders
