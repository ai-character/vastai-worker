"""Vast.ai PyWorker configuration for the image generator service.

Based on vast-ai/pyworker comfyui-json example.
"""


from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# Model server configuration
MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = 8080
MODEL_LOG_FILE = "/app/logs/handler.log"

# Log messages to detect readiness
# PyWorker uses PREFIX matching - log line must START with these strings
MODEL_LOAD_LOG_MSG = [
    " * Running on http://",  # Flask's actual startup message format
    "READY: ComfyUI ready",   # Our custom readiness marker
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

def image_workload_calculator(payload: dict) -> float:
    """Calculate workload for image generation requests.
    
    Returns a constant value since image generation has roughly constant cost.
    """
    # Health checks are cheap
    if payload.get("action") == "health_check":
        return 1.0
    # Image generation is expensive - use constant cost
    return 100.0


worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    handlers=[
        HandlerConfig(
            route="/generate",
            allow_parallel_requests=False,  # ComfyUI processes one at a time
            max_queue_time=300.0,  # 5 minute queue timeout
            workload_calculator=image_workload_calculator,
            benchmark_config=BenchmarkConfig(
                dataset=benchmark_dataset,
                runs=4,
                concurrency=1,  # Serial since allow_parallel_requests=False
            ),
        ),
        HandlerConfig(
            route="/health",
            allow_parallel_requests=True,
            workload_calculator=lambda _: 1.0,
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
