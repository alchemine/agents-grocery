# base-project: Basic Project Environment for Python Development

This project aims to build a Python project environment based on various useful tools.

## 0. Quickstart

- Install dependencies (runtime + tests)
  ```bash
  conda create -n base-project python=3.12 -y
  conda activate base-project
  pip install -r requirements.txt -r tests/requirements.txt
  ```
- Run tests
  ```bash
  pytest -q
  ```
- Run application (FastAPI)
  ```bash
  python -m app.main
  # or
  uvicorn app:application --host 0.0.0.0 --port 8000 --reload
  ```
  - Open `http://localhost:8000/docs` in your browser

## 1. Development Environment

To provide a consistent development experience across different platforms, I have set up the following environment:

- **Dev Container**: Utilizes Visual Studio Code's Dev Containers to provide a consistent development environment.
  - Configuration file: `.devcontainer/devcontainer.json`
- **Docker**: Supports containerization for deployment and testing.
  - Configuration files: `Dockerfile`, `docker-compose.yml`
- **Python**:
  - Project configuration: `pyproject.toml`
  - Dependency management: `requirements.txt`

## 2. Core Utilities

The `src/common/` directory includes several utility modules to enhance development productivity.

### 2.1 Timer

Provides functionality to measure code execution time.

1. **Context manager**

   ```python
   from time import sleep
   from src.common.timer import Timer

   with Timer("Task 1"):
       # Here is code snippet
       sleep(1)
   ```

   Output:

```
2025-08-09 00:19:37 | service_name | INFO     | [START]   Task 1
2025-08-09 00:19:38 | service_name | INFO     | [SUCCESS] Task 1 (0.02m)
```

2. **Decorator**

   ```python
   from time import sleep
   from src.common.timer import Timer, T

   @Timer("Task 1")
   def fn1():
       sleep(1)

   @T
   def fn2():
       sleep(1)

   fn1()
   fn2()
   ```

   Output:

```
2025-08-09 00:19:37 | service_name | INFO     | [START]   Task 1
2025-08-09 00:19:38 | service_name | INFO     | [SUCCESS] Task 1 (0.02m)
2025-08-09 00:19:38 | service_name | INFO     | [START]   fn2
2025-08-09 00:19:39 | service_name | INFO     | [SUCCESS] fn2 (0.02m)
```

### 2.2 Depth logging

Provides functionality to visualize the function call stack and measure execution time.

```python
from src.common.depth_logging import D

@D
def main():
    main1()
    main2()

@D
def main1():
    main11()
    main12()

@D
def main11():
    return

@D
def main12():
    return

@D
def main2():
    main21()

@D
def main21():
    return

main()
```

Output:

```
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.1              | main()
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.1.1            | main1()
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.1.1.1          | main11()
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.1.1.1          | main11() (0.00m)
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.1.2.1          | main12()
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.1.2.1          | main12() (0.00m)
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.1.1            | main1() (0.00m)
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.2.1            | main2()
2025-08-09 00:03:53 | service_name | INFO     | [START]   1.2.1.1          | main21()
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.2.1.1          | main21() (0.00m)
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.2.1            | main2() (0.00m)
2025-08-09 00:03:53 | service_name | INFO     | [SUCCESS] 1.1              | main() (0.00m)
```

### 2.3 Logging

Records logs to both console and file. \
Logs are saved in the `logs/YYYY-MM-DD.log` file for easy tracking and debugging. \
Utility functions allow for easy use.

```python
from src.common.logger import (
    slog,
    log_info,
    log_success,
    log_error,
    log_warning,
    log_api,
    STYLES,
)

log_info("This is an info message.")
log_success("This is a success message.")
log_error("This is an error message.")
log_warning("This is a warning message.")
log_api("This is an API message.")
for style in STYLES:
    slog(f"This is a {style} message.", style=style)
```

![alt text](assets/image.png)

### 2.4 Safe HTTP requests

Allows for safe HTTP requests with error handling and logging.

Synchronous:

```python
from src.common.request_utils import safe_request

url = "https://httpbin.org/post"
payload = {"key": "value"}
response = safe_request(url, json=payload, method="post")
```

Asynchronous:

```python
import aiohttp
from src.common.request_utils import async_safe_request

async with aiohttp.ClientSession() as session:
    url = "https://httpbin.org/post"
    payload = {"key": "value"}
    response = await async_safe_request(session, url, json=payload, method="post")
```

---

## 3. Playground

- You can find simple validation/demo scripts in the `playground/` directory.
  - Example: `playground/docs_update-readme/verify_readme_examples.py`

I hope this project helps improve your Python development experience!
