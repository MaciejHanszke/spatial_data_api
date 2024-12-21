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
        }
        ]
    }
}

test_cu_no_date = copy.deepcopy(test_cu)
del test_cu_no_date['date_range']
test_cu_no_date_expected = ("missing", ('date_range',), 'Field required')

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
