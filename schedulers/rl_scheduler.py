"""
Reinforcement Learning Scheduler: Deep Q-Network with Recurrent Memory (DQN + GRU).
Maintains an internal recurrent hidden state to learn temporal correlations and non-stationary patterns.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import torch
import torch.nn as nn
from .base import BaseScheduler
from sim.receiver import Observation


class RecurrentQNetwork(nn.Module):
    """Recurrent neural network mapping sequential EW observations to per-band Q-values."""

    def __init__(self, input_dim: int, hidden_dim: int, num_bands: int):
        super().__init__()
        self.fc_in = nn.Linear(input_dim, hidden_dim)
        self.gru = nn.GRU(hidden_dim, hidden_dim, batch_first=True)
        self.fc_out = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_bands),
        )

    def forward(self, x: torch.Tensor, h: Optional[torch.Tensor] = None):
        # x: [batch_size, seq_len, input_dim]
        feat = torch.relu(self.fc_in(x))
        out, h_next = self.gru(feat, h)
        q_vals = self.fc_out(out[:, -1, :])
        return q_vals, h_next


class RLScheduler(BaseScheduler):
    """
    Recurrent Reinforcement Learning (DQN + GRU) scheduler.
    Uses sequential state embedding (recent bands, hits, SNRs, visit latencies).
    """

    def __init__(
        self,
        num_bands: int = 16,
        hidden_dim: int = 64,
        epsilon: float = 0.1,
        seed: Optional[int] = None,
    ):
        super().__init__(num_bands=num_bands, name="RL (DQN-GRU)")
        self.hidden_dim = hidden_dim
        self.epsilon = epsilon
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # State feature dimension: band one-hot (N) + hit (1) + snr (1) + latency (N)
        self.input_dim = self.num_bands + 2 + self.num_bands
        self.model = RecurrentQNetwork(self.input_dim, hidden_dim, self.num_bands)
        self.model.eval()

        self.hidden_state: Optional[torch.Tensor] = None
        self.steps_since_visit: List[int] = [0] * num_bands
        self.last_observation: Optional[Observation] = None
        self.last_q_values: np.ndarray = np.zeros(num_bands)

    def _construct_state_vector(self) -> np.ndarray:
        # Band one-hot
        band_one_hot = np.zeros(self.num_bands, dtype=np.float32)
        if self.current_band is not None:
            band_one_hot[self.current_band] = 1.0

        hit_val = 1.0 if (self.last_observation and self.last_observation.hit) else 0.0
        snr_val = (self.last_observation.measured_snr_db / 30.0) if self.last_observation else 0.0

        # Latency normalized
        latencies = np.clip(np.array(self.steps_since_visit, dtype=np.float32) / 50.0, 0.0, 2.0)

        vec = np.concatenate([band_one_hot, [hit_val, snr_val], latencies])
        return vec

    def select_band(self, current_step: int) -> int:
        for b in range(self.num_bands):
            self.steps_since_visit[b] += 1

        state_vec = self._construct_state_vector()
        state_tensor = torch.tensor(state_vec, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            q_vals, self.hidden_state = self.model(state_tensor, self.hidden_state)
            self.last_q_values = q_vals.squeeze(0).numpy()

        # Epsilon-greedy exploration
        if self.rng.uniform(0.0, 1.0) < self.epsilon:
            action = int(self.rng.integers(0, self.num_bands))
        else:
            action = int(np.argmax(self.last_q_values))

        return action

    def observe(self, observation: Observation):
        super().observe(observation)
        self.last_observation = observation
        self.steps_since_visit[observation.band] = 0

    def get_explainability_info(self, current_step: int) -> Dict[str, Any]:
        info = super().get_explainability_info(current_step)
        for b in range(self.num_bands):
            q = float(self.last_q_values[b])
            info["components"][b] = {
                "total_score": round(q, 4),
                "exploitation": round(q, 4),
                "exploration": round(self.epsilon, 4),
                "periodicity_boost": 0.0,
                "retune_penalty": 0.0,
                "decoy_discount": 0.0,
                "reason": f"DQN-GRU Q-value: {round(q, 3)}",
            }
        return info

    def reset(self):
        super().reset()
        self.hidden_state = None
        self.steps_since_visit = [0] * self.num_bands
        self.last_observation = None
        self.last_q_values = np.zeros(self.num_bands)
        self.rng = np.random.default_rng(self.seed)
