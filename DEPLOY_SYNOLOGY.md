# Deployment Guide for Synology NAS

This guide will help you install the Network Monitor application on your Synology NAS using Container Manager (Docker).

## New: Automatic Configuration

We have updated the application to use an **internal Reverse Proxy**.
**You no longer need to manually configure the NAS IP address.** The application will work automatically wherever you install it.

## 1. Transfer to NAS

1.  Create a folder on your NAS, for example `/docker/network-monitor`.
2.  Copy **all** project files and folders (including `backend`, `frontend`, `docker-compose.yml`) into this folder.

## 2. Start with Container Manager

1.  Open **Container Manager** on your Synology.
2.  Go to the **Project** tab.
3.  Click on **Create**.
4.  Fill in the fields:
    *   **Project Name**: `network-monitor`
    *   **Path**: Select the folder `/docker/network-monitor` where you copied the files.
    *   **Source**: Select "Create docker-compose.yml" (the system will automatically detect the file in the folder).
5.  Click **Next** -> **Next** -> **Done**.

The NAS will start downloading the base images and building the containers. The first time might take a few minutes.

## 3. Accessing the Application

Once the containers are started (green dot), you can access:

*   **Frontend (Dashboard)**: `http://NAS-IP:3200`
    *   *The frontend will automatically contact the backend without needing extra configuration.*
*   **InfluxDB**: `http://NAS-IP:8086`

## Troubleshooting

*   **Ports Occupied**: If you receive an error that the ports are already in use, modify the `docker-compose.yml` file by changing the left port.
    Example to change the frontend port to 3005:
    ```yaml
    ports:
      - "3005:80"
    ```
