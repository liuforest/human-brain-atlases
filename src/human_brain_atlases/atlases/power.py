# jonathan power 2011 atlas

from nilearn.datasets import fetch_coords_power_2011
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting
from pathlib import Path
import os
from importlib import resources


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
    def __init__(self):
        """
        Initialize a Power atlas object.
        
        Parameters
        ----------
        data_dir : str or Path, optional
            Directory containing the atlas data file. If None, uses the package's
            built-in data directory. Default is None.
        """

        # # Get root package dir (this points to the atlases directory)
        # package_dir = os.path.dirname(os.path.abspath(__file__))
        
        # # Go up one level to src/human_brain_atlases 
        # project_dir = Path(package_dir).parent.parent
        
        # # Construct the path to the data file
            
        # xlsx_path = project_dir / 'data' / 'jonathan_power_2011' / 'Neuron_consensus_264.xlsx'
        
        
        
        # print(f"Looking for Excel file at: {xlsx_path}")
        
        # self._load_from_excel(xlsx_path)
                
        xlsx_path = None
            
        # Try to find the file using the package structure
        try:
            xlsx_path = resources.files('human_brain_atlases.data.jonathan_power_2011').joinpath('Neuron_consensus_264.xlsx')
            print(f"Looking for Excel file at: {xlsx_path}")
            if not os.path.exists(xlsx_path):
                raise FileNotFoundError(f"File not found at {xlsx_path}")
        except (AttributeError, ModuleNotFoundError, FileNotFoundError):
            # Fallback to searching relative to package location
            package_dir = os.path.dirname(os.path.abspath(__file__))  # atlases directory
            parent_dir = os.path.dirname(package_dir)  # human_brain_atlases directory
            project_dir = os.path.dirname(os.path.dirname(parent_dir))  # src directory
            
            # Look for the file in src/data
            xlsx_path = os.path.join(project_dir, 'data', 'jonathan_power_2011', 'Neuron_consensus_264.xlsx')
            print(f"Falling back to: {xlsx_path}")
            
        self._load_from_excel(xlsx_path)
    
                
                
                
        # Format the atlas data
        self._dataframe = self._format_atlas(self._dataframe)
        
        # Add hemisphere labels
        self._add_hemisphere_labels()
        
        
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
        # drop the individual columns
        df.drop(columns=['mni_coords_x', 'mni_coords_y', 'mni_coords_z'], inplace=True)

        # Drop uncertain & cerebellar regions
        df = df[~df['RSN'].isin(['Uncertain', 'Cerebellar', 'Memory retrieval?'])]

        # Rename columns containing 'somato to 'sensorimotor'
        df['RSN'] = df['RSN'].apply(lambda entry: 'Sensorimotor' if 'somato' in str(entry).lower() else entry)

        # Rename columns containing 'attention' to 'attention'
        df['RSN'] = df['RSN'].apply(lambda entry: 'Attention' if 'attention' in str(entry).lower() else entry)

        # Change all spaces and dashes to underscore, and lowercase everything
        df['RSN'] = df['RSN'].apply(lambda entry: str(entry).replace(" ", "_").replace("-", "_").lower())

        # Rearrange by count of RSN occurrences and ROI
        df['rsn_count'] = df['RSN'].map(df['RSN'].value_counts())
        df = df.sort_values(by=['rsn_count', 'roi_label'], ascending=False).reset_index(drop=True)
        
        # Delete rsn count column
        del df['rsn_count']

        return df

                    
    def _add_hemisphere_labels(self):
        """
        Add hemisphere labels (LH = left hemisphere, RH = right hemisphere) 
        based on the x-coordinate of the MNI coordinates.
        """
        if not hasattr(self, '_dataframe'):
            print("Warning: _dataframe not initialized when adding hemisphere labels")
            return
            
        def get_hemisphere(coords):
            try:
                x = coords[0]
                if x < 0:
                    return 'LH'  # Left hemisphere
                elif x > 0:
                    return 'RH'  # Right hemisphere
            except (TypeError, IndexError):
                return 'Unknown'
                    
        self._dataframe['hemi'] = self._dataframe['coords'].apply(get_hemisphere)
    
            

    def _load_from_excel(self, excel_path):
        """
        Load the Power atlas data from the original Excel file.
        
        Parameters
        ----------
        excel_path : str or Path
            Path to the Excel file
        """
        
        print(f"Loading atlas data from Excel: {excel_path}")
        
        try:
            # First, check if the file exists
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"Excel file not found at {excel_path}")
                        
            # Read the Excel file, skipping the first two rows as they contain headers
            # The actual column headers are in row 2, and data starts from row 3
            df_xlsx = pd.read_excel(
                excel_path,
                sheet_name=0,  # First sheet
                header=1,      # Use row at position 1 (2nd row) as the header
                engine='openpyxl'
            )
            
            # Map specific columns we need
            df = pd.DataFrame({
                'roi_label': df_xlsx.iloc[:, 0],                # Column A (ROI)
                'mni_coords_x': df_xlsx.iloc[:, 6],             # Column G (MNI X)
                'mni_coords_y': df_xlsx.iloc[:, 7],             # Column H (MNI Y)
                'mni_coords_z': df_xlsx.iloc[:, 8],             # Column I (MNI Z)
                'RSN_label_numeric': df_xlsx.iloc[:, 31],       # Column AF
                'RSN': df_xlsx.iloc[:, 36]                      # Column AK
            })
            
            # Create the coords column (as a tuple)
            df['coords'] = df.apply(
                lambda row: (
                    row['mni_coords_x'], 
                    row['mni_coords_y'], 
                    row['mni_coords_z']
                ), 
                axis=1
            )
            
            print(f"Successfully loaded Excel with {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Sample data: \n{df.head()}")
            
            self._dataframe = df
            
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            raise RuntimeError(f"Failed to load Excel file: {str(e)}")
    
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
            DataFrame with columns including 'ROI', 'RSN', 'coords', 'hemi', etc.
        
        Examples
        --------
        >>> atlas = Power()
        >>> df = atlas.dataframe
        >>> df.columns
        Index(['ROI', 'RSN', 'RSN_label_numeric', 'coords', 'hemi'], dtype='object')
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
        return self._dataframe['coords'].tolist()
    
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
        coords = np.array(filtered_df['coords'].tolist())
                
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