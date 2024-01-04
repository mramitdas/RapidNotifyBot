===================
FastAPI Project Setup
===================

This guide provides instructions on setting up a FastAPI project along with the creation of a virtual environment.

Create Virtual Environment
--------------------------

1. Open a terminal.

2. Navigate to the root directory of your project.

3. Run the following commands to create a virtual environment:

   .. code-block:: bash

      python -m venv venv

   This will create a virtual environment named "venv" in your project directory.

4. Activate the virtual environment:

   On Windows:

   .. code-block:: bash

      .\venv\Scripts\activate

   On macOS/Linux:

   .. code-block:: bash

      source venv/bin/activate

Install Dependencies
--------------------

Once the virtual environment is activated, you can install the required dependencies using `pip`.

.. code-block:: bash

   pip install -r requirements/dev.txt

This will install the necessary packages specified in the `requirements.txt` file.

Create Environment File
-----------------------

Create a .env file in the root directory of your project and add some random variables:

.. code-block:: bash
   
   DB_URL=mongodb-url
   DB_NAME=telegram-bot
   TABLE_NAME=RapidNotifyBot 
   BOT_KEY=telegram-bot-key


Run FastAPI Application
-----------------------

With the virtual environment activated and dependencies installed, you can now run your FastAPI application.

.. code-block:: bash

   python3 app/main.py

This command starts the development server, and your FastAPI application will be accessible at http://127.0.0.1:8000/.

To test the installation, you can open your web browser or use a tool like `curl` to make requests to your FastAPI application.

Deactivate Virtual Environment
------------------------------

Once you are done working on your FastAPI project, you can deactivate the virtual environment.

.. code-block:: bash

   deactivate

This concludes the setup process for your FastAPI project.

**Note:** Ensure that you have Python and `pip` installed on your system before following these instructions.
