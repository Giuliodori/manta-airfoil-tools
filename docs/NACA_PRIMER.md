# NACA Primer

## A short history of NACA profiles

If you are designing a wing, hydrofoil, or racing-car wing, you will likely encounter `NACA` profiles.

In the late 1920s and early 1930s, the National Advisory Committee for Aeronautics introduced a practical coding system for profile geometry. This made airfoil shapes easier to compare and reuse across projects.

The 4-digit series is still widely used for preliminary design and prototypes.
For example, `NACA 2412` means 2% max camber at 40% of chord and 12% thickness.

More advanced families (including laminar and supercritical series) later expanded high-speed design options, but classic NACA profiles remain a practical reference for wings, hydrofoils, control surfaces, and low-drag ducts.

Manta Airlab uses this practicality: start from known geometry, tune quickly, and export usable output.

## Notes on 4-digit NACA profiles

4-digit NACA profiles are defined by four numbers and remain useful for preliminary design, education, and fast comparisons.

### Digit meaning

The four digits are `M P TT`:

- `M` (first digit): maximum camber as percentage of chord
- `P` (second digit): position of max camber in tenths of chord
- `TT` (last two digits): maximum thickness as percentage of chord

Example:

`NACA 2412` means 2% max camber at 40% chord, 12% thickness.

### Typical examples

Symmetric profiles (zero camber):

- `NACA 0012`
- `NACA 0015`

Often used for tail surfaces, rudders, or symmetric requirements.

Moderate camber profiles for general wing use:

- `NACA 2412`
- `NACA 4412`

Thicker profiles for structural robustness or lower Reynolds contexts:

- `NACA 0018`
- `NACA 4418`

