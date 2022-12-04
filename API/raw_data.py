# Copyright (C) 2021 Humanitarian OpenStreetmap Team

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Humanitarian OpenStreetmap Team
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>

"""[Router Responsible for Raw data API ]
"""
import os
import shutil
import time

import requests
from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from fastapi_versioning import version

from src.app import RawData
from src.config import export_rate_limit, limiter
from src.config import logger as logging
from src.validation.models import (
    RawDataCurrentParams,
    SnapshotParamsPlain,
    SnapshotResponse,
    StatusResponse,
)

from .api_worker import process_raw_data

router = APIRouter(prefix="")


@router.get("/status/", response_model=StatusResponse)
@version(1)
def check_database_last_updated():
    """Gives status about how recent the osm data is , it will give the last time that database was updated completely"""
    result = RawData().check_status()
    return {"last_updated": result}


def remove_file(path: str) -> None:
    """Used for removing temp file dir and its all content after zip file is delivered to user"""
    try:
        shutil.rmtree(path)
    except OSError as ex:
        logging.error("Error: %s - %s.", ex.filename, ex.strerror)


def watch_s3_upload(url: str, path: str) -> None:
    """Watches upload of s3 either it is completed or not and removes the temp file after completion

    Args:
        url (_type_): url generated by the script where data will be available
        path (_type_): path where temp file is located at
    """
    start_time = time.time()
    remove_temp_file = True
    check_call = requests.head(url).status_code
    if check_call != 200:
        logging.debug("Upload is not done yet waiting ...")
        while check_call != 200:  # check until status is not green
            check_call = requests.head(url).status_code
            if time.time() - start_time > 300:
                logging.error(
                    "Upload time took more than 5 min , Killing watch : %s , URL : %s",
                    path,
                    url,
                )
                remove_temp_file = False  # don't remove the file if upload fails
                break
            time.sleep(3)  # check each 3 second
    # once it is verfied file is uploaded finally remove the file
    if remove_temp_file:
        logging.debug("File is uploaded at %s , flushing out from %s", url, path)
        os.unlink(path)


@router.post("/snapshot/", response_model=SnapshotResponse)
@limiter.limit(f"{export_rate_limit}/minute")
@version(1)
def get_osm_current_snapshot_as_file(
    request: Request,
    params: RawDataCurrentParams = Body(
        default={},
        examples={
            "normal": {
                "summary": "Example : Extract Evertyhing in the area",
                "description": "**Query** to Extract everything in the area , You can pass your geometry only and you will get everything on that area",
                "value": {
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
            },
            "fileformats": {
                "summary": "An example with different file formats and filename",
                "description": "Export tool api can export data into multiple file formats . See outputype for more details",
                "value": {
                    "outputType": "shp",
                    "fileName": "Pokhara_all_features",
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
                    },
                },
            },
            "filters": {
                "summary": "An example with filters and geometry type",
                "description": "Export tool api supports different kind of filters on both attributes and tags . See filters for more details",
                "value": {
                    "outputType": "geojson",
                    "fileName": "Pokhara_buildings",
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
                    },
                    "filters": {
                        "tags": {"all_geometry": {"building": []}},
                        "attributes": {"all_geometry": ["name"]},
                    },
                    "geometryType": ["point", "polygon"],
                },
            },
            "filters2": {
                "summary": "An example with more filters",
                "description": "Export tool api supports different kind of filters on both attributes and tags . See filters for more details",
                "value": {
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
                    "fileName": "my export",
                    "outputType": "geojson",
                    "geometryType": ["point", "polygon"],
                    "filters": {
                        "tags": {
                            "all_geometry": {
                                "building": [],
                                "amenity": ["cafe", "restaurant", "pub"],
                            }
                        },
                        "attributes": {"all_geometry": ["name", "addr"]},
                    },
                    "joinFilterType": "OR",
                },
            },
            "allfilters": {
                "summary": "An example with multiple level of filters",
                "description": "Export tool api supports multiple level of filters on point line polygon . See filters for more details",
                "value": {
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
            },
        },
    ),
):
    """Generates the current raw OpenStreetMap data available on database based on the input geometry, query and spatial features.

    Steps to Run Snapshot :

    1.  Post the your request here and your request will be on queue, endpoint will return as following :
        {
            "task_id": "your task_id",
            "track_link": "/tasks/task_id/"
        }
    2. Now navigate to /tasks/ with your task id to track progress and result

    """
    task = process_raw_data.delay(params)
    return JSONResponse({"task_id": task.id, "track_link": f"/tasks/status/{task.id}/"})


@router.post("/snapshot/plain/")
@version(1)
def get_current_snapshot_as_plain_geojson(
    request: Request,
    params: SnapshotParamsPlain = Body(
        default={},
        examples={
            "normal": {
                "summary": "Example : Normal Extract",
                "description": "**Query** to extract administrative boundary of nepal in plain geojson format",
                "value": {
                    "select": ["name"],
                    "where": [
                        {"key": "admin_level", "value": ["2"]},
                        {"key": "boundary", "value": ["administrative"]},
                        {"key": "name:en", "value": ["Nepal"]},
                    ],
                    "joinBy": "AND",
                    "lookIn": ["relations"],
                },
            }
        },
    ),
):
    """Simple API to get osm features as geojson for small region. This is designed only for querying small data for large data follow /snapshot/

    Params ::

        bbox: Optional List = takes xmin, ymin, xmax, ymax uses srid=4326
        select: List = this is select query  you can pass [*] to select all attribute
        where: List[WhereCondition] = [{'key': 'building', 'value': ['*']},{'key':'amenity','value':['school','college']}]
        join_by: Optional[JoinFilterType] = or/ and
        look_in: Optional[List[OsmFeatureType]] = ["nodes", "ways_poly","ways_line","relations"] : tables name


    """
    result = RawData(params).extract_plain_geojson()
    return result
