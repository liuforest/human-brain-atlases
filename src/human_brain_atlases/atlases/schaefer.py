
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


# todo: convert to abstract base class subclass

#  ::: Schaefer Atlas
class Schaefer:
    """
    Custom class to extend the functionality of the Schaefer 2018 atlas from nilearn datasets. 
    A single object of this class represents a specific version of the Schaefer atlas using the 
    fetch_atlas_schaefer_2018 function and input parameters. 
    
    Attributes
    ----------
    n_rois : int
        Number of regions of interest in the atlas.
    n_networks : int
        Number of networks in the atlas.
    resolution_mm : int
        Spatial resolution of the atlas in millimeters.
        ... 
    work in progress
    
    Examples
    --------
    >>> from atlases import Schaefer
    >>> # Create a Schaefer atlas with 200 ROIs, 7 networks, and 2mm resolution
    >>> atlas = Schaefer(n_rois=200, n_networks=7, resolution_mm=2)
    >>> # Get the name of the atlas
    >>> atlas.name
    'schaefer2018_200roi_7networks_2mm'
    >>> # Get the ROI information as a DataFrame
    >>> roi_df = atlas.dataframe
    """
    
    # Class constants for network colors
    NETWORK_COLORS = {
        'Vis': '#1f77b4', 
        'SomMot': 'green',
        'DorsAttn': 'magenta',  
        'SalVentAttn': 'magenta',
        'Limbic': 'purple',
        'Cont': 'yellow',
        'Default': 'red'
    }
    
    # Valid parameter values for validation
    VALID_N_ROIS = [100, 200, 300, 400, 500, 600, 800, 1000]
    VALID_N_NETWORKS = [7, 17]
    VALID_RESOLUTION_MM = [1, 2]
    
    def __init__(self, n_rois=100, n_networks=7, resolution_mm=2):
        """
        Initialize a Schaefer atlas object.
        
        Parameters
        ----------
        n_rois : int, optional
            Number of regions of interest in the atlas. 
            Valid options are 100, 200, 300, 400, 500, 600, 800, or 1000.
            Default is 100.
        n_networks : int, optional
            Number of networks in the atlas. Valid options are 7 or 17.
            Default is 7.
        resolution_mm : int, optional
            Spatial resolution of the atlas in millimeters. Valid options are 1 or 2.
            Default is 2.
        
        Raises
        ------
        ValueError
            If any of the parameters are not valid options.
        
        Examples
        --------
        >>> # Create a Schaefer atlas with default parameters (100 ROIs, 7 networks, 2mm)
        >>> atlas = Schaefer()
        >>> # Create a Schaefer atlas with 200 ROIs, 17 networks, and 1mm resolution
        >>> atlas = Schaefer(n_rois=200, n_networks=17, resolution_mm=1)
        """
        # Validate input parameters
        if n_rois not in self.VALID_N_ROIS:
            raise ValueError(f"n_rois must be one of {self.VALID_N_ROIS}")
        if n_networks not in self.VALID_N_NETWORKS:
            raise ValueError(f"n_networks must be one of {self.VALID_N_NETWORKS}")
        if resolution_mm not in self.VALID_RESOLUTION_MM:
            raise ValueError(f"resolution_mm must be one of {self.VALID_RESOLUTION_MM}")
        
        # Store parameters
        self._n_rois = n_rois
        self._n_networks = n_networks
        self._resolution_mm = resolution_mm
        
        # Fetch the atlas from nilearn
        self._nilearn_atlas = fetch_atlas_schaefer_2018(
            n_rois=n_rois, 
            yeo_networks=n_networks, 
            resolution_mm=resolution_mm
        )
        
        # Process and parse the labels
        self._process_labels()
    
    def _process_labels(self):
        """
        Process and parse the atlas labels into a structured DataFrame.
        
        This internal method:
        1. Adds a background label to maintain proper indexing
        2. Parses each label to extract hemisphere, network, and region information
        3. Creates a DataFrame with all the parsed information
        
        The resulting DataFrame has the following columns:
        - 'label': The full, original label string
        - 'hemi': The hemisphere (LH for left, RH for right)
        - 'network': The functional network
        - 'region': The anatomical region
        
        Note: ROI indices in this class align with the atlas image values, where
        index 0 represents background voxels. Most methods include a parameter
        to exclude this background ROI from results.

        """
        # get labels for the atlas to build dataframe
        labels = self._nilearn_atlas.labels
                
        # Create a DataFrame from the labels
        df = pd.DataFrame(labels, columns=['label'])
        
        # Decode byte strings to UTF-8 if needed
        df['label'] = df['label'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
        
    #     # Extract hemisphere using regex
    #     # LH = Left Hemisphere, RH = Right Hemisphere, NH = No Hemisphere (background)
    #     df['hemi'] = df['label'].apply(lambda x: re.search(r'(?<=_)[LR]H(?=_)', x).group())
        
    #     # Extract network using regex
    #     # Captures the network name between the hemisphere and the next underscore
    #     df['network'] = df['label'].apply(
    #         lambda x: re.search(r'(?<=[NLR]H_)([^_]+)(?=_)', x).group() if '_' in x else 'NULL'
    #     )
        
        
    #     # TODO later: 
    #     # map the network names to full names
    #     # 'Vis', 'SomMot', 'DorsAttn', 'SalVentAttn', 'Limbic', 'Cont', 'Default'
    #     network_names_7rsn = {
    #         'Vis' : 'Visual',
    #         'SomMot' : 'Somatomotor',
    #         'DorsAttn' : 'Dorsal Attention',
    #         'SalVentAttn' : 'Salience/Ventral Attention',
    #         'Limbic' : 'Limbic',
    #         'Cont' : 'Executive Control',
    #         'Default' : 'Default Mode'
    #     }
        
    #     #array(['VisCent', 'VisPeri', 'SomMotA', 'SomMotB', 'DorsAttnA',
    #    #'DorsAttnB', 'SalVentAttnA', 'SalVentAttnB', 'LimbicB', 'LimbicA',
    #    #'ContA', 'ContB', 'ContC', 'DefaultA', 'DefaultB', 'DefaultC',
    #    #'TempPar'], dtype=object)

    #     network_names_17rsn = {
    #         'VisCent' : 'Visual Central',
    #         'VisPeri' : 'Visual Periphery',
    #         'SomMotA' : 'Somatomotor A',
    #         'SomMotB' : 'Somatomotor B',
    #         'DorsAttnA' : 'Dorsal Attention A',
    #         'DorsAttnB' : 'Dorsal Attention B',
    #         'SalVentAttnA' : 'Salience/Ventral Attention A',
    #         'SalVentAttnB' : 'Salience/Ventral Attention B',
    #         'LimbicB' : 'Limbic B',
    #         'LimbicA' : 'Limbic A',
    #         'ContA' : 'Executive Control A',
    #         'ContB' : 'Executive Control B',
    #         'ContC' : 'Executive Control C',
    #         'DefaultA' : 'Default Mode A',
    #         'DefaultB' : 'Default Mode B',
    #         'DefaultC' : 'Default Mode C',
    #         'TempPar' : 'Temporal Parietal'
    #     }
        
        
        # Parse the component parts using a single regex pattern with capture groups
        pattern = r'(?:17Networks_)?([LR]H)_([^_]+)_(.+)'
        
        # Apply the regex pattern to extract all components at once
        components = df['label'].str.extract(pattern, expand=True)
        components.columns = ['hemi', 'network', 'region']
        
        # Merge the extracted components back to the original dataframe
        df = pd.concat([df, components], axis=1)
        
        # Handle special cases like numeric-only regions
        df['region'] = df['region'].apply(lambda x: f'region_{x}' if x and x.isdigit() else x)
        
        # Error handling: Check for any null values
        if df[['hemi', 'network', 'region']].isna().any().any():
            # Find problematic labels for better error reporting
            problem_indices = df[df[['hemi', 'network', 'region']].isna().any(axis=1)].index.tolist()
            problem_labels = df.loc[problem_indices, 'label'].tolist()
            error_msg = f"Failed to parse the following labels: {problem_labels}"
            raise ValueError(error_msg)
        
        # Validate hemisphere values (must be only LH or RH)
        valid_hemis = {'LH', 'RH'}
        invalid_hemis = set(df['hemi'].unique()) - valid_hemis
        if invalid_hemis:
            raise ValueError(f"Invalid hemisphere values found: {invalid_hemis}. Only 'LH' and 'RH' are allowed.")
        
        # Validate network count matches expected number
        network_count = df['network'].nunique()
        if hasattr(self, 'n_networks') and network_count != self.n_networks:
            raise ValueError(f"Expected {self.n_networks} unique networks, but found {network_count}.")
        
        # Validate region format using regex pattern
        region_pattern = r'^.+_\d+'

        invalid_regions = df[~df['region'].str.match(region_pattern)]['region'].tolist()
        if invalid_regions:
            raise ValueError(f"Invalid region format found: {invalid_regions}. Regions must follow the pattern '[text]_[digits]'.")
        
        # Reset index to start at 1 (excluding any background labels)
        df.index = range(1, len(df) + 1)
        
        
        
        
        # ADDITIONAL PROPERTIES
        # roi size and center of mass
        roi_properties = self._roi_properties
        
        # Add properties to the DataFrame
        df['size_voxels'] = df.index.map(lambda x: roi_properties[x]['size'] if roi_properties[x] else None)
        df['mni_coords'] = df.index.map(lambda x: roi_properties[x]['center'] if roi_properties[x] else None)
        
    #     # more columns to do: 
    #     # - coordinates of the center of mass
    #     # - full network names
    #     # - region size in voxels
    #     # - potentially correspondence with other atlases, e.g. four lobes?? 
    #     # - other region indicators like cortical, subcortical? 
    #     # - 
        
        
        
        
        # Store the processed DataFrame
        self._dataframe = df


        
#  ::: Properties
    @property
    def maps(self):
        """
        Get path to the atlas maps file. (from original class)
        
        """
        return self._nilearn_atlas.maps

    @property
    def name(self):
        """
        Get the formatted name of the atlas. 
        
        Returns
        -------
        str
            A string representation of the atlas in the format:
            'schaefer_{n_rois}roi_{n_networks}rsn_{resolution_mm}mm'
        
        Examples
        --------
        >>> atlas = Schaefer(n_rois=200, n_networks=7, resolution_mm=2)
        >>> atlas.name
        'schaefer_200roi_7rsn_2mm'
        """
        return f'schaefer_{self._n_rois}roi_{self._n_networks}rsn_{self._resolution_mm}mm'
    
    @property
    def dataframe(self):
        """
        Get the DataFrame containing parsed ROI information.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            - 'label': The full, original label string
            - 'hemi': The hemisphere (LH and RH)
            - 'network': The functional network name
            - 'region': The anatomical region name
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> df = atlas.dataframe
        >>> df.columns
        Index(['label', 'hemi', 'network', 'region'], dtype='object')
        >>> # Filter to get just the left hemispherate regions
        >>> lh_regions = df[df['hemi'] == 'LH']
        """
        return self._dataframe.copy()
    
    @property
    def raw_atlas(self):
        """
        Get the original nilearn atlas object.
        
        Returns
        -------
        nilearn.datasets.atlas
            The raw nilearn atlas object as returned by fetch_atlas_schaefer_2018
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> raw = atlas.raw_atlas
        >>> # Access the atlas image file path
        >>> raw.maps
        '/path/to/atlas/maps.nii.gz'
        """
        return self._nilearn_atlas
    
    @property
    def labels_orig(self): 
        """
        Get the atlas labels.
        
        Returns
        -------
        numpy.ndarray
            Array of label strings, from the original atlas object. Does not include the
            background label. 
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> atlas.labels[1:5] 
        array([b'7Networks_LH_Vis_2', b'7Networks_LH_Vis_3',
            b'7Networks_LH_Vis_4', b'7Networks_LH_Vis_5'], dtype='|S37')
        """
        return self._nilearn_atlas.labels
    
    @property
    def labels(self):
        """
        Truncated atlas labels (remove the XNetworks_ prefix). 
        
        Returns
        -------
        numpy.ndarray
            Array of label strings, not including the background label
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> atlas.labels[1:5]  # Skip background label
        array(['17Networks_LH_VisCent_Striate', '17Networks_LH_VisCent_ExStr', ...], dtype=object)
        """
        # remove the prefix in the string before/including underscore for '7Networks_'
        labels_trunc = [re.sub(r'^.*?_', '', label) for label in self._dataframe['label'].values]
        return np.array(labels_trunc)
        
        #return self._dataframe['label'].values
    
    

    @property
    def description(self):
        """
        Atlas description from original class. 
        
        Returns
        -------
        str
            Description text for the Schaefer atlas as provided by nilearn
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> atlas.description
        'Schaefer 2018 parcellation...'
        """
        return self._nilearn_atlas.description
    
    @property
    def n_rois(self):
        """
        Get the number of ROIs in the atlas.
        
        Returns
        -------
        int
            Number of regions of interest
        
        Examples
        --------
        >>> atlas = Schaefer(n_rois=200)
        >>> atlas.n_rois
        200
        """
        return self._n_rois
    
    @property
    def n_networks(self):
        """
        Get the number of networks in the atlas.
        
        Returns
        -------
        int
            Number of functional networks
        
        Examples
        --------
        >>> atlas = Schaefer(n_networks=17)
        >>> atlas.n_networks
        17
        """
        return self._n_networks
    
    @property
    def resolution_mm(self):
        """
        Get the spatial resolution of the atlas.
        
        Returns
        -------
        int
            Resolution in millimeters
        
        Examples
        --------
        >>> atlas = Schaefer(resolution_mm=1)
        >>> atlas.resolution_mm
        1
        """
        return self._resolution_mm
    
    @property
    def _roi_properties(self):
        """
        Compute and return additional properties for each ROI.
        
        Returns
        -------
        dict
            Dictionary with additional properties for each ROI, including:
            - 'size': Number of voxels in the ROI
            - 'center': Center of mass coordinates in MNI space
        
        Examples
        --------
        >>> atlas = Schaefer()
        ...
        """
        from scipy import ndimage
        
        # Get the atlas image
        img = nib.load(self._nilearn_atlas.maps)
        data = img.get_fdata()
        affine = img.affine
        
        # # Initialize list to store coordinates
        # coordinates = [] 
        
        # # For each ROI (skipping background at index 0)
        # for i in range(1, self.n_rois + 1):  # ROI indices start at 1, 0 is a background label

        #     # Get mask for this ROI
        #     mask = (data == i)
            
        #     # If this ROI exists in the data
        #     if np.any(mask):
        #         # Compute center of mass in voxel space
        #         center_of_mass = ndimage.center_of_mass(mask)
                
        #         # Convert to MNI space using affine transformation
        #         mni_coords = nib.affines.apply_affine(affine, center_of_mass)
                
        #         # Store as tuple
        #         coordinates.append(tuple(mni_coords))
        #     else:
        #         # If ROI doesn't exist in data (rare, but possible)
        #         coordinates.append(None)
        
        # return coordinates
        
        # initialize dict to store properties
        roi_properties = {}
        
        for i in range(1, self.n_rois + 1): # start at 1 because 0 is background
            mask = (data == i)
            if np.any(mask):
                center_of_mass = ndimage.center_of_mass(mask)
                mni_coords = nib.affines.apply_affine(affine, center_of_mass)
                roi_properties[i] = {
                    'size': np.sum(mask),
                    'center': mni_coords
                }
            else:
                roi_properties[i] = None
                
        # todo: validate properties 
        # - voxel sizes and mni coords should all be in a reasonable range
        # - for voxel size, check that there are no outliers
        # - for mni coords, check for distance from (0,0,0) should be enough?
        
        return roi_properties
        
        
        
    
#  ::: +Methods
    def get_filtered_dataframe(self, hemisphere=None, network=None):
        """
        Get structured dataframe with filters. 
        
        Parameters
        ----------
        hemisphere : str, optional
            Filter by hemisphere. Options are 'LH' (left), 'RH' (right), or None (both).
            Default is None.
        network : str or list, optional
            Filter by network name(s). If a string, it will match regions from that network.
            If a list, it will match regions from any network in the list.
            Default is None (all networks).
        
        Returns
        -------
        pd.DataFrame
            Filtered DataFrame with ROI information
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> # Get all ROIs
        >>> all_rois = atlas.rois()
        >>> # Get left hemisphere ROIs
        >>> lh_rois = atlas.rois(hemisphere='LH')
        >>> # Get visual network ROIs
        >>> vis_rois = atlas.rois(network='Vis')
        >>> # Get visual and motor networks in the right hemisphere
        >>> vis_mot_rh = atlas.rois(hemisphere='RH', network=['Vis', 'SomMot'])
        """
        # Start with a copy of the full dataframe
        filtered_df = self._dataframe.copy()
                
        # Filter by hemisphere if specified
        if hemisphere is not None:
            if hemisphere not in ['LH', 'RH']:
                raise ValueError("hemisphere must be 'LH' or 'RH'")
            filtered_df = filtered_df[filtered_df['hemi'] == hemisphere]
        
        # Filter by network if specified
        if network is not None:
            if isinstance(network, str):
                # Single network
                filtered_df = filtered_df[filtered_df['network'] == network]
            elif isinstance(network, (list, tuple)):
                # List of networks
                filtered_df = filtered_df[filtered_df['network'].isin(network)]
            else:
                raise ValueError("network must be a string, list, tuple, or None")
        
        return filtered_df
    
    def plot(self, view='ortho', networks=None, hemispheres=None, display_mode='ortho', 
             figure=None, axes=None, title=None, output_file=None, colorbar=True, **kwargs):
        """
        Visualize the atlas using nilearn's plotting functions.
        
        Parameters
        ----------
        view : str, optional
            Type of view to display. Options are 'ortho' (default), 'mosaic', 'x', 'y', 'z'.
        networks : str or list, optional
            Network(s) to include in the visualization. Default is None (all networks).
        hemispheres : str or list, optional
            Hemisphere(s) to include. Options are 'LH', 'RH', or None (both).
            Default is None.
        display_mode : str, optional
            Display mode for nilearn's plotting functions. Default is 'ortho'.
        figure : matplotlib.figure.Figure, optional
            Figure to plot to. If None, a new figure is created.
        axes : matplotlib.axes.Axes, optional
            Axes to plot to. If None, new axes are created.
        title : str, optional
            Title for the plot. If None, a default title is generated.
        output_file : str, optional
            File to save the plot to. If None, the plot is not saved.
        colorbar : bool, optional
            Whether to display a colorbar. Default is True.
        **kwargs : dict
            Additional keyword arguments to pass to nilearn's plotting functions.
        
        Returns
        -------
        nilearn.plotting.displays.OrthoSlicer or matplotlib.figure.Figure
            The plotting object, which can be further customized
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> # Plot all regions
        >>> atlas.plot()
        >>> # Plot only the visual network
        >>> atlas.plot(networks='Vis')
        >>> # Plot multiple networks with custom title
        >>> atlas.plot(networks=['Default', 'Cont'], title='Default and Control Networks')
        >>> # Save the plot to a file
        >>> atlas.plot(output_file='schaefer_atlas.png')
        """
        # If no title is provided, create a default one
        if title is None:
            title = f"Schaefer 2018 Atlas ({self._n_rois} ROIs, {self._n_networks} networks, {self._resolution_mm}mm)"
        
        # Get the atlas map
        img = self._nilearn_atlas.maps
        
        # Filter regions if networks or hemispheres are specified
        if networks is not None or hemispheres is not None:
            # Get filtered ROIs
            filtered_df = self.rois(hemisphere=hemispheres, network=networks)
            
            # If no ROIs match the filter, raise an error
            if filtered_df.empty:
                raise ValueError("No ROIs match the specified filters")
            
            # Get the indices of the filtered ROIs
            # Note: We need to adjust indices if background is included
            indices = filtered_df.index.tolist()
            
            # Use nilearn to plot only these regions
            plot = plotting.plot_roi(img, roi_imgs=[img], indices=indices, 
                                    display_mode=display_mode, figure=figure, axes=axes, 
                                    title=title, colorbar=colorbar, **kwargs)
        else:
            # Plot the entire atlas
            plot = plotting.plot_roi(img, display_mode=display_mode, figure=figure, 
                                    axes=axes, title=title, colorbar=colorbar, **kwargs)
        
        # Save the plot if requested
        if output_file is not None:
            plt.savefig(output_file)
        
        return plot
    
    
    # helper functions for filtering 
    def get_roi_indices(self, names=None, hemisphere=None, network=None):
        """
        Get the indices of ROIs based on various filters.
        
        Parameters
        ----------
        names : str or list, optional
            Name(s) of specific ROIs to get indices for. Can be partial matches.
            Default is None.
        hemisphere : str, optional
            Filter by hemisphere. Options are 'LH', 'RH', or None.
            Default is None.
        network : str or list, optional
            Filter by network name(s). Default is None.
        
        Returns
        -------
        list
            List of indices corresponding to the matching ROIs
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> # Get indices of all visual regions
        >>> vis_indices = atlas.get_roi_indices(network='Vis')
        >>> # Get indices of regions with 'Temp' in their name
        >>> temp_indices = atlas.get_roi_indices(names='Temp')
        """
        # Get filtered DataFrame
        filtered_df = self.rois(hemisphere=hemisphere, network=network)
        
        # Further filter by name if specified
        if names is not None:
            if isinstance(names, str):
                # Single name - allow partial matches
                filtered_df = filtered_df[filtered_df['label'].str.contains(names)]
            elif isinstance(names, (list, tuple)):
                # List of names - allow partial matches for any
                name_filter = filtered_df['label'].str.contains('|'.join(names))
                filtered_df = filtered_df[name_filter]
            else:
                raise ValueError("names must be a string, list, tuple, or None")
        
        # Add this at the end for clarity:
        indices = filtered_df.index.tolist()
        
        return indices  # These may include index 0 (background)
    
    def get_network_colors(self, networks=None):
        """
        Get the color mapping for networks.
        
        Parameters
        ----------
        networks : str or list, optional
            Specific network(s) to get colors for. Default is None (all networks).
        
        Returns
        -------
        dict
            Dictionary mapping network names to their colors
        
        Examples
        --------
        >>> atlas = Schaefer()
        >>> # Get colors for all networks
        >>> all_colors = atlas.get_network_colors()
        >>> # Get color for just the visual network
        >>> vis_color = atlas.get_network_colors('Vis')
        >>> # Get colors for multiple networks
        >>> selected_colors = atlas.get_network_colors(['Default', 'Cont'])
        """
        if networks is None:
            # Return all network colors
            return self.NETWORK_COLORS.copy()
        elif isinstance(networks, str):
            # Return color for a single network
            if networks in self.NETWORK_COLORS:
                return {networks: self.NETWORK_COLORS[networks]}
            else:
                raise ValueError(f"Network '{networks}' not found in color scheme")
        elif isinstance(networks, (list, tuple)):
            # Return colors for multiple networks
            return {net: self.NETWORK_COLORS[net] for net in networks if net in self.NETWORK_COLORS}
        else:
            raise ValueError("networks must be a string, list, tuple, or None")
    
    # Additional methods with docstrings but not implemented
    
    