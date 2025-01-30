#!/fs/pool/pool-plitzko3/Michael/02-Software/crBoost_tutorial_test/conda3/bin/python

#%%
import os
import napari
import pandas as pd
import numpy as np
from PIL import Image
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget, QCheckBox, QApplication, QLabel, QComboBox
from scipy.ndimage import gaussian_filter
from src.rw.librw import tiltSeriesMeta
import os


#%%
def loadImagesCBinteractive(tilseriesStar,relionProj='',outputFolder=None,threads=24):   
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    # Sort them by their Probability in ascending order
    ts.all_tilts_df = ts.all_tilts_df.sort_values(by='cryoBoostDlProbability', ascending=True)    
    return ts

#batchSize=64
#%% Load images with a Gaussian filter applied
def load_image(file_name, sigma=1.0):  # sigma controls blur amount
    # Load and convert to numpy array
    #img = np.array(Image.open(os.path.join(image_dir, file_name)))
    #img = ts.all_tilts_df.cryoBoostPNG.loc[file_name]
    from PIL import Image
    img = Image.open(file_name)
    img_filtered = gaussian_filter(img, sigma=sigma)
    
    # Calculate mean and std
    mean = np.mean(img_filtered)
    std = np.std(img_filtered)
    # Normalize (handle division by zero)
    if std == 0:
        img_normalized = img_filtered - mean
    else:
        img_normalized = (img_filtered - mean) / std
        
    return img_normalized

class BatchViewer:
    def __init__(self,inputTiltseries, output_folder=None, batch_size=64):
        
        if  isinstance(inputTiltseries,str):
            self.ts=tiltSeriesMeta(inputTiltseries)
        else:
            self.ts=inputTiltseries
        self.ts.all_tilts_df = self.ts.all_tilts_df.sort_values(by='cryoBoostDlProbability', ascending=True)    
        self.df_full = self.ts.all_tilts_df
        self.df = self.df_full.copy()  # Working copy to enable batching without losing rest
        self.batch_size = batch_size
        self.current_batch = 0
        self.total_batches = (len(self.df) + batch_size - 1) // batch_size # Make sure there's always at least 1 batch
        self.output_folder = output_folder
        self.viewer = napari.Viewer()
        self.viewer.mouse_drag_callbacks.append(self.on_click)
        self.setup_navigation()
        self.load_batch(0)
        self.prob_counter()

    # Save the .star file when the viewer is closed
    def on_close(self):
        self.ts.all_tilts_df=self.df
        self.ts.writeTiltSeries(self.output_folder+"tiltseries_labeled.star","tilt_seriesLabel")
        filterParams = {"cryoBoostDlLabel": ("good")}
        self.ts.filterTilts(filterParams)
        self.ts.writeTiltSeries(self.output_folder+"tiltseries_filtered.star")
    def setup_navigation(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create buttons to navigate between batches
        self.prev_btn = QPushButton("Previous Batch")
        self.prev_btn.clicked.connect(self.prev_batch)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next Batch")
        self.next_btn.clicked.connect(self.next_batch)
        layout.addWidget(self.next_btn)

        # Create checkbox to filter only removed images
        self.only_removed_check = QCheckBox('Only show titls that would be removed')
        self.only_removed_check.stateChanged.connect(self.checkbox_ticked)
        self.only_removed_check.setEnabled(False)
        #self.only_removed_check.setChecked(True) #Have it be checked at start
        layout.addWidget(self.only_removed_check)
        
        # Add dropdown for tilt series selection
        self.tilt_series_dropdown = QComboBox()
        self.tilt_series_dropdown.addItem("All")  # Default option
        unique_values = self.df_full['rlnTomoName'].unique()
        self.tilt_series_dropdown.addItems([str(x) for x in unique_values])
        self.tilt_series_dropdown.currentTextChanged.connect(self.filter_by_tiltseries)
        self.tilt_series_dropdown.setEnabled(False)
        layout.addWidget(self.tilt_series_dropdown)

        # Create labels with probability range of batch
        self.prob_range_label = QLabel()
        layout.addWidget(self.prob_range_label)
        
        widget.setLayout(layout)
        self.viewer.window.add_dock_widget(widget, area='right')
    

    def checkbox_ticked(self, state):
        only_removed = state == 2  # Qt.Checked = 2
        # Filter df
        if only_removed:
            self.df = self.df_full[self.df_full['cryoBoostDlLabel'] == "bad"].copy()
        else:
            self.df = self.df_full.copy()
        # Update total batches and reset to first batch
        self.total_batches = (len(self.df) + self.batch_size - 1) // self.batch_size
        self.current_batch = 0
        print(f"Filtered to {len(self.df)} images ({self.total_batches} batches)")
        self.load_batch(0)
        self.prob_counter()


    def prob_counter(self):
        # Calculate indices for current batch
        start_idx = self.current_batch * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.df))
        
        # Get current batch probabilities
        current_batch = self.df.iloc[start_idx:end_idx]
        min_prob = current_batch['cryoBoostDlProbability'].iloc[0]
        max_prob = current_batch['cryoBoostDlProbability'].iloc[-1]
        self.prob_range_label.setText(f"Displayed Probability Range: {min_prob:.3f} - {max_prob:.3f}")


    def filter_by_tiltseries(self, selected_ts):
      
        if selected_ts == "All":
            self.df = self.df_full.copy()
        else:
           self.df = self.df_full[self.df_full['rlnTomoName'] == selected_ts].copy()

        self.total_batches = (len(self.df) + self.batch_size - 1) // self.batch_size
        self.current_batch = 0  
        self.load_batch(0)
        self.prob_counter()


    def load_batch(self, batch_num):
        # Clear current layers
        self.viewer.layers.clear()
        self.current_batch = batch_num
        
        start_idx = batch_num * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.df))
        batch_df = self.df.iloc[start_idx:end_idx]

        image_layers = []
        import time
        startT = time.time()
        print("starting to load batch",flush=True)
        for i, row in batch_df.iterrows():
            img = load_image(row['cryoBoostPNG'])
            # Show each image in the viewer as a separate layer
            layer = self.viewer.add_image(
                img, 
                name=row['cryoBoostPNG'], 
                colormap='gray', 
                blending='additive',
                visible=True 
            )
            image_layers.append(layer)
        print("batch loaded",flush=True)
        endT = time.time()
        print(f"Time taken: {endT - startT} seconds")

        n_images = len(image_layers)
        grid_size = int(np.ceil(np.sqrt(n_images))) 
        self.viewer.grid.shape = (grid_size, grid_size)

        # Calculate image dimensions
        img_height, img_width = image_layers[0].data.shape

        # Add spacing between images
        spacing = 10  # pixels

        # Add label indicators (dot showing current label)
        for i, row in batch_df.reset_index(drop=True).iterrows(): # Have to reset i for each batch
            img = image_layers[i].data
            height, width = img.shape
            
            # Calculate grid position
            grid_row = i // grid_size
            grid_col = i % grid_size
            
            # Calculate image position with spacing
            x = grid_col * (width + spacing)
            y = grid_row * (height + spacing)
            
            # Position point in top-right corner of each image
            point_pos = [[y + 30, x + 30]]  # Offset from corner, using (y,x) ordering
            color = 'green' if row['cryoBoostDlLabel'] == "good" else 'red'
            
            # Add point layer
            point_layer = self.viewer.add_points(
                point_pos,
                name=f'label_indicator_{row["cryoBoostPNG"]}',
                size=30,
                face_color=color,
                border_color=color,
                symbol='disc'
            )
            # Set point layer translation to match image layer
            point_layer.translate = image_layers[i].translate
    

        # Update layer positions based on grid
        for i, layer in enumerate(image_layers):
            # Calculate grid position
            row = i // grid_size
            col = i % grid_size
            
            # Calculate pixel position with spacing
            x = col * (img_width + spacing)
            y = row * (img_height + spacing)
            
            # Update layer translation
            layer.translate = (y, x)  # napari uses (y,x) ordering

        # Enable grid view
        self.viewer.reset_view()

        # Update button states
        self.prev_btn.setEnabled(batch_num > 0)
        self.next_btn.setEnabled(batch_num < self.total_batches - 1)
        self.prob_counter() 

        print(f"Showing batch {batch_num + 1} of {self.total_batches}")
    

    def next_batch(self):
        if self.current_batch < self.total_batches - 1:
            self.load_batch(self.current_batch + 1)
    
    def prev_batch(self):
        if self.current_batch > 0:
            self.load_batch(self.current_batch - 1)


    def on_click(self, layer, event):
        # Get the clicked coordinates in world space
        coordinates = event.position
        x, y = int(coordinates[1]), int(coordinates[0])  # Swap x,y as napari uses (y,x)
    
        # Find which layer was clicked
        clicked_layer = None
        for current_layer in self.viewer.layers:
            if isinstance(current_layer, napari.layers.Image):
                # Get layer position and scale
                translate = current_layer.translate
                scale = current_layer.scale
                
                # Transform world coordinates to layer coordinates
                layer_x = (x - translate[1]) / scale[1]
                layer_y = (y - translate[0]) / scale[0]
                
                # Get image dimensions
                img_height, img_width = current_layer.data.shape
                
                # Check if click is within layer bounds
                if (0 <= layer_x < img_width and 
                    0 <= layer_y < img_height):
                    clicked_layer = current_layer
                    break
        
        if clicked_layer is not None:
            # Get image name from layer
            img_name = clicked_layer.name
            
            # Find corresponding index in DataFrame
            index = self.df[self.df['cryoBoostPNG'] == img_name].index[0]
            
            # Toggle the label
            
            if self.df.loc[index, 'cryoBoostDlLabel'] == 'good':
                invLabel = 'bad'
            if self.df.loc[index, 'cryoBoostDlLabel'] == 'bad':
                invLabel = 'good'
            self.df.loc[index, 'cryoBoostDlLabel'] = invLabel
            #new_label = self.df.loc[index, 'cryoBoostDlLabel']
            print(f"Updated label for {img_name}: {invLabel}")
            
            # Update point color
            color = 'green' if invLabel == 'good' else 'red'
            indicator_layer = self.viewer.layers[f'label_indicator_{img_name}']
            indicator_layer.face_color = color
            indicator_layer.border_color = color 


#%%
def filterTiltsInterActive(inputList, output_folder=None,mode="onFailure"):

    inputBase=os.path.basename(inputList)
    if inputBase=="tiltseries_filtered.star":
        inputListOrg=inputList
        inputList=inputList.replace("tiltseries_filtered.star","tiltseries_labeled.star")
        if mode=="Never" or (mode=="onFailure" and os.path.exists(inputList.replace("tiltseries_filtered.star","DATA_IN_DISTRIBUTION"))):
            print("Skipping manual sort")
            ts=tiltSeriesMeta(inputListOrg)
            ts.writeTiltSeries(output_folder+"tiltseries_filtered.star")
            return   
    print("preparing napari",flush=True)
    viewer = BatchViewer(inputList, output_folder)
    app = QApplication.instance() 
    app.lastWindowClosed.connect(viewer.on_close) 
    napari.run()

if __name__ == '__main__':
    filterTiltsInterActive()
