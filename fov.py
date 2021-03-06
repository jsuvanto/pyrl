from generic_algorithms import bresenham


class ShadowCast(object):

    # Multipliers for transforming coordinates to other octants:
    _mult = (
            (1, 0, 0, -1, -1, 0, 0, 1),
            (0, 1, -1, 0, 0, -1, 1, 0),
            (0, 1, 1, 0, 0, -1, -1, 0),
            (1, 0, 0, 1, -1, 0, 0, -1),
    )

    @classmethod
    def get_light_set(self, visibility_func, coord, sight, max_rows, max_cols):
        y, x = coord
        light_set = set()
        light_set.add(coord)
        for octant in range(8):
            self._shadow_cast(light_set, visibility_func, y, x, 1, 1.0, 0.0, sight, max_rows, max_cols,
                    self._mult[0][octant], self._mult[1][octant], self._mult[2][octant], self._mult[3][octant])
        return light_set

    # Based on an algorithm by Bjorn Bergstrom bjorn.bergstrom@roguelikedevelopment.org
    # http://roguebasin.roguelikedevelopment.org/index.php?title=FOV_using_recursive_shadowcasting
    @classmethod
    def _shadow_cast(self, light_set, visibility_func, cy, cx, row, start, end, r, max_rows, max_cols, xx, xy, yx, yy):
        """Recursive lightcasting function."""
        if start < end:
            return
        radius_squared = r * r
        for j in range(row, r + 1):
            dx = -j - 1
            dy = -j
            blocked = False
            while dx <= 0:
                dx += 1
                # Translate the dx, dy coordinates into map coordinates:
                X = cx + dx * xx + dy * xy
                Y = cy + dx * yx + dy * yy

                # Don't try to compute outside of the map
                if 0 <= Y < max_rows and 0 <= X < max_cols:
                    # l_slope and r_slope store the slopes of the left and right
                    # extremities of the square we're considering:
                    l_slope = (dx - 0.5) / (dy + 0.5)
                    r_slope = (dx + 0.5) / (dy - 0.5)

                    if end > l_slope:
                        break
                    if start >= r_slope:
                        # Our light beam is touching this square; light it:
                        if dx * dx + dy * dy <= radius_squared:
                            light_set.add((Y, X))

                        if blocked:
                            # we're scanning a row of blocked squares:
                            if not visibility_func((Y, X)):
                                new_start = r_slope
                            else:
                                blocked = False
                                start = new_start
                        else:
                            if not visibility_func((Y, X)) and j < r:
                                # This is a blocking square, start a child scan:
                                blocked = True
                                self._shadow_cast(light_set, visibility_func, cy, cx, j + 1, start, l_slope, r,
                                            max_rows, max_cols, xx, xy, yx, yy)
                                new_start = r_slope

            # Row is scanned; do next row unless last square was blocked:
            if blocked:
                break


class Bresenham(object):

    _mult = (
            (0, 0, 1, 1, 0, 0, -1, -1),
            (1, 1, 0, 0, -1, -1, 0, 0),
            (-1, -1, -1, 0, 1, 1, 1, 0),
            (-1, 0, 1, 1, 1, 0, -1, -1),
    )

    @classmethod
    def get_light_set(self, visibility_func, start_coord, sight):
        light_set = set()
        sight_squared = sight * sight
        start_y, start_x = start_coord
        for octant in range(8):
            mult_y_i = self._mult[0][octant]
            mult_x_i = self._mult[1][octant]
            mult_y_s = self._mult[2][octant]
            mult_x_s = self._mult[3][octant]
            for i in range(sight):
                for y, x in bresenham(start_coord, (start_y + sight * mult_y_s + i * mult_y_i,
                                                    start_x + sight * mult_x_s + i * mult_x_i)):
                    if sight_squared < ((start_y - y) ** 2 + (start_x - x) ** 2):
                        break
                    if (y, x) not in light_set:
                        light_set.add((y, x))
                    if not visibility_func((y, x)):
                        break
        return light_set
