import argparse
import json
import random
from pathlib import Path


def _list_task_dirs(tasks_dir: Path, app_prefix: str) -> list[str]:
    task_dirs = [
        path.name
        for path in tasks_dir.iterdir()
        if path.is_dir() and path.name.startswith(f"{app_prefix}-")
    ]
    return sorted(task_dirs)


def _sample_tasks(task_dirs: list[str], count: int, rng: random.Random) -> list[str]:
    if count > len(task_dirs):
        raise ValueError(f"Requested {count} tasks but only found {len(task_dirs)}")
    return rng.sample(task_dirs, count)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic OfficeBench subset.")
    parser.add_argument("--tasks_dir", default="tasks", help="Path to the tasks directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--single", type=int, default=16, help="Number of single-app tasks")
    parser.add_argument("--two", type=int, default=16, help="Number of two-app tasks")
    parser.add_argument("--three", type=int, default=18, help="Number of three-app tasks")
    parser.add_argument(
        "--output",
        default="subset.json",
        help="Output path for subset JSON (relative to repo root)",
    )
    args = parser.parse_args()

    tasks_dir = Path(args.tasks_dir)
    if not tasks_dir.exists():
        raise FileNotFoundError(f"Tasks directory not found: {tasks_dir}")

    rng = random.Random(args.seed)

    single_tasks = _sample_tasks(_list_task_dirs(tasks_dir, "1"), args.single, rng)
    two_tasks = _sample_tasks(_list_task_dirs(tasks_dir, "2"), args.two, rng)
    three_tasks = _sample_tasks(_list_task_dirs(tasks_dir, "3"), args.three, rng)

    all_tasks = single_tasks + two_tasks + three_tasks
    all_tasks_sorted = sorted(
        all_tasks, key=lambda x: (int(x.split("-")[0]), int(x.split("-")[1]))
    )

    subset = {
        "seed": args.seed,
        "counts": {"single": args.single, "two": args.two, "three": args.three},
        "tasks": all_tasks_sorted,
    }

    output_path = Path(args.output)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(subset, f, indent=2)
        f.write("\n")

    print(f"Wrote subset file to {output_path}")


if __name__ == "__main__":
    main()
