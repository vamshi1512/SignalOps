from __future__ import annotations

from app.simulator.state_machine import advance_progress, coverage_route, point_on_route, route_length


def test_coverage_route_and_progress_math():
    boundary = [{"x": 0, "y": 0}, {"x": 120, "y": 0}, {"x": 120, "y": 80}, {"x": 0, "y": 80}]
    charging_station = {"x": 10, "y": 10}
    route = coverage_route(boundary, charging_station, lane_spacing=20)

    assert route[0] == charging_station
    assert route[-1] == charging_station
    assert route_length(route) > 0

    progressed = advance_progress(15.0, 1.6, 1.0, route_length(route))
    assert progressed > 15.0

    point, heading = point_on_route(route, 40.0)
    assert 0 <= point["x"] <= 120
    assert 0 <= point["y"] <= 80
    assert isinstance(heading, float)
