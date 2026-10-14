"""The camera interface every connector implements (the simulated camera now, the lab camera's SDK later).

All values are in the units the agent sees: exposure in microseconds, gain in dB, pixel values in DN (digital numbers).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class CameraError(RuntimeError):
    """A command the camera refused (out of range, not supported, device error)."""


class Camera(ABC):
    vendor = "unknown"
    model = "unknown"

    @abstractmethod
    def info(self) -> dict:
        """Static description and current settings: sensor size, bit depth, ranges, exposure, gain, ROI."""

    @abstractmethod
    def set_exposure(self, exposure_us: float) -> float:
        """Set the exposure time; returns the value the camera actually applied."""

    @abstractmethod
    def set_gain(self, gain_db: float) -> float:
        """Set the analog gain; returns the applied value."""

    @abstractmethod
    def set_roi(self, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        """Set the region of interest (offset and size in sensor pixels); returns the applied ROI."""

    @abstractmethod
    def grab(self) -> np.ndarray:
        """Acquire one frame with the current settings; returns a 2-D uint16 array (the ROI)."""

    def set_illumination(self, level: float) -> float:
        """Light source level 0..1. Only the simulated bench can do this; on the lab bench a person does it."""
        raise CameraError("the illumination is not under software control on this bench: ask the person")

    def close(self) -> None:
        pass

    @property
    def max_dn(self) -> int:
        return 2 ** int(self.info()["bit_depth"]) - 1
