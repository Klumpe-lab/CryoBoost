import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

# =============================================================================
# 1. Synthetic 3D Segmentation Dataset (MRI-like volumes with gray values)
# =============================================================================
class SyntheticSegmentation3DDataset(Dataset):
    def __init__(self, num_samples=50, volume_size=64):
        """
        Creates synthetic 3D volumes with a random cuboid target and Gaussian noise.
        Each sample is a 4D tensor of shape (1, D, H, W) for both the volume and mask.
        """
        super(SyntheticSegmentation3DDataset, self).__init__()
        self.num_samples = num_samples
        self.volume_size = volume_size

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # Create a blank volume and mask.
        vol = np.zeros((self.volume_size, self.volume_size, self.volume_size), dtype=np.float32)
        mask = np.zeros((self.volume_size, self.volume_size, self.volume_size), dtype=np.float32)
        
        # Random cuboid parameters for the segmentation target.
        min_size = self.volume_size // 8
        max_size = self.volume_size // 2
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        d = random.randint(min_size, max_size)
        x1 = random.randint(0, self.volume_size - w)
        y1 = random.randint(0, self.volume_size - h)
        z1 = random.randint(0, self.volume_size - d)
        x2 = x1 + w
        y2 = y1 + h
        z2 = z1 + d

        # Set the mask and corresponding higher-intensity region in the volume.
        mask[z1:z2, y1:y2, x1:x2] = 1.0
        vol[z1:z2, y1:y2, x1:x2] = 1.0
        
        # Add Gaussian noise to simulate MRI noise.
        noise = np.random.normal(loc=0.0, scale=0.2, size=(self.volume_size, self.volume_size, self.volume_size))
        vol = vol + noise
        vol = np.clip(vol, 0, 1)
        
        # Add a channel dimension: resulting shape is (1, D, H, W)
        vol = np.expand_dims(vol, axis=0)
        mask = np.expand_dims(mask, axis=0)
        
        # Convert to torch tensors.
        vol = torch.tensor(vol, dtype=torch.float32)
        mask = torch.tensor(mask, dtype=torch.float32)
        return vol, mask

# =============================================================================
# 2. Define U-Net 3D Components
# =============================================================================
class DoubleConv3D(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv3D, self).__init__()
        self.double_conv = nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )
    def forward(self, x):
        return self.double_conv(x)

class DownBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DownBlock, self).__init__()
        self.conv = DoubleConv3D(in_channels, out_channels)
        self.pool = nn.MaxPool3d(2)
    def forward(self, x):
        x_conv = self.conv(x)
        x_pooled = self.pool(x_conv)
        return x_conv, x_pooled

class UpBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        """
        in_channels: number of channels coming from the previous layer (to upsample)
        out_channels: desired number of channels after upsampling.
        """
        super(UpBlock, self).__init__()
        self.up = nn.ConvTranspose3d(in_channels, out_channels, kernel_size=2, stride=2)
        # After upsampling, we concatenate skip connection (which has out_channels channels)
        # so the double conv receives 2*out_channels channels.
        self.conv = DoubleConv3D(out_channels * 2, out_channels)
    def forward(self, x, x_skip):
        x = self.up(x)
        # If necessary, pad x so that its dimensions match x_skip.
        diffZ = x_skip.size(2) - x.size(2)
        diffY = x_skip.size(3) - x.size(3)
        diffX = x_skip.size(4) - x.size(4)
        x = nn.functional.pad(x, [diffX // 2, diffX - diffX // 2,
                                    diffY // 2, diffY - diffY // 2,
                                    diffZ // 2, diffZ - diffZ // 2])
        # Concatenate along the channel dimension.
        x = torch.cat([x_skip, x], dim=1)
        return self.conv(x)

# =============================================================================
# 3. Define the 3D U-Net Architecture
# =============================================================================
class UNet3D(nn.Module):
    def __init__(self, n_channels=1, n_classes=1):
        super(UNet3D, self).__init__()
        self.inc = DoubleConv3D(n_channels, 16)         # Initial conv block.
        self.down1 = DownBlock(16, 32)                    # Downsample 1.
        self.down2 = DownBlock(32, 64)                    # Downsample 2.
        self.down3 = DownBlock(64, 128)                   # Downsample 3.
        
        # Bottleneck.
        self.bottom = DoubleConv3D(128, 256)
        
        # Upsampling path with skip-connections.
        self.up3 = UpBlock(256, 128)                      # Upsample 1: combines with skip from down3.
        self.up2 = UpBlock(128, 64)                       # Upsample 2: combines with skip from down2.
        self.up1 = UpBlock(64, 32)                        # Upsample 3: combines with skip from down1.
        self.outc = nn.Conv3d(32, n_classes, kernel_size=1)
        
    def forward(self, x):
        # Encoder path.
        x1 = self.inc(x)                 # -> (B,16, D, H, W)
        x2, x1_down = self.down1(x1)       # x2 -> (B,32, D, H, W); x1_down -> (B,32, D/2, H/2, W/2)
        x3, x2_down = self.down2(x1_down)  # x3 -> (B,64, D/2, H/2, W/2); x2_down -> (B,64, D/4, H/4, W/4)
        x4, x3_down = self.down3(x2_down)  # x4 -> (B,128, D/4, H/4, W/4); x3_down -> (B,128, D/8, H/8, W/8)
        
        # Bottleneck.
        x_bottom = self.bottom(x3_down)   # -> (B,256, D/8, H/8, W/8)
        
        # Decoder path.
        x = self.up3(x_bottom, x4)        # -> (B,128, D/4, H/4, W/4)
        x = self.up2(x, x3)               # -> (B,64, D/2, H/2, W/2)
        x = self.up1(x, x2)               # -> (B,32, D, H, W)
        logits = self.outc(x)             # -> (B, n_classes, D, H, W)
        return torch.sigmoid(logits)

# =============================================================================
# 4. Training Loop for the Segmentation Model
# =============================================================================
def train_model(model, dataloader, criterion, optimizer, num_epochs=10, device='cpu'):
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for volumes, masks in tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}"):
            volumes = volumes.to(device)
            masks = masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(volumes)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * volumes.size(0)
            
        epoch_loss = running_loss / len(dataloader.dataset)
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}")

# =============================================================================
# 5. Visualization of Central Slices from 3D Volumes
# =============================================================================
def visualize_results_3d(model, dataset, device='cpu', num_samples=3):
    model.eval()
    fig, axs = plt.subplots(num_samples, 3, figsize=(12, 4*num_samples))
    
    for i in range(num_samples):
        vol, mask = dataset[i]
        vol = vol.to(device).unsqueeze(0)  # add batch dimension.
        with torch.no_grad():
            pred = model(vol)
            
        # Extract the central slice along the depth dimension.
        depth = vol.shape[2]
        center_slice = depth // 2
        vol_slice = vol[0, 0, center_slice, :, :].cpu().numpy()
        mask_slice = mask[0, center_slice, :, :].cpu().numpy()
        pred_slice = pred[0, 0, center_slice, :, :].cpu().numpy()
        
        ax0 = axs[i, 0] if num_samples > 1 else axs[0]
        ax1 = axs[i, 1] if num_samples > 1 else axs[1]
        ax2 = axs[i, 2] if num_samples > 1 else axs[2]
        
        ax0.imshow(vol_slice, cmap='gray')
        ax0.set_title("Noisy Input (Central Slice)")
        ax0.axis('off')
        
        ax1.imshow(mask_slice, cmap='gray')
        ax1.set_title("Ground Truth (Central Slice)")
        ax1.axis('off')
        
        ax2.imshow(pred_slice, cmap='gray')
        ax2.set_title("Predicted (Central Slice)")
        ax2.axis('off')
    
    plt.tight_layout()
    plt.show()

# =============================================================================
# 6. Main Function: Dataset, Model, Training, and Visualization
# =============================================================================
def main():
    # Use GPU if available.
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Hyperparameters.
    num_samples = 50
    volume_size = 64
    batch_size = 2
    num_epochs = 10
    learning_rate = 0.001
    
    # Initialize dataset and dataloader.
    dataset = SyntheticSegmentation3DDataset(num_samples=num_samples, volume_size=volume_size)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Initialize model with UNet3D for better performance on noisy data.
    model = UNet3D(n_channels=1, n_classes=1).to(device)
    criterion = nn.BCELoss()  # Binary Cross Entropy Loss.
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    print("Starting training with UNet3D on synthetic 3D volumes...")
    train_model(model, dataloader, criterion, optimizer, num_epochs=num_epochs, device=device)
    
    # Visualize a few central slices.
    visualize_results_3d(model, dataset, device=device, num_samples=3)

if __name__ == '__main__':
    main()