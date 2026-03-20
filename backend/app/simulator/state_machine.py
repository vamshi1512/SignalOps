from __future__ import annotations

from math import atan2, degrees, hypot


def coverage_route(boundary: list[dict[str, float]], charging_station: dict[str, float], lane_spacing: float = 16.0) -> list[dict[str, float]]:
    xs = [point["x"] for point in boundary]
    ys = [point["y"] for point in boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    route = [{"x": charging_station["x"], "y": charging_station["y"]}]
    x = min_x + 8
    flip = False
    while x <= max_x - 8:
        if flip:
            route.append({"x": x, "y": max_y - 8})
            route.append({"x": x, "y": min_y + 8})
        else:
            route.append({"x": x, "y": min_y + 8})
            route.append({"x": x, "y": max_y - 8})
        flip = not flip
        x += lane_spacing
    route.append({"x": charging_station["x"], "y": charging_station["y"]})
    return route


def route_length(route: list[dict[str, float]]) -> float:
    return sum(distance(route[index - 1], route[index]) for index in range(1, len(route)))


def distance(a: dict[str, float], b: dict[str, float]) -> float:
    return hypot(b["x"] - a["x"], b["y"] - a["y"])


def point_on_route(route: list[dict[str, float]], progress_pct: float) -> tuple[dict[str, float], float]:
    if not route:
        return {"x": 0.0, "y": 0.0}, 0.0
    if len(route) == 1:
        return route[0], 0.0

    total = route_length(route)
    if total == 0:
        return route[0], 0.0

    target = max(0.0, min(100.0, progress_pct)) / 100.0 * total
    traversed = 0.0
    for index in range(1, len(route)):
        start = route[index - 1]
        end = route[index]
        segment = distance(start, end)
        if traversed + segment >= target:
            ratio = 0.0 if segment == 0 else (target - traversed) / segment
            point = {
                "x": start["x"] + (end["x"] - start["x"]) * ratio,
                "y": start["y"] + (end["y"] - start["y"]) * ratio,
            }
            heading = degrees(atan2(end["y"] - start["y"], end["x"] - start["x"]))
            return point, heading
        traversed += segment
    final_heading = degrees(atan2(route[-1]["y"] - route[-2]["y"], route[-1]["x"] - route[-2]["x"]))
    return route[-1], final_heading


def advance_progress(progress_pct: float, speed_mps: float, tick_seconds: float, total_distance: float) -> float:
    if total_distance <= 0:
        return progress_pct
    return min(100.0, progress_pct + ((speed_mps * tick_seconds) / total_distance) * 100.0)


def approach(current: dict[str, float], destination: dict[str, float], step_distance: float) -> tuple[dict[str, float], float]:
    remaining = distance(current, destination)
    if remaining <= step_distance:
        heading = degrees(atan2(destination["y"] - current["y"], destination["x"] - current["x"])) if remaining else 0.0
        return {"x": destination["x"], "y": destination["y"]}, heading
    ratio = step_distance / remaining if remaining else 0.0
    point = {
        "x": current["x"] + (destination["x"] - current["x"]) * ratio,
        "y": current["y"] + (destination["y"] - current["y"]) * ratio,
    }
    heading = degrees(atan2(destination["y"] - current["y"], destination["x"] - current["x"]))
    return point, heading


def should_emit(seed: int, tick: int, every: int, offset: int = 0) -> bool:
    return (tick + seed + offset) % every == 0
