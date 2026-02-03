import argparse
import json
import subprocess
import sys
from pathlib import Path


def _list_subtasks(task_dir: Path) -> list[str]:
    subtasks_dir = task_dir / "subtasks"
    if not subtasks_dir.exists():
        return []
    subtask_files = sorted(subtasks_dir.glob("*.json"), key=lambda p: int(p.stem))
    return [path.stem for path in subtask_files]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or print commands for a subset.")
    parser.add_argument("--subset_file", default="subset.json", help="Path to subset JSON")
    parser.add_argument("--docker_name", default="officebench", help="Docker image name")
    parser.add_argument(
        "--container_name", default="officebench-subset", help="Docker container base name"
    )
    parser.add_argument("--model_name", default="gpt-4o-2024-05-13", help="Model name")
    parser.add_argument("--tag", default="subset-run", help="Tag for outputs")
    parser.add_argument("--max_iter", type=int, default=20, help="Max iterations per subtask")
    parser.add_argument(
        "--mode",
        default="default",
        choices=["default", "force_new", "use_llm_cache"],
        help="Run mode",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute commands (default is dry-run)",
    )
    args = parser.parse_args()

    subset_path = Path(args.subset_file)
    subset = json.loads(subset_path.read_text(encoding="utf-8"))
    task_ids = subset.get("tasks", [])

    commands = []
    for task_id in task_ids:
        task_dir = Path("tasks") / task_id
        for subtask_id in _list_subtasks(task_dir):
            config_file = task_dir / "subtasks" / f"{subtask_id}.json"
            container_name = f"{args.container_name}-{task_id}-{subtask_id}"
            cmd = [
                sys.executable,
                "agent_interact.py",
                "--docker_name",
                args.docker_name,
                "--container_name",
                container_name,
                "--model_name",
                args.model_name,
                "--task_dir",
                str(task_dir),
                "--config_file",
                str(config_file),
                "--tag",
                args.tag,
                "--max_iter",
                str(args.max_iter),
                "--mode",
                args.mode,
            ]
            commands.append(cmd)

    if not commands:
        print("No commands generated. Check subset.json and task directories.")
        return

    for cmd in commands:
        print(" ".join(cmd))
        if args.execute:
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
