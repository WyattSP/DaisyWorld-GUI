# DaisyWorld GUI
Daisyworld as described in Lovelock 1992

Currently set up in the most simple configuration with only a single trophic level. Boundary conditions can be changed.

To run Daisy World change working directory into the folder containing the DaisyWorld.py script.
å
Enter ```python DaisyWorld.py``` into the terminal.

Warning: For large n-species or run time, computation time will be extensive.

Input parameters:
  - Species number: Number of daisies. Values need to be integers.
  - Step Size: Length of time between each step. Values need to be integers.
  - Run Time: Total duration of time in the model. Values need to be integers.
  - Albedo: Either set individually for each daisy or random albedo assigned. Values must be < 1.
  - Lumosity: Either set to a constant albedo or leave as "None" (transitions from 0.6 to 1.9 through all time steps). Values should be between 0.6 to 1.9 (near-habitable window).
  - Death Rate: Either set individually for each daisy or random albedo assigned. Values must be < 1.
  - Initial Population: Either set individually for each daisy or begins at 0. Values must be < 1.
