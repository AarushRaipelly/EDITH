import heapq
import time
import threading
from typing import Dict, Any, List, Optional, Callable

class TaskItem:
    def __init__(self, task_id: str, description: str, priority: int, action: Callable[..., Any], args: tuple = (), kwargs: dict = None, condition: Callable[[], bool] = None) -> None:
        self.task_id = task_id
        self.description = description
        # Priority mapping: 1 (Highest) to 3 (Lowest). Heapq sorts ascending.
        self.priority = priority
        self.action = action
        self.args = args
        self.kwargs = kwargs or {}
        self.condition = condition
        self.created_at = time.time()
        self.status = "pending"  # "pending", "running", "completed", "cancelled"

    def __lt__(self, other: 'TaskItem') -> bool:
        if self.priority == other.priority:
            return self.created_at < other.created_at
        return self.priority < other.priority

class EdithTaskManager:
    def __init__(self) -> None:
        self.queue: List[TaskItem] = []
        self.tasks_map: Dict[str, TaskItem] = {}
        self.lock = threading.Lock()
        self._running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def add_task(self, task_id: str, description: str, priority: int, action: Callable[..., Any], args: tuple = (), kwargs: dict = None, condition: Callable[[], bool] = None) -> None:
        """Adds a task to the priority queue."""
        task = TaskItem(task_id, description, priority, action, args, kwargs, condition)
        with self.lock:
            heapq.heappush(self.queue, task)
            self.tasks_map[task_id] = task

    def cancel_task(self, task_id: str) -> bool:
        """Cancels a pending or running task."""
        with self.lock:
            task = self.tasks_map.get(task_id)
            if task and task.status in ("pending", "running"):
                task.status = "cancelled"
                return True
        return False

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Returns details of all registered tasks."""
        with self.lock:
            return [
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "created_at": t.created_at
                }
                for t in self.tasks_map.values()
            ]

    def _worker_loop(self) -> None:
        """Background loop executing items in priority order."""
        while self._running:
            task_to_run: Optional[TaskItem] = None
            with self.lock:
                # Filter out tasks whose conditions aren't met yet or are cancelled
                non_matching = []
                while self.queue:
                    candidate = heapq.heappop(self.queue)
                    if candidate.status == "cancelled":
                        continue
                    if candidate.condition and not candidate.condition():
                        non_matching.append(candidate)
                        continue
                    
                    task_to_run = candidate
                    break

                # Re-add non-matching conditions
                for t in non_matching:
                    heapq.heappush(self.queue, t)

            if task_to_run:
                try:
                    task_to_run.status = "running"
                    task_to_run.action(*task_to_run.args, **task_to_run.kwargs)
                    task_to_run.status = "completed"
                except Exception as e:
                    task_to_run.status = f"failed: {str(e)}"
            
            time.sleep(1.0)

    def shutdown(self) -> None:
        """Gracefully shuts down task queues."""
        self._running = False
