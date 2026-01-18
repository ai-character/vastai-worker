"""Vast.ai PyWorker configuration for the image generator service.

Based on vast-ai/pyworker comfyui-json example.
"""

import random
import sys

from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# Model server configuration
MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = 8080
MODEL_LOG_FILE = "/app/logs/handler.log"
MODEL_HEALTHCHECK_ENDPOINT = "/health"

# Log messages to detect readiness
MODEL_LOAD_LOG_MSG = [
    "Running on http://",
    "ComfyUI ready. Starting HTTP server",
]

MODEL_ERROR_LOG_MSGS = [
    "Traceback (most recent call last):",
    "RuntimeError:",
    "CUDA out of memory",
    "ComfyUI did not start",
]

MODEL_INFO_LOG_MSGS = [
    "Waiting for ComfyUI",
]

# Benchmark dataset - simple health checks
benchmark_dataset = [
    {
        "action": "health_check"
    }
    for _ in range(4)
]

worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    model_healthcheck_url=MODEL_HEALTHCHECK_ENDPOINT,
    handlers=[
        HandlerConfig(
            route="/generate",
            allow_parallel_requests=False,  # ComfyUI processes one at a time
            max_queue_time=300.0,  # 5 minute queue timeout
            benchmark_config=BenchmarkConfig(
                dataset=benchmark_dataset,
            ),
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=MODEL_LOAD_LOG_MSG,
        on_error=MODEL_ERROR_LOG_MSGS,
        on_info=MODEL_INFO_LOG_MSGS,
    ),
)

if __name__ == "__main__":
    Worker(worker_config).run()
