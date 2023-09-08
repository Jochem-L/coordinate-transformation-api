import json

from coordinates_transformation_api.models import CrsFeatureCollection
from coordinates_transformation_api.util import init_oas, transform_request_body
from geojson_pydantic import Feature
from geojson_pydantic.geometries import Geometry, GeometryCollection, parse_geometry_obj
from pydantic import ValidationError

from tests.util import not_raises

_, _, _, CRS_LIST = init_oas()


def test_bbox_transformed():
    with open("tests/data/geometry.json") as f:
        data = json.load(f)
        geometry = parse_geometry_obj(data)
        geometry_original = parse_geometry_obj(data)
        transform_request_body(geometry, "EPSG:28992", "EPSG:4326", CRS_LIST)
        assert geometry_original.bbox is not None
        assert geometry.bbox is not None
        assert len(geometry_original.bbox) == len(geometry.bbox)
        assert geometry_original.bbox != geometry.bbox


def test_transform_geometry():
    with open("tests/data/geometry.json") as f:
        data = json.load(f)
        geometry: Geometry = parse_geometry_obj(data)
        geometry_original: Geometry = parse_geometry_obj(data)
        geometry_crs84: Geometry = parse_geometry_obj(data)

        transform_request_body(geometry, "EPSG:28992", "EPSG:4326", CRS_LIST)
        geometry_dict = json.loads(geometry.model_dump_json())
        transform_request_body(geometry_crs84, "EPSG:28992", "OGC:CRS84", CRS_LIST)
        # since axis order is always x,y OGC:CRS84==EPSG:4326 in GeoJSON
        assert geometry == geometry_crs84

        # check if input is actually transformed
        assert geometry != geometry_original
        with not_raises(ValidationError, "could not convert output of transform_request_body to type Geometry: {exc}"):
            parse_geometry_obj(geometry_dict)


def test_transform_feature_geometrycollection():
    with open("tests/data/feature-geometry-collection.json") as f:
        data = json.load(f)

        feature = Feature.model_validate(data)
        feature_original = Feature.model_validate(data)

        transform_request_body(feature, "EPSG:28992", "EPSG:4326", CRS_LIST)
        feature_dict = json.loads(feature.model_dump_json())
        # check if input is actually transformed
        assert feature != feature_original
        with not_raises(ValidationError, "could not convert output of transform_request_body to type Feature: {exc}"):
            Feature(**feature_dict)


def test_transform_feature():
    with open("tests/data/feature.json") as f:
        data = json.load(f)
        feature = Feature(**data)
        feature_original = Feature(**data)
        transform_request_body(feature, "EPSG:28992", "EPSG:4326", CRS_LIST)
        feature_dict = json.loads(feature.model_dump_json())
        # check if input is actually transformed
        assert feature != feature_original
        with not_raises(ValidationError, "could not convert output of transform_request_body to type Feature: {exc}"):
            Feature(**feature_dict)


def test_transform_featurecollection():
    with open("tests/data/polygons.json") as f:
        data = json.load(f)
        fc = CrsFeatureCollection(**data)
        fc_original = CrsFeatureCollection(**data)
        transform_request_body(fc, "EPSG:28992", "EPSG:4326", CRS_LIST)
        fc_dict = json.loads(fc.model_dump_json())
        # check if input is actually transformed
        assert fc != fc_original
        # check if crs is updated in transformed output
        assert fc.crs.properties.name != fc_original.crs.properties.name
        with not_raises(ValidationError, "could not convert output of transform_request_body to type CrsFeatureCollection: {exc}"):
            CrsFeatureCollection(**fc_dict)


def test_transform_featurecollection_geometrycollection():
    with open("tests/data/feature-collection-geometry-collection.json") as f:
        data = json.load(f)
        fc = CrsFeatureCollection(**data)
        fc_original = CrsFeatureCollection(**data)

        transform_request_body(fc, "EPSG:28992", "EPSG:4326", CRS_LIST)

        fc_dict = json.loads(fc.model_dump_json())
        # check if input is actually transformed
        assert fc != fc_original
        with not_raises(ValidationError, "could not convert output of transform_request_body to type CrsFeatureCollection: {exc}"):
            CrsFeatureCollection(**fc_dict)


def test_transform_geometrycollection():
    with open("tests/data/geometry-collection.json") as f:
        data = json.load(f)
        gc = GeometryCollection(**data)
        gc_original = GeometryCollection(**data)
        transform_request_body(gc, "EPSG:28992", "EPSG:4326", CRS_LIST)

        gc_dict = json.loads(gc.model_dump_json())
        # check if input is actually transformed
        assert gc != gc_original
        with not_raises(ValidationError, "could not convert output of transform_request_body to type GeometryCollection: {exc}"):
            GeometryCollection(**gc_dict)
