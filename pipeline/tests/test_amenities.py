import networkx as nx

from .. import amenities, config


def make_amenities_fc():
    return {
        "type": "FeatureCollection",
        "features": [
            {"properties": {"amenity_type": "school", "name": "Near School"}, "geometry": {"coordinates": [101.7000, 2.8440]}},
            {"properties": {"amenity_type": "school", "name": "Far School"}, "geometry": {"coordinates": [101.7100, 2.8500]}},
            {"properties": {"amenity_type": "park", "name": "The Park"}, "geometry": {"coordinates": [101.7005, 2.8445]}},
        ],
    }


def make_walk_graph(connected: bool = True):
    """A tiny synthetic graph in osmnx's node-attribute shape (x=lon, y=lat)."""
    g = nx.MultiDiGraph(crs="epsg:4326")
    g.add_node(1, x=101.7000, y=2.8443)
    g.add_node(2, x=101.7005, y=2.8445)
    g.add_edge(1, 2, length=80.0)
    if connected:
        g.add_node(3, x=101.7000, y=2.8440)
        g.add_edge(1, 3, length=40.0)
    else:
        g.add_node(3, x=101.7000, y=2.8440)  # isolated, no edge back to 1
    return g


def test_nearest_amenity_picks_closest_of_type():
    fc = make_amenities_fc()
    unit = (101.70285, 2.8443)
    nearest = amenities.nearest_amenity(unit, fc, "school")
    assert nearest["name"] == "Near School"


def test_nearest_amenity_none_for_missing_type():
    fc = make_amenities_fc()
    assert amenities.nearest_amenity((101.70285, 2.8443), fc, "mosque") is None


def test_walk_minutes_uses_shortest_path_length():
    graph = make_walk_graph(connected=True)
    minutes = amenities.walk_minutes((101.7000, 2.8443), (101.7000, 2.8440), graph)
    assert minutes == round(40.0 / config.WALK_SPEED_M_PER_MIN, 1)


def test_walk_minutes_none_when_unreachable():
    graph = make_walk_graph(connected=False)
    minutes = amenities.walk_minutes((101.7000, 2.8443), (101.7000, 2.8440), graph)
    assert minutes is None


def test_unit_amenities_assembles_result_and_skips_missing_types():
    fc = make_amenities_fc()
    graph = make_walk_graph(connected=True)
    result = amenities.unit_amenities((101.7000, 2.8443), fc, graph)
    assert "school" in result
    assert result["school"]["name"] == "Near School"
    assert "park" in result
    # no mosque/clinic/supermarket in the synthetic data -> not present, not crashed
    assert "mosque" not in result
    assert "clinic" not in result
    assert "supermarket" not in result
