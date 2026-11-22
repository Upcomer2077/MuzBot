def time_to_seconds(t_str: str) -> int:
    parts = list(map(int, t_str.split(":")))[::-1]
    multipliers = [1, 60, 3600]
    return sum(p * m for p, m in zip(parts, multipliers))
