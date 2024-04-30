import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np

# 定義數據集類別
class MyDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

# 讀取數據集
def read_data(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    data = []
    labels = []
    for line in lines:
        values = line.strip().split(',')
        data.append([float(x) for x in values[:-1]])  # 將前9個數字作為特徵
        labels.append(int(values[-1]))  # 最後一個數字作為標籤
    
    return data, labels

# 將數據轉換為 PyTorch 的 Tensor
def convert_to_tensor(data, labels):
    data_tensors = torch.tensor(data, dtype=torch.float32)
    labels_tensor = torch.tensor(labels, dtype=torch.float32)
    return data_tensors, labels_tensor

# 定義模型
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.fc1 = nn.Linear(10, 30)
        self.fc2 = nn.Linear(30, 30)
        self.fc3 = nn.Linear(30, 30)
        self.fc4 = nn.Linear(30, 30)
        self.fc5 = nn.Linear(30, 1)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.sigmoid(self.fc5(x))
        return x

# 訓練模型
def train_model(model, dataloader, criterion, optimizer, num_epochs):
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
        epoch_loss = running_loss / len(dataloader.dataset)
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss}")

# 使用模型進行預測
def predict_new_data(model, new_data):
    new_data_tensor = torch.tensor(new_data, dtype=torch.float32)
    predictions = model(new_data_tensor)
    return predictions

# 計算準確率
def calculate_accuracy(predictions, labels):
    # 將預測概率轉換為二元標籤
    rounded_predictions = (predictions >= 0.6).float()
    # 比較預測結果和實際標籤，計算正確預測的比例
    correct = (rounded_predictions == labels).float()
    accuracy = correct.sum() / len(correct)
    return accuracy.item()

# 主函數
def main():
    # 讀取數據集
    data, labels = read_data("your_dataset.txt")
    
    # 將數據轉換為 PyTorch Tensor
    data_tensors, labels_tensor = convert_to_tensor(data, labels)
    
    # 定義 DataLoader
    dataset = MyDataset(data_tensors, labels_tensor)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # 初始化模型、損失函數和優化器
    model = MyModel()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 讀取新數據集
    new_data, _ = read_data("new_data.txt")

    times = 20
    accuracy = 0.0
    while accuracy < 0.8:
        # 訓練模型
        train_model(model, dataloader, criterion, optimizer, num_epochs=5)
        
        # 使用模型進行預測
        predictions = predict_new_data(model, new_data)
        
        # 計算準確率
        accuracy = calculate_accuracy(predictions, labels_tensor)
        print(f"Accuracy: {accuracy}")

        times-=1
        if times<=0:
            print("over")
            break

main()
