service_healthy_sample_response = {
        200: {
            "description": "App up and running",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "OK"
                    }
                }
            }
        }
    }

create_project_sample_request = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Sample project",
                    "description": "Test description",
                    "date_range": {"lower": "2020-08-01", "upper": "2021-08-09"},
                    "area_of_interest": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [125.6, 10.1]
                        },
                        "properties": {
                            "name": "Dinagat Islands"
                        }
                    }
                }
            ]
        }
    }

create_project_sample_response = {
        200: {
            "description": "Project successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "New project added: f1a46630-4a09-4107-856e-1bbb55465bfe"
                    }
                }
            }
        }
    }

get_project_sample_response = {
        200: {
            "description": "Project successfully fetched",
            "content": {
                "application/json": {
                    "example": {
                        "id": "6a9035a5-9dd1-4642-9284-b182bda60799",
                        "name": "Test name",
                        "description": "Test description",
                        "date_range": {
                            "lower": "2020-08-01",
                            "upper": "2021-08-09",
                            "bounds": "[)",
                            "empty": False
                        },
                        "area_of_interest": {
                            "type": "FeatureCollection",
                            "features": [
                                {
                                    "type": "Feature",
                                    "properties": {
                                        "capacity": "10",
                                        "type": "U-Rack",
                                        "mount": "Surface"
                                    },
                                    "geometry": {
                                        "type": "Point",
                                        "coordinates": [
                                            -71.073283,
                                            42.4175
                                        ]
                                    }
                                }
                            ]
                        },
                        "area_of_interest_geom": [
                            "0101000020e610000094162eabb0c451c03d0ad7a370354540"
                        ]
                    }
                }
            }
        },
        404: {
            "description": "No project existing with that ID",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Project not found"
                    }
                }
            }
        }
    }

delete_project_sample_response = {
        200: {
            "description": "Project successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Project f1a46630-4a09-4107-856e-1bbb55465bfe deleted"
                    }
                }
            }
        },
        404: {
            "description": "No project existing with that ID",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Project not found"
                    }
                }
            }
        }
    }

update_project_sample_request = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "New sample values",
                    "description": "New Test description",
                    "date_range": {"lower": "2022-11-05", "upper": "2024-06-11"},
                    "area_of_interest": {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [0.0, 0.0]
                        },
                        "properties": {
                            "name": "No islands"
                        }
                    }
                }
            ]
        }
    }

update_project_sample_response = {
        200: {
            "description": "Project successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Project f1a46630-4a09-4107-856e-1bbb55465bfe updated"
                    }
                }
            }
        },
        404: {
            "description": "No project existing with that ID",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Project not found"
                    }
                }
            }
        }
    }

list_project_sample_response = {
        200: {
            "description": "All projects successfully fetched",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "3f38b222-53f8-406e-a27c-2882833c6640",
                            "name": "Sample project",
                            "description": "Test description",
                            "date_range": {
                                "lower": "2020-08-01",
                                "upper": "2021-08-09",
                                "bounds": "[)",
                                "empty": False
                            },
                            "area_of_interest": {
                                "geometry": {
                                    "coordinates": [
                                        125.6,
                                        10.1
                                    ],
                                    "type": "Point"
                                },
                                "properties": {
                                    "name": "Dinagat Islands"
                                },
                                "type": "Feature"
                            },
                            "area_of_interest_geom": [
                                "0101000020e61000006666666666665f403333333333332440"
                            ]
                        },
                        {
                            "id": "6a9035a5-9dd1-4642-9284-b182bda60799",
                            "name": "New sample values",
                            "description": "New Test description",
                            "date_range": {
                                "lower": "2022-11-05",
                                "upper": "2024-06-11",
                                "bounds": "[)",
                                "empty": False
                            },
                            "area_of_interest": {
                                "geometry": {
                                    "coordinates": [
                                        0,
                                        0
                                    ],
                                    "type": "Point"
                                },
                                "properties": {
                                    "name": "No islands"
                                },
                                "type": "Feature"
                            },
                            "area_of_interest_geom": [
                                "0101000020e610000000000000000000000000000000000000"
                            ]
                        },
                        {
                            "id": "85433a19-4c4a-4df6-9ac4-a54ad321295e",
                            "name": "Test name",
                            "description": "Test description",
                            "date_range": {
                                "lower": "2020-08-01",
                                "upper": "2021-08-09",
                                "bounds": "[)",
                                "empty": False
                            },
                            "area_of_interest": {
                                "type": "FeatureCollection",
                                "features": [
                                    {
                                        "type": "Feature",
                                        "properties": {
                                            "capacity": "10",
                                            "type": "U-Rack",
                                            "mount": "Surface"
                                        },
                                        "geometry": {
                                            "type": "Point",
                                            "coordinates": [
                                                -71.073283,
                                                42.4175
                                            ]
                                        }
                                    }
                                ]
                            },
                            "area_of_interest_geom": [
                                "0101000020e610000094162eabb0c451c03d0ad7a370354540"
                            ]
                        }
                    ]
                }
            }
        }
    }