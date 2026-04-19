```bash
#!/bin/bash

set -e

APP_DIR=/home/ubuntu/RAG_lcel
REPO_URL=https://github.com/Anjana-Mahadev/RAG_lcel.git

echo "Updating system..."
sudo apt update -y

echo "Installing required packages..."
sudo apt install python3-pip python3-venv git -y

echo "Cloning repository..."
if [ ! -d "$APP_DIR" ]; then
    git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating venv and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn

echo "Creating FastAPI service..."

sudo tee /etc/systemd/system/fastapi_rag.service > /dev/null <<EOL
[Unit]
Description=FastAPI RAG Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

echo "Creating Streamlit service..."

sudo tee /etc/systemd/system/streamlit_rag.service > /dev/null <<EOL
[Unit]
Description=Streamlit RAG Frontend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOL

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling services..."
sudo systemctl enable fastapi_rag
sudo systemctl enable streamlit_rag

echo "Starting services..."
sudo systemctl start fastapi_rag
sudo systemctl start streamlit_rag

echo "Deployment complete!"

echo "Access your app:"
echo "Streamlit UI: http://EC2_PUBLIC_IP:8501"
echo "FastAPI Docs: http://EC2_PUBLIC_IP:8000/docs"
```
