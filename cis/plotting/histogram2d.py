from cis.plotting.generic_plot import Generic_Plot


class Histogram_2D(Generic_Plot):
    valid_histogram_styles = ["bar", "step", "stepfilled"]

    def plot(self):
        """
        Plots a 2D histogram
        """
        from numpy.ma import MaskedArray
        vmin = self.mplkwargs.pop("vmin")
        vmax = self.mplkwargs.pop("vmax")

        self.mplkwargs["bins"] = self.calculate_bin_edges()

        for i, unpacked_data_item in enumerate(self.unpacked_data_items):
            datafile = self.plot_args["datagroups"][i]
            if datafile["itemstyle"]:
                if datafile["itemstyle"] in self.valid_histogram_styles:
                    self.mplkwargs["histtype"] = datafile["itemstyle"]
                else:
                    from cis.exceptions import InvalidHistogramStyleError
                    raise InvalidHistogramStyleError(
                        "'" + datafile["itemstyle"] + "' is not a valid histogram style, please use one of: " + str(
                            self.valid_histogram_styles))

            else:
                self.mplkwargs.pop("histtype", None)

            if datafile["color"]:
                self.mplkwargs["color"] = datafile["color"]
            else:
                self.mplkwargs.pop("color", None)

            if isinstance(unpacked_data_item["data"], MaskedArray):
                data = unpacked_data_item["data"].compressed()
            else:
                data = unpacked_data_item["data"].flatten()

            self.matplotlib.hist(data, *self.mplargs, **self.mplkwargs)
        self.mplkwargs["vmin"] = vmin
        self.mplkwargs["vmax"] = vmax

    def unpack_data_items(self):
        return self.unpack_comparative_data()

    def setup_map(self):
        pass

    def is_map(self):
        return False

    def calculate_bin_edges(self):
        """
        Calculates the number of bins for a given axis.
        Uses 10 as the default
        :param axis: The axis to calculate the number of bins for
        :return: The number of bins for the given axis
        """
        from cis.utils import calculate_histogram_bin_edges
        from numpy import array
        min_val = min(unpacked_data_item["data"].min() for unpacked_data_item in self.unpacked_data_items)
        max_val = max(unpacked_data_item["data"].max() for unpacked_data_item in self.unpacked_data_items)
        data = array([min_val, max_val])
        bin_edges = calculate_histogram_bin_edges(data, "x", self.plot_args["xrange"], self.plot_args["xbinwidth"],
                                                  self.plot_args["logx"])

        self.plot_args["xrange"]["xmin"] = bin_edges.min()
        self.plot_args["xrange"]["xmax"] = bin_edges.max()

        return bin_edges

    def format_plot(self):
        # We don't format the time axis here as we're only plotting frequency against data
        self.format_2d_plot()

    def set_default_axis_label(self, axis):
        """
        Sets the default axis label for the given axis.
        If the axis is "y", then labels it "Frequency", else works it out based on the name and units of the data
        :param axis: The axis to calculate the default axis label for
        """
        axis = axis.lower()
        axislabel = axis + "label"

        if self.plot_args[axislabel] is None:
            if axis == "x":
                units = self.packed_data_items[0].units

                if len(self.packed_data_items) == 1:
                    name = self.packed_data_items[0].name()
                    # only 1 data to plot, display
                    self.plot_args[axislabel] = name + " " + self.format_units(units)
                else:
                    # if more than 1 data, legend will tell us what the name is. so just displaying units
                    self.plot_args[axislabel] = self.format_units(units)
            elif axis == "y":
                self.plot_args[axislabel] = "Frequency"

    def calculate_axis_limits(self, axis, min_val, max_val):
        """
        Calculates the limits for a given axis.
        If the axis is "y" then looks at the "data" as this is where the values are stored
        :param axis: The axis to calculate the limits for
        :return: A dictionary containing the min and max values for the given axis
        """
        if axis == "x":
            c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis, self.unpacked_data_items[0]['data'])
        elif axis == "y":
            c_min, c_max = None, None

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        return new_min, new_max

    def set_axis_ticks(self, axis, no_of_dims):

        if axis == "x":
            tick_method = self.matplotlib.xticks
        elif axis == "y":
            tick_method = self.matplotlib.yticks

        if self.plot_args.get(axis + "tickangle", None) is None:
            angle = None
        else:
            angle = self.plot_args[axis + "tickangle"]

        tick_method(rotation=angle)

    def apply_axis_limits(self):
        """
        Applies the limits (if given) to the specified axis.
        Sets the "y" axis as having a minimum value of 0 as can never have a negative frequency
        :param valrange: A dictionary containing the min and/or max values for the axis
        :param axis: The axis to apply the limits to
        """
        # Need to ensure that frequency starts from 0
        if 'yrange' in self.plot_args:
            ymin = self.plot_args['yrange'].get('ymin', 0)
            self.plot_args['yrange']['ymin'] = 0 if ymin < 0 else ymin

        super(Histogram_2D, self).apply_axis_limits()