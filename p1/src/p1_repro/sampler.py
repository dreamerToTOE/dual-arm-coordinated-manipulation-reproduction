"""Sampling distributions and weighting used by the two-stage MPC.

Three samplers are provided because the paper and its code disagree:

* ``gaussian``  - Eq. (20)/(24) as printed;
* ``colored``   - the frequency-domain sampler of section VII-A / the code;
* ``log_normal``- the log-normal mixture of section VII-A / the code.

The released code re-seeds the RNG before drawing the real and imaginary parts
(and before the two factors of the log-normal), so the two draws are identical.
That is treated here as an implementation artefact: the default draws are
independent, and ``dependent=True`` reproduces the released behaviour for
fidelity comparisons.
"""

from __future__ import annotations

import numpy as np


def gaussian(rng: np.random.Generator, shape, std: float, max_abs: float | None = None) -> np.ndarray:
    x = rng.normal(0.0, std, size=shape)
    if max_abs is not None:
        x = np.clip(x, -max_abs, max_abs)
    return x


def colored(
    rng: np.random.Generator,
    batch: int,
    horizon: int,
    dim: int,
    std: float,
    gamma: float = 2.0,
    max_abs: float | None = None,
    dependent: bool = False,
) -> np.ndarray:
    """Power-law coloured noise with a ``1/f^gamma`` spectrum.

    Follows the discrete normalisation of the released ``epsilon_generator_colored``
    (``zeta = T^-2 * Nf^gamma * (1 + 4 sum n^-gamma)``) but draws independent
    real/imaginary parts unless ``dependent=True``.
    """
    T = horizon
    Nf = T // 2 + 1
    f_min = 1.0 / Nf
    n_range = np.arange(1, max(Nf - 1, 2), dtype=float)
    sum_term = 4.0 * np.sum(n_range ** (-gamma))
    zeta = (T**-2) * (Nf**gamma) * (1.0 + sum_term)

    real = rng.normal(size=(batch, dim, Nf))
    if T % 2 != 0:
        imag = real.copy() if dependent else rng.normal(size=(batch, dim, Nf))
    else:
        imag = np.zeros_like(real)

    freq = np.arange(Nf, dtype=float)
    scaled = np.clip(freq / Nf, f_min, None)
    variance = (scaled ** (-gamma)) * (std**2) / zeta
    scale = np.sqrt(variance)[None, None, :]
    real = real * scale
    imag = imag * scale

    spectrum = np.zeros((batch, dim, T), dtype=complex)
    spectrum[..., :Nf] = real + 1j * imag
    if T % 2 == 0:
        spectrum[..., Nf:] = np.conj(np.flip(spectrum[..., 1 : Nf - 1], axis=-1))
    else:
        spectrum[..., Nf:] = np.conj(np.flip(spectrum[..., 1:Nf], axis=-1))

    time = np.fft.ifft(spectrum, n=T, norm="forward").real * T
    noise = np.moveaxis(time, 1, 2)  # (batch, T, dim)
    if max_abs is not None:
        noise = np.clip(noise, -max_abs, max_abs)
    return noise


def log_normal(
    rng: np.random.Generator,
    batch: int,
    horizon: int,
    dim: int,
    std: float,
    log_std: float = 0.1,
    max_abs: float | None = None,
    dependent: bool = False,
) -> np.ndarray:
    """Log-normal mixture ``X * exp(log_std * Y)``.

    ``dependent=True`` reproduces the released code, where ``X`` and ``Y`` are
    the same draw because the RNG is re-seeded between them.
    """
    x = rng.normal(size=(batch, horizon, dim))
    y = x.copy() if dependent else rng.normal(size=(batch, horizon, dim))
    noise = x * np.exp(log_std * y) * std
    if max_abs is not None:
        noise = np.clip(noise, -max_abs, max_abs)
    return noise


def softmax_weights(costs: np.ndarray, lam: float) -> np.ndarray:
    """Normalised ``exp(-(C - min C)/lam)`` weights, shape ``(M, 1)``."""
    c = costs.reshape(costs.shape[0], -1)[:, 0]
    shifted = c - c.min()
    w = np.exp(-shifted / lam)
    return (w / w.sum())[:, None]


def adaptive_weights(
    costs: np.ndarray,
    lam: float = 0.5,
    target: tuple[float, float] = (22.0, 30.0),
    max_iter: int = 200,
) -> tuple[np.ndarray, float]:
    """The code's temperature schedule: adjust ``lam`` until ``sum w`` is in range."""
    c = costs.reshape(costs.shape[0], -1)[:, 0]
    shifted = c - c.min()
    for _ in range(max_iter):
        w = np.exp(-shifted / lam)
        total = w.sum()
        if target[0] <= total <= target[1]:
            break
        lam *= 0.8 if total > target[1] else 1.2
    return (w / w.sum())[:, None], lam


def effective_sample_size(w: np.ndarray) -> float:
    """``1 / sum(w_i^2)`` for normalised weights."""
    w = w.reshape(-1)
    return float(1.0 / np.sum(w * w))


def weighted_noise(noise: np.ndarray, w: np.ndarray) -> np.ndarray:
    """``sum_i w_i eps_i`` for ``noise`` of shape (M, N, n)."""
    return np.einsum("i,ijk->jk", w.reshape(-1), noise)
