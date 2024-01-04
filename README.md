# RapidNotifyBot

**A Python FastAPI-based Telegram notification bot with a simple API.**


## Introduction
RapidNotifyBot is a lightweight Telegram bot designed to facilitate quick and easy communication by providing a straightforward API. Users can send POST requests to the bot's API endpoint with their unique API key in the request body, and the bot will forward the provided data to the corresponding Telegram user.

## Features

- **Easy to Use**: The API is designed for simplicity. Users only need to send a POST request with their API key and the desired data to trigger a notification.
- **Customizable**: Users have the flexibility to customize the content of the notifications by sending different data in the request body.
- **Tech Stack**: Built with Python and FastAPI, RapidNotifyBot ensures fast and efficient communication.

## How to Use

- **Obtain API Key**: Each user needs to obtain a unique API key from RapidNotifyBot(t.me/rapidnotifybot).
- **Send Notification**: To send a notification, make a POST request to the bot's API endpoint (/RapidNotify) with the API key and desired data in the request body.

    Example Request:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"api_key": "your_unique_api_key", "data": {"name": "Amit Das", "github_profile": "github.com/mramitdas"}}' https://endpoint.com/RapidNotify
    ```
## Contributing

Contributions are welcome! Check out the [Contributing Guidelines](CONTRIBUTING.md).

## Documentation

- Installation Guide: [docs/installation.rst](docs/installation.rst)
- API Usage Guide: [docs/api.rst](docs/api.rst)

## Community and Code of Conduct

- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, [Amit Das](https://github.com/mramitdas/) has waived all copyright and related or neighboring rights to this work.

## Contact

For support or inquiries, please contact [Amit Das](https://github.com/mramitdas/) at [mramitdas99@gmail.com](mailto:mramitdas99@gmail.com)
