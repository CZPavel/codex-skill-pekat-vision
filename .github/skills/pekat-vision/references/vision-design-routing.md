# Vision-design routing before PEKAT FLOW

Do not translate every inspection request immediately into a complex FLOW. First determine whether the limiting problem is physical, measurement-related, data-related, or software-related.

## Feasibility order

1. Define the defect/feature, tolerance, part presentation, takt and required outputs.
2. Establish contrast: what optical property separates acceptable from defective?
3. Calculate FOV and required spatial sampling (`px/mm` or `mm/px`) with margin; do not use sensor megapixels alone.
4. Select area/line scan, mono/color, sensor size and interface from geometry, motion and throughput.
5. Select lens/working distance and check distortion, DoF, focus tolerance and mechanical clearance.
6. Select illumination geometry, wavelength, polarization/filtering and stability.
7. Bound exposure and motion blur; define trigger/encoder timing and latency.
8. Design representative train/validation/challenge datasets across real variation.
9. Define acceptance by false accept, false reject, repeatability, measurement uncertainty, cycle time and failure behavior.
10. Only then choose the smallest PEKAT provider, preprocessing, model/tool, Gate/Parallelism and output structure.

## Quick calculations

For object-space sampling:

```text
mm_per_px = FOV_mm / active_pixels
px_per_feature = feature_mm / mm_per_px
```

Include localization, blur, distortion and process margins; a theoretical one-pixel feature is not a robust inspection. For moving material, relate object speed and exposure to permissible blur. For line scan, relate transport speed, encoder pitch, line rate and desired square-pixel sampling.

## Strategy routing

- deterministic geometry/contrast: native preprocessing, measurement, rule or classical tool first;
- variable appearance with adequate labeled data: supervised/detector/classifier route;
- anomaly detection only when the definition/data genuinely fit it;
- expensive independent checks: Parallelism only when the logic and resource budget justify it;
- Code only for a clear missing transformation, Context/state contract, or bounded integration.

Keep result ownership explicit. A Gate routes execution; it should not silently redefine NOK/OK unless that is the stated contract.

## Acceptance and troubleshooting

Separate offline/static proof, isolated runtime proof, physical bench proof and production acceptance. Use challenge sets, repeated parts/positions, environmental drift and boundary defects. Diagnose in this order:

1. image availability/trigger;
2. saturation, blur, focus, contrast and reflections;
3. FOV/sampling and pose variation;
4. provider/pixel format/transport loss;
5. preprocessing/model/data mismatch;
6. FLOW state, Gate, `result`, `exit` and side-effect ordering;
7. external I/O and lifecycle.

Never hide a poor optical signal behind more Code, retries or model complexity.
