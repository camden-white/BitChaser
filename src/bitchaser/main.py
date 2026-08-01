"""Command-line entry point for the BitChaser application."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import sleep

from bitchaser.config import DATE_FORMAT, SNAPSHOT_DATA_DIR
from bitchaser.inference.predict import predict_price

today = datetime.now(UTC)


def thinking(thought: str, speed: float = 0.5) -> None:
    """Placeholder for different steps in BitChaser application"""

    print(thought + "...")
    width = 30

    for i in range(101):
        filled = i * width // 100
        bar = "█" * filled + "░" * (width - filled)
        print(f"\r{bar} {i:3d}%", end="", flush=True)
        sleep(speed / 100)

    sleep(speed / 100)
    print()


def get_date_range(file: Path) -> tuple[datetime, datetime]:
    names = file.stem.split("_")
    first, last = (
        datetime.strptime(names[i], DATE_FORMAT).replace(tzinfo=UTC)
        for i in range(2, 4)
    )
    return first, last + timedelta(days=1, microseconds=-1)


def main() -> None:
    """BitChaser application"""
    snapshot_path = next((f for f in SNAPSHOT_DATA_DIR.iterdir() if f.is_file()), None)
    if snapshot_path is None:
        print("Snapshot not found. Run `make snapshot` first.")
        return
    thinking("Pulling Snapshot")

    start, end = get_date_range(snapshot_path)
    print(
        "Snapshot Range:",
        start.strftime(DATE_FORMAT),
        "through",
        end.strftime(DATE_FORMAT),
    )
    print("Today:", today.strftime(DATE_FORMAT))
    print("Data Span:", (end - start).days + 1, "days")
    print("New Data Avalible:", (today - end).days, "days")
    print("(Update with `make data`)")
    thinking("Fitting model")
    # thinking("Plotting model against data")
    # thinking("Printing model metrics")
    while True:
        date = input("Date: ")
        if not date:
            break
        confidence = float(input("Condidence %: "))
        if not confidence:
            prediction = predict_price(date)
            thinking("Generating prediction")
            print(f"{date} prediction: ${prediction:,.2f}")
        else:
            thinking(f"Generating {confidence:.0f}% confidence interval")
            print(f"{date} {confidence:.0f}% CI: (low, high)")
            print("ERROR: Need to make CI function")


if __name__ == "__main__":
    main()
