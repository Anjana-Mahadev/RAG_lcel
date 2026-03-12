#!/bin/bash

APP_DIR=/home/ubuntu/RAG_lcel
VENV_DIR=$APP_DIR/venv

echo "Cleaning old services..."

sudo systemctl stop flask_rag fastapi_rag streamlit_rag 2>/dev/null
sudo systemctl disable flask_rag fastapi_rag streamlit_rag 2>/dev/null
sudo rm -f /etc/systemd/system/flask_rag.service
sudo rm -f /etc/systemd/system/fastapi_rag.service
sudo rm -f /etc/systemd/system/streamlit_rag.service
sudo systemctl daemon-reload


echo "Creating FastAPI service..."

sudo tee /etc/systemd/system/fastapi_rag.service > /dev/null <<EOL
[Unit]
Description=FastAPI RAG Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/uvicorn main:app --host 0.0.0.0 --port 8000
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
ExecStart=$VENV_DIR/bin/streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOL


sudo systemctl daemon-reload
sudo systemctl enable fastapi_rag
sudo systemctl enable streamlit_rag
sudo systemctl start fastapi_rag
sudo systemctl start streamlit_rag

echo "✅ Deployment complete!"
echo "Streamlit: http://<EC2_IP>:8501"
echo "FastAPI Docs: http://<EC2_IP>:8000/docs"