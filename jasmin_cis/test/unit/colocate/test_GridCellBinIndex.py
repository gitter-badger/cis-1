import timeit
import unittest
import datetime
import numpy
from data_index import GridCellBinIndex
from hamcrest import *
import data_index
from data_io.hyperpoint import HyperPoint

from jasmin_cis.data_io.gridded_data import GriddedDataList
from jasmin_cis.data_io.ungridded_data import UngriddedDataList
from jasmin_cis.col_implementations import GeneralGriddedColocator, mean, CubeCellConstraint, \
    BinningCubeCellConstraint, moments, make_coord_map, BinnedCubeCellOnlyConstraint
from jasmin_cis.test.util.mock import make_mock_cube, make_dummy_ungridded_data_single_point, \
    make_dummy_ungridded_data_two_points_with_different_values, make_dummy_1d_ungridded_data, \
    make_dummy_1d_ungridded_data_with_invalid_standard_name, make_square_5x3_2d_cube_with_time, \
    make_square_5x3_2d_cube_with_altitude, make_square_5x3_2d_cube_with_pressure, \
    make_square_5x3_2d_cube_with_decreasing_latitude, make_square_5x3_2d_cube, make_regular_2d_ungridded_data, \
    make_square_NxM_2d_cube_with_time

from jasmin_cis.time_util import convert_datetime_to_std_time

class TestGridCellBinIndex(unittest.TestCase):

    def test_GIVEN_single_point_in_cube_WHEN_iterate_THEN_return_point_in_middle(self):

        sample_cube = make_square_5x3_2d_cube_with_time(offset=0, time_offset=0)
        data_point = make_dummy_ungridded_data_single_point(0.5, 0.5, 1.2, time=datetime.datetime(1984, 8, 28, 0, 0))
        coord_map = make_coord_map(sample_cube, data_point)
        coords = sample_cube.coords()
        for (hpi, ci, shi) in coord_map:
            coord = coords[ci]
            if coord.ndim > 1:
                raise NotImplementedError("Co-location of data onto a cube with a coordinate of dimension greater"
                                          " than one is not supported (coordinate %s)", coord.name())
            # Ensure that bounds exist.
            if not coord.has_bounds():
                coord.guess_bounds()

        constraint = BinnedCubeCellOnlyConstraint()
        data_index.create_indexes(constraint, coords, data_point.get_non_masked_points(), coord_map)
        iterator = constraint.get_iterator(False, coord_map, coords, data_point.get_non_masked_points(), None, sample_cube, None)


        final_points_index = [(out_index, hp, points) for out_index, hp, points in iterator]
        assert_that(len(final_points_index), is_(1), "There is one mapping from sample_cube to the final grid")
        assert_that(final_points_index[0][0], is_((2, 1, 1)), "The points should map to index")
        assert_that(final_points_index[0][1], is_(HyperPoint(lat=0, lon=0, t=datetime.datetime(1984, 8, 28))), "The points should map to index")
        assert_that(final_points_index[0][2].latitudes, is_([0.5]), "The points should map to index")
        assert_that(final_points_index[0][2].longitudes, is_([0.5]), "The points should map to index")
        assert_that(final_points_index[0][2].times, is_([convert_datetime_to_std_time(datetime.datetime(1984, 8, 28, 0, 0))]), "The points should map to index")
        assert_that(final_points_index[0][2].vals, is_([1.2]), "The points should map to index")
