from fastapi.testclient import TestClient
import time
from API.main import app

client = TestClient(app)


def test_status():
    response = client.get("/latest/status/")
    assert response.status_code == 200


def test_snapshot():
    response = client.post(
        "/latest/snapshot/",
        json={
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [83.96919250488281, 28.194446860487773],
                        [83.99751663208006, 28.194446860487773],
                        [83.99751663208006, 28.214869548073377],
                        [83.96919250488281, 28.214869548073377],
                        [83.96919250488281, 28.194446860487773],
                    ]
                ],
            }
        },
    )
    assert response.status_code == 200
    res = response.json()
    track_link = res["track_link"]
    time.sleep(6)  # wait for worker to complete task
    response = client.get(f"/latest{track_link}")
    assert response.status_code == 200
    res = response.json()
    check_status = res["status"]
    assert check_status == "SUCCESS"


def test_snapshot_filters():
    response = client.post(
        "/latest/snapshot/",
        json={
            "fileName": "Example export with all features",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [83.585701, 28.046607],
                        [83.585701, 28.382561],
                        [84.391823, 28.382561],
                        [84.391823, 28.046607],
                        [83.585701, 28.046607],
                    ]
                ],
            },
            "outputType": "geojson",
            "geometryType": ["point", "line", "polygon"],
            "filters": {
                "tags": {
                    "point": {
                        "amenity": [
                            "bank",
                            "ferry_terminal",
                            "bus_station",
                            "fuel",
                            "kindergarten",
                            "school",
                            "college",
                            "university",
                            "place_of_worship",
                            "marketplace",
                            "clinic",
                            "hospital",
                            "police",
                            "fire_station",
                        ],
                        "building": [
                            "bank",
                            "aerodrome",
                            "ferry_terminal",
                            "train_station",
                            "bus_station",
                            "pumping_station",
                            "power_substation",
                            "kindergarten",
                            "school",
                            "college",
                            "university",
                            "mosque ",
                            " church ",
                            " temple",
                            "supermarket",
                            "marketplace",
                            "clinic",
                            "hospital",
                            "police",
                            "fire_station",
                            "stadium ",
                            " sports_centre",
                            "governor_office ",
                            " townhall ",
                            " subdistrict_office ",
                            " village_office ",
                            " community_group_office",
                            "government_office",
                        ],
                        "man_made": ["tower", "water_tower", "pumping_station"],
                        "tower:type": ["communication"],
                        "aeroway": ["aerodrome"],
                        "railway": ["station"],
                        "emergency": ["fire_hydrant"],
                        "landuse": ["reservoir", "recreation_gound"],
                        "waterway": ["floodgate"],
                        "natural": ["spring"],
                        "power": ["tower", "substation"],
                        "shop": ["supermarket"],
                        "leisure": [
                            "stadium ",
                            " sports_centre ",
                            " pitch ",
                            " swimming_pool",
                            "park",
                        ],
                        "office": ["government"],
                    },
                    "line": {
                        "highway": [
                            "motorway ",
                            " trunk ",
                            " primary ",
                            " secondary ",
                            " tertiary ",
                            " service ",
                            " residential ",
                            " pedestrian ",
                            " path ",
                            " living_street ",
                            " track",
                        ],
                        "railway": ["rail"],
                        "man_made": ["embankment"],
                        "waterway": [],
                    },
                    "polygon": {
                        "amenity": [
                            "bank",
                            "ferry_terminal",
                            "bus_station",
                            "fuel",
                            "kindergarten",
                            "school",
                            "college",
                            "university",
                            "place_of_worship",
                            "marketplace",
                            "clinic",
                            "hospital",
                            "police",
                            "fire_station",
                        ],
                        "building": [
                            "bank",
                            "aerodrome",
                            "ferry_terminal",
                            "train_station",
                            "bus_station",
                            "pumping_station",
                            "power_substation",
                            "power_plant",
                            "kindergarten",
                            "school",
                            "college",
                            "university",
                            "mosque ",
                            " church ",
                            " temple",
                            "supermarket",
                            "marketplace",
                            "clinic",
                            "hospital",
                            "police",
                            "fire_station",
                            "stadium ",
                            " sports_centre",
                            "governor_office ",
                            " townhall ",
                            " subdistrict_office ",
                            " village_office ",
                            " community_group_office",
                            "government_office",
                        ],
                        "man_made": ["tower", "water_tower", "pumping_station"],
                        "tower:type": ["communication"],
                        "aeroway": ["aerodrome"],
                        "railway": ["station"],
                        "landuse": ["reservoir", "recreation_gound"],
                        "waterway": [],
                        "natural": ["spring"],
                        "power": ["substation", "plant"],
                        "shop": ["supermarket"],
                        "leisure": [
                            "stadium ",
                            " sports_centre ",
                            " pitch ",
                            " swimming_pool",
                            "park",
                        ],
                        "office": ["government"],
                        "type": ["boundary"],
                        "boundary": ["administrative"],
                    },
                },
                "attributes": {
                    "point": [
                        "building",
                        "ground_floor:height",
                        "capacity:persons",
                        "building:structure",
                        "building:condition",
                        "name",
                        "admin_level",
                        "building:material",
                        "office",
                        "building:roof",
                        "backup_generator",
                        "access:roof",
                        "building:levels",
                        "building:floor",
                        "addr:full",
                        "addr:city",
                        "source",
                    ],
                    "line": ["width", "source", "waterway", "name"],
                    "polygon": [
                        "landslide_prone",
                        "name",
                        "admin_level",
                        "type",
                        "is_in:town",
                        "flood_prone",
                        "is_in:province",
                        "is_in:city",
                        "is_in:municipality",
                        "is_in:RW",
                        "is_in:village",
                        "source",
                        "boundary",
                    ],
                },
            },
        },
    )
    assert response.status_code == 200
    res = response.json()
    track_link = res["track_link"]
    time.sleep(6)  # wait for worker to complete task
    response = client.get(f"/latest{track_link}")
    assert response.status_code == 200
    res = response.json()
    check_status = res["status"]
    assert check_status == "SUCCESS"


def test_snapshot_plain():
    response = client.post(
        "/latest/snapshot/plain/",
        json={
            "select": ["name"],
            "where": [
                {"key": "admin_level", "value": ["7"]},
                {"key": "boundary", "value": ["administrative"]},
                {"key": "name", "value": ["Pokhara"]},
            ],
            "joinBy": "AND",
            "lookIn": ["relations"],
        },
    )
    assert response.status_code == 200
