
COOLDOWN_SECONDS = 60 * 5

def readable(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = (seconds % 3600) % 60

    times = {"hour": h, "minute": m, "second":s}

    return " and ".join([f"{v} {k}{'s'[:v^1]}" for k, v in times.items() if v])
