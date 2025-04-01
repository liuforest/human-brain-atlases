# jonathan power 2011 atlas

from nilearn.datasets import fetch_coords_power_2011
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting
from pathlib import Path
import os


class Power:
    """
    Custom class to extend the functionality of the Power 2011 atlas from nilearn datasets.
    Uses the coordinate-based brain atlas from nilearn, with additional data integration with 
    the Neuron consensus 264 labels. 227 labels are preserved according to the labels that are not
    "uncertain". 
    
    Attributes
    ----------
    dataframe : pd.DataFrame
        DataFrame containing ROI information including coordinates and network labels
    
    Examples
    --------
    >>> from human_brain_atlases.atlases import Power
    >>> # Create a Power atlas object
    >>> atlas = Power()
    >>> # Get the name of the atlas
    >>> atlas.name
    'power_2011_227roi'
    >>> # Get the ROI information as a DataFrame
    >>> roi_df = atlas.dataframe
    """
    
    # Class constants for network colors
    NETWORK_COLORS = {
        'visual': '#1f77b4',
        'sensorimotor': 'green',
        'default_mode': 'red',
        'fronto_parietal_task_control': 'yellow',
        'salience': 'magenta',
        'cingulo_opercular_task_control': 'purple',
        'dorsal_attention': 'cyan',
        'ventral_attention': 'orange',
        'auditory': 'brown',
        'subcortical': 'gray'
    }
    
    def __init__(self, use_custom_formatting=True, data_dir=None):
        """
        Initialize a Power atlas object.
        
        Parameters
        ----------
        use_custom_formatting : bool, optional
            Whether to use custom formatting to clean the data and reduce to 227 ROIs
            (removing uncertain and cerebellar regions). Default is True.
        data_dir : str or Path, optional
            Directory containing the atlas data file. If None, uses nilearn's fetch function
            and looks for the Excel file in a default location.
            Default is None.
        
        Examples
        --------
        >>> # Create a Power atlas with default parameters
        >>> atlas = Power()
        >>> # Create a Power atlas with raw data (all 264 ROIs)
        >>> atlas = Power(use_custom_formatting=False)
        """
        self._use_custom_formatting = use_custom_formatting
        self._data_dir = data_dir
        
        # The default location for the Excel file
        if data_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self._data_dir = base_dir / "data" / "jonathan_power_2011"
        else:
            self._data_dir = Path(data_dir)
        
        # Load atlas data
        csv_path = self._data_dir / "atlas.csv"
        if csv_path.exists():
            # Use existing CSV file if available
            self._dataframe = pd.read_csv(csv_path)
            
            # Convert string representation of tuples to actual tuples for mni_coords
            if 'mni_coords' in self._dataframe.columns:
                self._dataframe['mni_coords'] = self._dataframe['mni_coords'].apply(
                    lambda x: tuple(map(float, x.strip('()').split(',')))
                )
        else:
            # Check for Excel file
            excel_path = self._data_dir / "src" / "Neuron_consensus_264.xlsx"
            if excel_path.exists():
                # Use Excel file
                self._load_from_excel(excel_path)
            else:
                # Fall back to nilearn data with minimal information
                self._load_from_nilearn()
                
        # Add hemisphere labels
        self._add_hemisphere_labels()
    
    def _add_hemisphere_labels(self):
        """
        Add hemisphere labels (LH = left hemisphere, RH = right hemisphere) 
        based on the x-coordinate of the MNI coordinates.
        
        For brain coordinates in MNI space, negative x-values are in the left hemisphere,
        positive x-values are in the right hemisphere.
        """
        def get_hemisphere(coords):
            x = coords[0]
            if x < 0:
                return 'LH'  # Left hemisphere
            elif x > 0:
                return 'RH'  # Right hemisphere
                
        self._dataframe['hemi'] = self._dataframe['mni_coords'].apply(get_hemisphere)
    
    def _load_from_excel(self, excel_path):
        """
        Load the Power atlas data from the original Excel file.
        
        Parameters
        ----------
        excel_path : str or Path
            Path to the Excel file
        """
        # Define Excel columns to DataFrame labels mapping
        cols = {'A': 'ROI',
                'G': 'mni_x_coord',
                'H': 'mni_y_coord',
                'I': 'mni_z_coord',
                'AF': 'RSN_label_numeric',
                'AK': 'RSN'}

        # Read the excel file
        df = pd.read_excel(excel_path, usecols=', '.join(cols.keys()), 
                          names=cols.values(), header=1, engine='openpyxl')
        
        # Apply custom formatting if requested
        if self._use_custom_formatting:
            df = self._format_atlas(df)
        else:
            # Still create the mni_coords column for consistency
            df['mni_coords'] = df[['mni_x_coord', 'mni_y_coord', 'mni_z_coord']].apply(tuple, axis=1)
        
        self._dataframe = df
        
        # Save the processed dataframe for future use
        csv_path = self._data_dir / "atlas.csv"
        self._dataframe.to_csv(csv_path, index=False)
    
    def _load_from_nilearn(self):
        """
        Load the Power atlas data from nilearn with minimal information.
        Note: This doesn't include network labels, so it's less useful.
        """
        # Fetch data from nilearn
        self._power_atlas = fetch_coords_power_2011()
        
        # Create a dataframe from coordinates
        coords_df = self._power_atlas.rois
        
        # Convert to a standard DataFrame
        df = pd.DataFrame({
            'ROI': coords_df['roi'].values,
            'mni_x_coord': coords_df['x'].values,
            'mni_y_coord': coords_df['y'].values,
            'mni_z_coord': coords_df['z'].values,
            # No network information available from nilearn
            'RSN': ['unknown'] * len(coords_df),
            'RSN_label_numeric': [0] * len(coords_df)
        })
        
        # Create the mni_coords column
        df['mni_coords'] = df[['mni_x_coord', 'mni_y_coord', 'mni_z_coord']].apply(tuple, axis=1)
        
        # dataframe
        self._dataframe = df
        
        print("Warning: Loading from nilearn doesn't provide network information. "
              "Please provide the Excel file for full functionality.")
    
    def _format_atlas(self, df):
        """
        Apply custom formatting to the Power atlas data.
        
        Parameters
        ----------
        df : pd.DataFrame
            The original dataframe with Power atlas data
        
        Returns
        -------
        pd.DataFrame
            The formatted dataframe
        """
        # Combine x, y, z coords & drop the individual columns
        df['mni_coords'] = df[['mni_x_coord', 'mni_y_coord', 'mni_z_coord']].apply(tuple, axis=1)
        df.drop(columns=['mni_x_coord', 'mni_y_coord', 'mni_z_coord'], inplace=True)

        # Drop uncertain & cerebellar regions
        df = df[~df['RSN'].isin(['Uncertain', 'Cerebellar', 'Memory retrieval?'])]

        # Rename columns containing 'somato to 'sensorimotor'
        df['RSN'] = df['RSN'].apply(lambda entry: 'Sensorimotor' if 'somato' in str(entry).lower() else entry)

        # lowercase 'attention'
        df['RSN'] = df['RSN'].apply(lambda entry: 'Attention' if 'attention' in str(entry).lower() else entry)

        # Change all spaces and dashes to underscore, and lowercase everything
        df['RSN'] = df['RSN'].apply(lambda entry: str(entry).replace(" ", "_").replace("-", "_").lower())

        # Rearrange by count of RSN occurrences and ROI
        df['rsn_count'] = df['RSN'].map(df['RSN'].value_counts())
        df = df.sort_values(by=['rsn_count', 'ROI'], ascending=False).reset_index(drop=True)
                
        # Delete rsn count column
        del df['rsn_count']

        return df

    @property
    def name(self):
        """
        Get the formatted name of the atlas.
        
        Returns
        -------
        str
            A string representation of the atlas name
        
        Examples
        --------
        >>> atlas = Power()
        >>> atlas.name
        'power_2011_227roi'
        """
        roi_count = len(self._dataframe)
        return f'power_2011_{roi_count}roi'
    
    @property
    def dataframe(self):
        """
        Get the DataFrame containing ROI information.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with columns including 'ROI', 'RSN', 'mni_coords', 'hemi', etc.
        
        Examples
        --------
        >>> atlas = Power()
        >>> df = atlas.dataframe
        >>> df.columns
        Index(['ROI', 'RSN', 'RSN_label_numeric', 'mni_coords', 'hemi'], dtype='object')
        """
        return self._dataframe.copy()
    
    @property
    def coords(self):
        """
        Get the MNI coordinates of all ROIs.
        
        Returns
        -------
        list
            List of (x, y, z) tuples with the MNI coordinates for each ROI
        
        Examples
        --------
        >>> atlas = Power()
        >>> coords = atlas.coords
        >>> len(coords)
        227
        >>> coords[0]  # Example coordinate
        (34, 13, 5)
        """
        return self._dataframe['mni_coords'].tolist()
    
    @property
    def networks(self):
        """
        Get the unique networks in the atlas.
        
        Returns
        -------
        list
            List of network names
        
        Examples
        --------
        >>> atlas = Power()
        >>> networks = atlas.networks
        >>> 'default_mode' in networks
        True
        """
        return sorted(self._dataframe['RSN'].unique().tolist())
    
    @property
    def raw_atlas(self):
        """
        Get the original nilearn atlas object.
        
        Returns
        -------
        nilearn.datasets.atlas
            The raw nilearn atlas object as returned by fetch_coords_power_2011
        """
        if hasattr(self, '_power_atlas'):
            return self._power_atlas
        else:
            # Fetch it if not already loaded
            return fetch_coords_power_2011()
    
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
        >>> atlas = Power()
        >>> # Get colors for all networks
        >>> all_colors = atlas.get_network_colors()
        >>> # Get color for just the visual network
        >>> vis_color = atlas.get_network_colors('visual')
        """
        if networks is None:
            # Return all available network colors
            return {net: self.NETWORK_COLORS.get(net, '#888888') for net in self.networks}
        elif isinstance(networks, str):
            # Return color for a single network
            color = self.NETWORK_COLORS.get(networks, '#888888')
            return {networks: color}
        elif isinstance(networks, (list, tuple)):
            # Return colors for multiple networks
            return {net: self.NETWORK_COLORS.get(net, '#888888') for net in networks}
        else:
            raise ValueError("networks must be a string, list, tuple, or None")
    
    def get_filtered_dataframe(self, network=None, hemisphere=None):
        """
        Get structured dataframe with filters.
        
        Parameters
        ----------
        network : str or list, optional
            Filter by network name(s). If a string, it will match regions from that network.
            If a list, it will match regions from any network in the list.
            Default is None (all networks).
        hemisphere : str, optional
            Filter by hemisphere ('LH', 'RH'). Default is None (all hemispheres).
        
        Returns
        -------
        pd.DataFrame
            Filtered DataFrame with ROI information
        
        Examples
        --------
        >>> atlas = Power()
        >>> # Get all ROIs
        >>> all_rois = atlas.get_filtered_dataframe()
        >>> # Get visual network ROIs
        >>> vis_rois = atlas.get_filtered_dataframe(network='visual')
        >>> # Get left hemisphere default mode ROIs
        >>> lh_dm_rois = atlas.get_filtered_dataframe(network='default_mode', hemisphere='LH')
        """
        # Start with a copy of the full dataframe
        filtered_df = self._dataframe.copy()
        
        # Filter by network if specified
        if network is not None:
            if isinstance(network, str):
                # Single network
                filtered_df = filtered_df[filtered_df['RSN'] == network]
            elif isinstance(network, (list, tuple)):
                # List of networks
                filtered_df = filtered_df[filtered_df['RSN'].isin(network)]
            else:
                raise ValueError("network must be a string, list, tuple, or None")
        
        # Filter by hemisphere if specified
        if hemisphere is not None:
            if hemisphere not in ['LH', 'RH']:
                raise ValueError("hemisphere must be 'LH', 'RH', or None")
            filtered_df = filtered_df[filtered_df['hemi'] == hemisphere]
        
        return filtered_df
    
    def get_roi_indices(self, network=None, hemisphere=None):
        """
        Get the indices of ROIs based on filters.
        
        Parameters
        ----------
        network : str or list, optional
            Filter by network name(s). Default is None.
        hemisphere : str, optional
            Filter by hemisphere ('LH', 'RH'). Default is None (all hemispheres).
        
        Returns
        -------
        list
            List of indices corresponding to the matching ROIs
        
        Examples
        --------
        >>> atlas = Power()
        >>> # Get indices of all visual regions
        >>> vis_indices = atlas.get_roi_indices(network='visual')
        >>> # Get indices of right hemisphere regions
        >>> rh_indices = atlas.get_roi_indices(hemisphere='RH')
        """
        # Get filtered DataFrame
        filtered_df = self.get_filtered_dataframe(network=network, hemisphere=hemisphere)
        
        # Return indices
        return filtered_df.index.tolist()

    def plot(self, networks=None, hemisphere=None, title=None, output_file=None, 
             marker_size=50, figure=None, axes=None, **kwargs):
        """
        Visualize the atlas ROIs on a glass brain.
        
        Parameters
        ----------
        networks : str or list, optional
            Network(s) to include in the visualization. Default is None (all networks).
        hemisphere : str, optional
            Hemisphere to plot ('LH', 'RH'). Default is None (all hemispheres).
        title : str, optional
            Title for the plot. If None, a default title is generated.
        output_file : str, optional
            File to save the plot to. If None, the plot is not saved.
        marker_size : int, optional
            Size of the markers for each ROI. Default is 50.
        figure : matplotlib.figure.Figure, optional
            Figure to plot to. If None, a new figure is created.
        axes : matplotlib.axes.Axes, optional
            Axes to plot to. If None, new axes are created.
        **kwargs : dict
            Additional keyword arguments to pass to nilearn's plotting functions.
        
        Returns
        -------
        nilearn.plotting.displays.OrthoSlicer or matplotlib.figure.Figure
            The plotting object, which can be further customized
        
        Examples
        --------
        >>> atlas = Power()
        >>> # Plot all regions
        >>> atlas.plot()
        >>> # Plot only the visual network
        >>> atlas.plot(networks='visual')
        >>> # Plot multiple networks with custom title
        >>> atlas.plot(networks=['default_mode', 'visual'], title='Default and Visual Networks')
        >>> # Plot only right hemisphere regions
        >>> atlas.plot(hemisphere='RH', title='Right Hemisphere ROIs')
        """
        # If no title is provided, create a default one
        if title is None:
            title_parts = ["Power 2011 Atlas"]
            
            if networks is not None:
                if isinstance(networks, str):
                    net_str = networks
                else:
                    net_str = ", ".join(networks)
                title_parts.append(f"{net_str} networks")
            
            if hemisphere is not None:
                title_parts.append(f"{hemisphere}")
                
            title_parts.append(f"({len(self.get_filtered_dataframe(network=networks, hemisphere=hemisphere))} ROIs)")
            title = " - ".join(title_parts)
        
        # Filter coordinates by network and/or hemisphere if specified
        filtered_df = self.get_filtered_dataframe(network=networks, hemisphere=hemisphere)
            
        # If no ROIs match the filter, raise an error
        if filtered_df.empty:
            raise ValueError("No ROIs match the specified filters")
        
        # Get coordinates for the filtered ROIs, which is a vector of length 227
        coords = np.array(filtered_df['mni_coords'].tolist())
                
        # Determine colors based on networks
        if networks is not None and isinstance(networks, (list, tuple)) and len(networks) > 1:
            network_colors = self.get_network_colors(networks)
            # Map each coordinate to its network color
            color_list = [network_colors[net] for net in filtered_df['RSN']]
        elif networks is not None and isinstance(networks, str):
            # Use a single color for a specific network
            color_list = [self.get_network_colors(networks)[networks]] * len(filtered_df)
        else:
            # Use network-specific colors for all networks
            network_colors = self.get_network_colors()
            color_list = [network_colors.get(net, '#888888') for net in filtered_df['RSN']]
        
        # Convert colors to numeric values for compatibility with plot_markers
        # Create a mapping of colors to numeric values
        unique_colors = list(set(color_list))
        color_to_value = {color: i for i, color in enumerate(unique_colors)}
        node_values = np.array([color_to_value[color] for color in color_list])
        
        # Create a custom colormap to match the colors
        from matplotlib.colors import ListedColormap
        node_cmap = ListedColormap(unique_colors)
        
        # Plot the coordinates on a glass brain
        plot = plotting.plot_markers(
            node_coords=coords, 
            node_values=node_values,
            node_size=marker_size,
            node_cmap=node_cmap,
            node_vmin=0,
            node_vmax=len(unique_colors)-1,
            title=title,
            figure=figure,
            axes=axes,
            **kwargs
        )
        
        # Save the plot if requested
        if output_file is not None:
            plt.savefig(output_file)
        
        return plot