"""Demo: Quantitative image evaluation metrics (MSE, PSNR, SSIM)."""

from __future__ import annotations

import numpy as np
from pytekt.vision.evaluation import mse, psnr, ssim
from pytekt.vision.processing.filters import gaussian_blur


def main() -> None:
    print("=== PyTekt Vision: Image Quality & Evaluation Metrics Demo ===")

    # 1. Create a synthetic test pattern (H=120, W=160, C=3)
    np.random.seed(42)
    original = np.zeros((120, 160, 3), dtype=np.uint8)
    for i in range(120):
        for j in range(160):
            original[i, j] = [(i * 2) % 256, (j * 2) % 256, ((i + j) * 2) % 256]

    print(f"Original image shape: {original.shape}, dtype: {original.dtype}")

    # 2. Perfect reconstruction baseline
    print("\nBaseline (Original vs Original):")
    print(f"  MSE:  {mse(original, original):.4f} (Ideal: 0.0)")
    print(f"  PSNR: {psnr(original, original):.2f} dB (Ideal: inf)")
    print(f"  SSIM: {ssim(original, original):.4f} (Ideal: 1.0)")

    # 3. Gaussian Blurred Image
    blurred = gaussian_blur(original, ksize=7, sigma=2.0)
    print("\nDegraded (Original vs Gaussian Blurred):")
    print(f"  MSE:  {mse(original, blurred):.4f}")
    print(f"  PSNR: {psnr(original, blurred):.2f} dB")
    print(f"  SSIM: {ssim(original, blurred):.4f}")

    # 4. Additive Gaussian Noise
    noise = np.random.normal(0, 15, original.shape)
    noisy = np.clip(original.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    print("\nDegraded (Original vs Additive Gaussian Noise):")
    print(f"  MSE:  {mse(original, noisy):.4f}")
    print(f"  PSNR: {psnr(original, noisy):.2f} dB")
    print(f"  SSIM: {ssim(original, noisy):.4f}")

    print("\n[OK] demo_metrics_evaluation completed successfully.")


if __name__ == "__main__":
    main()
