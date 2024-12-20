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