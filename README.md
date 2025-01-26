# Vehicle Fine Checker

## Overview

This project allows you to check if your vehicle has any fines in Vietnam.

## Setup Instructions

### 1. Clone the repository

Pull this repository to your local environment:

```bash
git init
git clone https://github.com/duytanisme/check_phat_nguoi.git
```

### 2. Install all required libraries

Run this command in your current folder that contains the source code.

If you are working in a venv, make sure that you already activated the venv to prevent installing libraries globally in
your computer.

```bash
python install -r requirements.txt
```

### 3. Run the main.py

You need to provide a TikTok user ID in .env file. If you don't have it, just create a new .env file, then add USER_ID.
Eg:

```text
USER_ID=@target_user_id
```

Or you can explicitly hard code the user ID in main.py.

```python
USER_ID = "@target_user_id"
```

Run the main function to start working continuously.

```bash
python main.py
```

### 4. Dockerize

**Important**: For those who use docker, please remove any parts of the source code that are related to "pyttsx3". This
library is used to read out the messages that are logged into terminal, which does not work in ubuntu OS.

Build the docker image:

```bash
docker build -t image_name .
```

If you want to run the container normally, run this command:

```bash
docker run --name container_name -d image_name
```

If you want to automatically sync your changes to the codes inside the container, run this command instead:

- For Windows users:

```bash
docker run --name container_name -d -v ${pwd}:/app image_name
```

- For those who use macOS or Linux-based OS, replace "{pwd}" with "(pwd)" (curly bracket to normal bracket):

```bash
docker run --name container_name -d -v $(pwd):/app image_name
```

Note: Replace "image_name" and "container_name" with your desired names.

### Notes

If you want to change the voice to read the messages, change voice by index. By default, voice uses the one that has
index 1:

```python
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[1].id)
```
