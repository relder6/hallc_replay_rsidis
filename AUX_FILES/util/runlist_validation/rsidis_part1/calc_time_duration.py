import sys
from datetime import datetime

def calc_time_duration(start_time, stop_time):
    """
    Calculates difference between two times given in format:
    "YYYY-MM-DD HH:MM:SS". NOTE: 1st argument must be an
    earlier time than the 2nd argument.
    """
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    stop = datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S")
    duration_seconds = int((stop - start).total_seconds())
    print(duration_seconds)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} 'YYYY-MM-DD HH:MM:SS' 'YYYY-MM-DD HH:MM:SS'")
        sys.exit(1)

    start_time = sys.argv[1]
    stop_time = sys.argv[2]

    calc_time_duration(start_time, stop_time)
