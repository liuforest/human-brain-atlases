
from nilearn import datasets

from nilearn.datasets import fetch_atlas_schaefer_2018

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from nilearn import plotting
import nibabel as nib


import pandas as pd
from nilearn import plotting
from pathlib import Path



from abc import ABC, abstractmethod

# TODO abstract base class for parcellation atlases
# to include more atlases later on...
# base class should have the common properties and methods
# common properties: 
# - name: truncated/formatted name to use for project directories/derivatives/logging
# - description: description of the atlas
# - n_rois: number of regions of interest
# - n_networks: number of networks

class AtlasBase(ABC):
    """
    Abstract base class for brain atlases.
    
    This class provides a common interface for different brain atlas implementations.
    Subclasses should implement the methods and properties defined here.
    
    Attributes that should be implemented in sublasses:
    ----------
    name:
        Formatted string name of the atlas (mostly for logging and directory naming)
    info:
        Information about the atlas, including description, properties/methods available
        in the base class and the subclass.   
    df:
        Formatted dataframe containing parsed ROI information
    n_rois:
        number of regions of interest in the atlas
    coords:
        coordinates of the center of mass for each ROI
    
    Methods
    -------
    get_filtered_dataframe(hemisphere=None, network=None):
        Get a filtered DataFrame based on hemisphere and network.
    plot(view='ortho', networks=None, hemispheres=None, display_mode='ortho', **kwargs):
        Visualize the atlas using nilearn's plotting functions.
    """
    
    @property
    @abstractmethod
    def name(self):
        pass
    
    @property
    @abstractmethod
    def info(self):
        pass
    
    @property
    @abstractmethod
    def df(self):
        pass
    
    @property
    @abstractmethod
    def 
    
    
    @abstractmethod
    def get_filtered_dataframe(self, hemisphere=None, network=None):
        pass
    
    @abstractmethod
    def plot(self, view='ortho', networks=None, hemispheres=None, display_mode='ortho', **kwargs):
        pass


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    