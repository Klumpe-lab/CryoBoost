import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)
# Define the PCN model with corrected dimensions
class PCN(nn.Module):
    def __init__(self, num_points=2048, bottleneck_size=1024):
        super(PCN, self).__init__()
        
        # Encoder
        self.conv1 = nn.Conv1d(3, 128, 1)
        self.conv2 = nn.Conv1d(128, 256, 1)
        self.conv3 = nn.Conv1d(256, 512, 1)
        self.conv4 = nn.Conv1d(512, bottleneck_size, 1)
        
        # Decoder (Coarse)
        self.fc1 = nn.Linear(bottleneck_size, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, 3 * 1024)  # Coarse output: 1024 points
        
        # Decoder (Fine) - CORRECTED DIMENSIONS
        self.conv5 = nn.Conv1d(3 + bottleneck_size, 512, 1)  # Changed from 1024+3
        self.conv6 = nn.Conv1d(512, 512, 1)
        self.conv7 = nn.Conv1d(512, 3, 1)
        
        self.num_points = num_points
        self.bottleneck_size = bottleneck_size
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # Encoder
        x = x.transpose(1, 2)  # [B, N, 3] -> [B, 3, N]
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = self.conv4(x)  # [B, bottleneck_size, N]
        
        # Global feature
        global_feat = torch.max(x, 2, keepdim=True)[0]  # [B, bottleneck_size, 1]
        global_feat = global_feat.view(-1, self.bottleneck_size)  # [B, bottleneck_size]
        
        # Decoder (Coarse)
        x = F.relu(self.fc1(global_feat))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)  # [B, 3 * 1024]
        
        coarse = x.view(batch_size, 1024, 3)  # [B, 1024, 3]
        
        # Decoder (Fine) - CORRECTED IMPLEMENTATION
        coarse_features = coarse.transpose(1, 2)  # [B, 3, 1024]
        
        # Expand global feature and concatenate with coarse output
        global_feat_expanded = global_feat.unsqueeze(2).expand(batch_size, self.bottleneck_size, 1024)
        point_features = torch.cat([coarse_features, global_feat_expanded], dim=1)  # [B, 3+bottleneck_size, 1024]
        
        x = F.relu(self.conv5(point_features))
        x = F.relu(self.conv6(x))
        x = self.conv7(x)  # [B, 3, 1024]
        
        fine = x.transpose(1, 2)  # [B, 1024, 3]
        
        return coarse, fine
# Create a simple dataset for demonstration
class PointCloudDataset(Dataset):
    def __init__(self, num_samples=1000, num_points=2048, partial_points=512):
        self.num_samples = num_samples
        self.num_points = num_points
        self.partial_points = partial_points
        
        # Generate random point clouds for demonstration
        self.complete_point_clouds = []
        for _ in range(num_samples):
            # Generate a sphere as an example
            phi = np.random.uniform(0, 2 * np.pi, num_points)
            costheta = np.random.uniform(-1, 1, num_points)
            theta = np.arccos(costheta)
            r = 1.0
            
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            
            points = np.stack([x, y, z], axis=1)
            self.complete_point_clouds.append(points)
    
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        complete_pc = self.complete_point_clouds[idx]
        
        # Create partial point cloud by randomly selecting points
        indices = np.random.choice(self.num_points, self.partial_points, replace=False)
        partial_pc = complete_pc[indices]
        
        return {
            'partial': torch.FloatTensor(partial_pc),
            'complete': torch.FloatTensor(complete_pc)
        }
# Define the Chamfer Distance loss
def chamfer_distance(x, y):
    # x: [B, N, 3]
    # y: [B, M, 3]
    
    batch_size = x.size(0)
    n_points = x.size(1)
    m_points = y.size(1)
    
    # Reshape to compute pairwise distances
    x = x.unsqueeze(2).repeat(1, 1, m_points, 1)  # [B, N, M, 3]
    y = y.unsqueeze(1).repeat(1, n_points, 1, 1)  # [B, N, M, 3]
    
    # Compute squared distances
    dist = torch.sum((x - y) ** 2, dim=3)  # [B, N, M]
    
    # Minimum distances in both directions
    min_dist_x_to_y = torch.min(dist, dim=2)[0]  # [B, N]
    min_dist_y_to_x = torch.min(dist, dim=1)[0]  # [B, M]
    
    # Average over points
    chamfer_x_to_y = torch.mean(min_dist_x_to_y, dim=1)  # [B]
    chamfer_y_to_x = torch.mean(min_dist_y_to_x, dim=1)  # [B]
    
    # Sum both directions
    chamfer_dist = chamfer_x_to_y + chamfer_y_to_x  # [B]
    
    # Average over batch
    return torch.mean(chamfer_dist)
# Visualization function
def visualize_point_cloud(partial, complete, coarse, fine, title, save_dir="results"):
    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    fig = plt.figure(figsize=(20, 5))
    
    # Partial point cloud
    ax = fig.add_subplot(141, projection='3d')
    ax.scatter(partial[:, 0], partial[:, 1], partial[:, 2], c='r', s=5)
    ax.set_title('Partial Point Cloud')
    ax.set_axis_off()
    
    # Complete point cloud (ground truth)
    ax = fig.add_subplot(142, projection='3d')
    ax.scatter(complete[:, 0], complete[:, 1], complete[:, 2], c='g', s=5)
    ax.set_title('Complete Point Cloud (Ground Truth)')
    ax.set_axis_off()
    
    # Coarse predicted point cloud
    ax = fig.add_subplot(143, projection='3d')
    ax.scatter(coarse[:, 0], coarse[:, 1], coarse[:, 2], c='b', s=5)
    ax.set_title('Coarse Prediction')
    ax.set_axis_off()
    
    # Fine predicted point cloud
    ax = fig.add_subplot(144, projection='3d')
    ax.scatter(fine[:, 0], fine[:, 1], fine[:, 2], c='purple', s=5)
    ax.set_title('Fine Prediction')
    ax.set_axis_off()
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(f"{save_dir}/{title}.png")
    plt.close()
# Training function
def train(model, train_loader, optimizer, epoch, device):
    model.train()
    total_loss = 0
    
    for batch_idx, data in enumerate(train_loader):
        partial = data['partial'].to(device)
        complete = data['complete'].to(device)
        
        optimizer.zero_grad()
        coarse, fine = model(partial)
        
        # Compute loss
        loss_coarse = chamfer_distance(coarse, complete)
        loss_fine = chamfer_distance(fine, complete)
        loss = loss_coarse + loss_fine
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        if batch_idx % 10 == 0:
            print(f'Epoch: {epoch} [{batch_idx}/{len(train_loader)}] Loss: {loss.item():.6f}')
    
    avg_loss = total_loss / len(train_loader)
    print(f'====> Epoch: {epoch} Average loss: {avg_loss:.6f}')
    return avg_loss
# Test function to visualize predictions
def test(model, test_dataset, device, epoch, save_dir="results"):
    model.eval()
    os.makedirs(save_dir, exist_ok=True)
    
    with torch.no_grad():
        for i in range(min(5, len(test_dataset))):  # Visualize first 5 samples
            data = test_dataset[i]
            partial = data['partial'].unsqueeze(0).to(device)
            complete = data['complete']
            
            coarse, fine = model(partial)
            
            # Convert to numpy for visualization
            partial_np = partial[0].cpu().numpy()
            complete_np = complete.numpy()
            coarse_np = coarse[0].cpu().numpy()
            fine_np = fine[0].cpu().numpy()
            
            visualize_point_cloud(
                partial_np, complete_np, coarse_np, fine_np,
                f"Epoch_{epoch}_Sample_{i}", save_dir
            )
# Main function
def main():
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    # Check if CUDA is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Hyperparameters
    batch_size = 32
    num_epochs = 20
    learning_rate = 0.0001
    num_points = 2048
    partial_points = 512
    
    # Create dataset and dataloader
    train_dataset = PointCloudDataset(num_samples=1000, num_points=num_points, partial_points=partial_points)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    
    # Create test dataset for visualization
    test_dataset = PointCloudDataset(num_samples=10, num_points=num_points, partial_points=partial_points)
    
    # Create model
    model = PCN(num_points=num_points).to(device)
    
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training loop
    losses = []
    for epoch in range(1, num_epochs + 1):
        loss = train(model, train_loader, optimizer, epoch, device)
        losses.append(loss)
        
        # Test and visualize every 5 epochs
        if epoch % 5 == 0 or epoch == 1:
            test(model, test_dataset, device, epoch)
    
    # Plot loss curve
    plt.figure(figsize=(10, 5))
    plt.plot(losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.savefig("results/loss_curve.png")
    plt.close()
    
    # Save the model
    torch.save(model.state_dict(), "results/pcn_model.pth")
    print("Training completed and model saved.")
    
    # Final test with saved model
    print("Generating final test visualizations...")
    test(model, test_dataset, device, "final", save_dir="results/final_predictions")
if __name__ == "__main__":
    main()