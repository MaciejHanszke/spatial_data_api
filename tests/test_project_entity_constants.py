import copy

test_cu = {
        "name": "Test name",
        "description": "Test description",
        "date_range": {"lower": "2020-08-01", "upper": "2021-08-09"},
        "area_of_interest": {
        "type" : "FeatureCollection",
        "features" : [{
            "type" : "Feature",
            "properties" : {
                "capacity" : "10",
                "type" : "U-Rack",
                "mount" : "Surface"
            },
            "geometry" : {
                "type" : "Point",
                "coordinates" : [ -71.073283, 42.417500 ]
            }
        }, {
            "type" : "Feature",
            "properties" : {
                "capacity" : "10",
                "type" : "U-Rack",
                "mount" : "Surface"
            },
            "geometry" : {
                "type" : "Point",
                "coordinates" : [ -70.073283, 40.417500 ]
            }
        }
        ]
    }
}

test_cu_2 = {
    "name": "Test name",
    "description": "Test description",
    "date_range": {"lower": "2020-08-01", "upper": "2021-08-09"},
    "area_of_interest": {
    "type": "Feature",
    "properties": {"name": "test"},
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [
                        -52.8430645648562,
                        -5.63351005831322
                    ],
                    [
                        -52.8289481608136,
                        -5.674529420529012
                    ],
                    [
                        -52.8114438198008,
                        -5.6661010219506664
                    ],
                    [
                        -52.797327415758296,
                        -5.654301057317909
                    ],
                    [
                        -52.788292917171,
                        -5.651491506446291
                    ],
                    [
                        -52.7803877309072,
                        -5.640815088854069
                    ],
                    [
                        -52.7555428597923,
                        -5.641377010471558
                    ],
                    [
                        -52.738603174941204,
                        -5.63800547260297
                    ],
                    [
                        -52.729568676354,
                        -5.631262338119598
                    ],
                    [
                        -52.719404865443295,
                        -5.626204935899693
                    ],
                    [
                        -52.709241054532704,
                        -5.616089999567166
                    ],
                    [
                        -52.6708444355369,
                        -5.569446637469866
                    ],
                    [
                        -52.6787496218007,
                        -5.558206718303779
                    ],
                    [
                        -52.687784120388,
                        -5.534602190108217
                    ],
                    [
                        -52.7098057106944,
                        -5.5390983634896
                    ],
                    [
                        -52.7244867708986,
                        -5.546404572245265
                    ],
                    [
                        -52.7600601090859,
                        -5.5722565836830285
                    ],
                    [
                        -52.7843403240391,
                        -5.584058210883924
                    ],
                    [
                        -52.8074912266689,
                        -5.589115978388449
                    ],
                    [
                        -52.823301599196604,
                        -5.618337778382639
                    ],
                    [
                        -52.8385473155626,
                        -5.620585548523252
                    ],
                    [
                        -52.8430645648562,
                        -5.63351005831322
                    ]
                ]
            ]
        ]
    }
}
}

test_cu_3 = {
    "name": "test123456789",
    "description": "abcde",
    "date_range": {"lower": "2021-08-01", "upper": "2021-08-01"},
    "area_of_interest": {
  "type": "GeometryCollection",
  "geometries": [
    {
      "type": "Point",
      "coordinates": [102.0, 0.5]
    },
    {
      "type": "LineString",
      "coordinates": [
        [102.0, 0.0],
        [103.0, 1.0],
        [104.0, 0.0]
      ]
    },
    {
      "type": "Polygon",
      "coordinates": [
        [
          [102.0, 0.0],
          [103.0, 0.0],
          [103.0, 1.0],
          [102.0, 1.0],
          [102.0, 0.0]
        ]
      ]
    }
  ]
}
}

test_cu_no_date = copy.deepcopy(test_cu)
del test_cu_no_date['date_range']
test_cu_no_date_expected = ("missing", ('date_range',), 'Field required')

test_cu_date_empty_dict = copy.deepcopy(test_cu)
test_cu_date_empty_dict['date_range'] = {}
test_cu_date_empty_dict_expected = ("value_error", (), "Value error, date_range field is an empty dictionary")

test_cu_no_lower = copy.deepcopy(test_cu)
del test_cu_no_lower['date_range']['lower']
test_cu_no_lower_expected = ("value_error", (), "Value error, date_range field has to contain both 'lower' and 'upper' fields")

test_cu_no_upper = copy.deepcopy(test_cu)
del test_cu_no_upper['date_range']['upper']
test_cu_no_upper_expected = ("value_error", (), "Value error, date_range field has to contain both 'lower' and 'upper' fields")

test_cu_invalid_type = copy.deepcopy(test_cu)
test_cu_invalid_type['date_range']['lower'] = 123
test_cu_invalid_type_expected = ("value_error", (), 'Value error, You need to provide string following YYYY-MM-DD format for lower')

test_cu_invalid_value = copy.deepcopy(test_cu)
test_cu_invalid_value['date_range']['upper'] = "XXXX-10-12"
test_cu_invalid_value_expected = ("value_error", (), 'Value error, The field upper does not follow YYYY-MM-DD format')

test_cu_lower_higher_than_upper = copy.deepcopy(test_cu)
test_cu_lower_higher_than_upper['date_range'] = {"lower": "2021-08-01", "upper": "2020-08-09"}
test_cu_lower_higher_than_upper_expected = ("value_error", (), 'Value error, The lower range cannot be equal or higher than upper range!')

test_cu_no_aoi = copy.deepcopy(test_cu)
del test_cu_no_aoi['area_of_interest']
test_cu_no_aoi_expected = ("missing", ('area_of_interest',), 'Field required')

test_cu_invalid_aoi = copy.deepcopy(test_cu)
test_cu_invalid_aoi['area_of_interest'] = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              13.377016,
              52.512418
            ],
            [
              13.378182,
              52.51285
            ],
            [
              13.377016,
              52.512418
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}
test_cu_invalid_aoi_expected = ("value_error", (), 'Value error, area_of_interest has invalid geometry')


test_init_fields_1 = copy.deepcopy(test_cu)
test_init_fields_2 = copy.deepcopy(test_cu)
del test_init_fields_2['description']
test_init_fields_3 = copy.deepcopy(test_init_fields_2)
del test_init_fields_3['date_range']

test_date_range_transform_1 = {"lower": "2020-08-01", "upper": "2021-08-09"}
test_date_range_transform_1_expected = "[2020-08-01,2021-08-09)"
test_date_range_transform_2 = {"lower": "2020-08-01", "upper": "2020-08-01"}
test_date_range_transform_2_expected = "[2020-08-01,2020-08-01]"
