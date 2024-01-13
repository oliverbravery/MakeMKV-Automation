# MakeMKV Automation

⚠️ **Warning: This project is no longer actively maintained.**

This project automates the DVD ripping process using WhatsApp as the user interface. Users can send commands and provide the DVD name through WhatsApp messaging, and the automation process will handle the entire DVD ripping process.

## Features

- DVD ripping automation through WhatsApp messaging
- Simple and intuitive user interface
- Easy setup and configuration

## Prerequisites

Before running this project, make sure you have the following prerequisites installed:

- Python 3.x
- MakeMKV software
- WhatsApp account

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/oliverbravery/MakeMKV-Automation.git
    ```

2. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

3. Setup the `.env` file:

    - Rename the `.env.template` file to `.env`.
    - Update the values in the `.env` file with your Whatsapp API credentials and other required fields.

4. Run the application:

    ```shell
    python main.py
    ```

## Usage

1. Start makeMKV and run the automation process.

    ```shell
    python main.py
    ```

2. Insert the DVD into the DVD reader.

3. The automation process will start automatically. The process will take a few minutes to complete and will update the user through WhatsApp messaging.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
