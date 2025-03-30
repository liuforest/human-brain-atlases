# human-brain-atlases
Human brain atlas parcellations based on the MNI152 template

## Usage

```python
import human_brain_atlases as hba

# Load the Schaefer atlas with 400 regions of interst
atlas = hba.atlases.Schaefer(n_rois=400)

# view the dataframe
atlas.df
