.. _api:

API Documentation
=================

RapidNotifyBot provides a simple and flexible API for sending notifications. Users can send a POST request to the bot's API endpoint with their unique API key and custom data.

API Endpoint
------------

- **Endpoint**: `/RapidNotify`
- **Method**: POST
- **Content-Type**: application/json

Request Payload
---------------

The request payload should be a JSON object with the following structure:

.. code-block:: json
    {
        "api_key": "your_unique_api_key",
        "data": {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            ...
        }
    }


- api_key (string, required): Your unique API key.
- data (object, required): Custom key-value data to be included in the notification.

Example Request
---------------

Using cURL:

.. code-block:: bash

    curl -X POST -H "Content-Type: application/json" -d '{"api_key": "your_unique_api_key", "data": {"name": "Amit Das", "github_profile": "github.com/mramitdas"}}' https://rapidnotifybot.com/send-notification

Response
--------

Upon successful submission, the API will respond with a success message:

.. code-block:: json

    {
        "status": "success",
        "message": "Notification sent successfully."
    }

In case of an error, an error message will be returned:

.. code-block:: json

    {
        "status": "error",
        "message": "Invalid API key. Please provide a valid API key."
    }

Please refer to the Contributing Guidelines for more information on error handling and reporting issues.

**Note**: Ensure that you replace placeholders such as ``your_unique_api_key`` with your actual API key and customize the ``data`` payload according to your requirements.

Feel free to add more details or expand on specific aspects based on your bot's functionalities and user needs.
