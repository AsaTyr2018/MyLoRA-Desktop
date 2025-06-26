# MyLoRA Desktop Client

This folder contains a Tkinter based client for interacting with the MyLoRA REST API.
The application now uses a dark themed grid interface inspired by the MyLora web gallery. Grid items display the preview with the file name overlaid at the bottom and the download action uses an accent coloured button.

## Usage

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

Set the `MYLORA_API_URL` environment variable to point to a different server. The default is `http://localhost:5000`.
