from copy import deepcopy, copy
from pygamelib.gfx import core
import pygamelib.board_items as board_items
import pygamelib.assets.graphics as graphics
import pygamelib.constants as constants
import pygamelib.base as base

# from dataclasses import dataclass

# DEBUG ONLY
from pygamelib import engine

import time
import random
import uuid
import math

__docformat__ = "restructuredtext"


class ParticleSprixel(core.Sprixel):
    def __init__(self, model="", bg_color=None, fg_color=None, is_bg_transparent=None):
        super().__init__(
            model=model,
            bg_color=bg_color,
            fg_color=fg_color,
            is_bg_transparent=is_bg_transparent,
        )


class Particle(base.PglBaseObject):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        sprixel: ParticleSprixel = None,
    ) -> None:
        super().__init__()
        self.__pos_x = self._initial_column = column
        self.__pos_y = self._initial_row = row
        self.velocity = velocity
        # print(f"Particle constructor: self.velocity={self.velocity}")
        if self.velocity is None:
            self.velocity = base.Vector2D(
                random.uniform(-1, 1), 2 * random.uniform(-1, 1)
            )
            if abs(self.velocity.column) < abs(self.velocity.row) * 2:
                self.velocity.column = (
                    self.velocity.column / abs(self.velocity.column)
                ) * (abs(self.velocity.row) * 2)
        self.__velocity_accumulator = base.Vector2D(0.0, 0.0)
        self.acceleration = base.Vector2D(0.0, 0.0)
        self.lifespan = lifespan
        if self.lifespan is None:
            self.lifespan = 20
        self._initial_lifespan = self.lifespan
        self.sprixel = sprixel
        if sprixel is None:
            self.sprixel = core.Sprixel(graphics.GeometricShapes.BULLET)
        self.__last_update = time.time()

    def reset(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
    ):
        self.__pos_x = self._initial_column = column
        self.__pos_y = self._initial_row = row
        if velocity is not None:
            self.velocity = velocity
        # if self.velocity is None:
        #     self.velocity = base.Vector2D(
        #         random.uniform(-1, 1), 2 * random.uniform(-1, 1)
        #     )
        #     if abs(self.velocity.column) < abs(self.velocity.row) * 2:
        #         self.velocity.column = (
        #             self.velocity.column / abs(self.velocity.column)
        #         ) * (abs(self.velocity.row) * 2)
        self.__velocity_accumulator = base.Vector2D(0.0, 0.0)
        self.acceleration = base.Vector2D(0.0, 0.0)
        if lifespan is not None:
            self.reset_lifespan(lifespan)

        # if sprixel is not None:
        #     self.sprixel = sprixel
        self.__last_update = time.time()

    @property
    def x(self):
        return self.__pos_x

    @x.setter
    def x(self, value: int):
        if type(value) is int:
            self.__pos_x = value

    @property
    def column(self):
        return self.__pos_x

    @column.setter
    def column(self, value: int):
        if type(value) is int:
            self.__pos_x = value

    @property
    def y(self):
        return self.__pos_y

    @y.setter
    def y(self, value: int):
        if type(value) is int:
            self.__pos_y = value

    @property
    def row(self):
        return self.__pos_y

    @row.setter
    def row(self, value: int):
        if type(value) is int:
            self.__pos_y = value

    def apply_force(self, force: base.Vector2D):
        if force is not None and isinstance(force, base.Vector2D):
            self.acceleration += force

    def reset_lifespan(self, lifespan):
        self.lifespan = lifespan
        if self.lifespan is None:
            self.lifespan = 20
        self._initial_lifespan = self.lifespan

    def update(self):
        now = time.time()
        self.velocity += self.acceleration
        # print(f"\tParticle.update() NEW velocity={self.velocity}")
        # sign_c = sign_r = 1.0
        # if self.velocity.row != 0.0 and self.velocity.row != 0:
        #     sign_r = self.velocity.row / abs(self.velocity.row)
        # if self.velocity.column != 0.0 and self.velocity.column != 0:
        #     sign_c = self.velocity.column / abs(self.velocity.column)
        # if abs(self.velocity.row) >= 1.0:
        #     self.velocity.row -= sign_r * 1.0
        #     self.row += sign_r * 1.0
        # else:
        #     self.row += round(self.velocity.row)
        # if abs(self.velocity.column) >= 1.0:
        #     self.velocity.column -= sign_c * 1.0
        #     self.column += sign_c * 1.0
        # else:
        #     self.column += round(self.velocity.column)

        # self.row += round(self.velocity.row)
        # self.column += round(self.velocity.column)

        self.__velocity_accumulator += self.velocity
        # self.__velocity_accumulator.row += self.velocity.row * (
        #     now - self.__last_update
        # )
        # self.__velocity_accumulator.column += self.velocity.column * (
        #     now - self.__last_update
        # )

        # V1
        # self.row = int(self._initial_row + self.velocity.row)
        # self.column = int(self._initial_column + self.velocity.column)

        # V2
        self.row = int(self._initial_row + self.__velocity_accumulator.row)
        self.column = int(self._initial_column + self.__velocity_accumulator.column)

        #     print(f"\tivr: {self.velocity.row} - {int(self.velocity.row)} = {ivr}")
        #     print(
        #         f"\tivc: {self.velocity.column} - {int(self.velocity.column)} = {ivc}"
        #     )
        # print(f"\tParticle.update() NEW position={self.row}x{self.column}\n")
        self.acceleration *= 0
        self.lifespan -= 1
        self.__last_update = now

    def render(self, sprixel: core.Sprixel = None):
        # If you override this method, it's your responsibility to return a copy of
        # yourself (or just use super().render(sprixel) as it already returns a copy).
        if isinstance(sprixel, ParticleSprixel):
            sprixel.model = self.sprixel.model
            return sprixel
        elif isinstance(sprixel, core.Sprixel):
            # This sprixel might be modified later in the rendering cycle so we want to
            # make sure that the next particle will only overide the rendered sprixel,
            # not our live one. While preserving the
            # NOTE: on the other hand, the model is overwritten at each update... I need
            # to test to see if I could save the copy...
            # # TODO: DEV
            # return None
            # ret = deepcopy(self.sprixel)
            ret = copy(self.sprixel)
            ret.bg_color = sprixel.bg_color
            return ret
        else:
            # This sprixel might be modified later in the rendering cycle so we want to
            # make sure that the next particle will only overide the rendered sprixel,
            # not our live one.
            # NOTE: on the other hand, the model is overwritten at each update... I need
            # to test to see if I could save the copy...
            # return deepcopy(self.sprixel)
            return copy(self.sprixel)

    def finished(self):
        return self.lifespan <= 0

    def terminate(self):
        self.lifespan = -1


class PartitionParticle(Particle):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        partition: list = None,
        partition_blending_table: list = None,
        sprixel: ParticleSprixel = None,
    ) -> None:
        super().__init__(
            row=row,
            column=column,
            velocity=velocity,
            lifespan=lifespan,
            sprixel=sprixel,
        )
        self.partition = partition
        self.partition_blending_table = partition_blending_table
        self._spx_row = 0
        self._spx_column = 0
        if partition is None and sprixel is None:
            self.partition = [
                [
                    graphics.Blocks.QUADRANT_UPPER_LEFT,
                    graphics.Blocks.QUADRANT_UPPER_RIGHT,
                ],
                [
                    graphics.Blocks.QUADRANT_LOWER_LEFT,
                    graphics.Blocks.QUADRANT_LOWER_RIGHT,
                ],
            ]
            self.sprixel = ParticleSprixel(self.partition[0][0])

            if partition_blending_table is None:
                gb = graphics.Blocks
                # I don't think anyone is going to willingly go through that...
                # So first I coded a way to dynamically recognize the addition to do,
                # but crappy performances got me to build a "cached version".
                self.partition_blending_table = {
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT: gb.UPPER_HALF_BLOCK,
                    gb.QUADRANT_UPPER_LEFT + gb.QUADRANT_LOWER_LEFT: gb.LEFT_HALF_BLOCK,
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,
                    gb.QUADRANT_UPPER_LEFT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT + gb.LEFT_HALF_BLOCK: gb.LEFT_HALF_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.UPPER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT + gb.QUADRANT_UPPER_LEFT: gb.LEFT_HALF_BLOCK,
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK + gb.QUADRANT_UPPER_LEFT: gb.LEFT_HALF_BLOCK,
                    #
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.RIGHT_HALF_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.UPPER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT + gb.QUADRANT_UPPER_LEFT: gb.LEFT_HALF_BLOCK,
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.LOWER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT + gb.RIGHT_HALF_BLOCK: gb.RIGHT_HALF_BLOCK,
                    gb.RIGHT_HALF_BLOCK + gb.QUADRANT_UPPER_RIGHT: gb.RIGHT_HALF_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.LOWER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.RIGHT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_LOWER_RIGHT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.RIGHT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_UPPER_RIGHT: gb.RIGHT_HALF_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.QUADRANT_LOWER_RIGHT: gb.RIGHT_HALF_BLOCK,
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.QUADRANT_LOWER_LEFT: gb.LOWER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT
                    + gb.QUADRANT_LOWER_RIGHT: gb.LOWER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_RIGHT + gb.RIGHT_HALF_BLOCK: gb.RIGHT_HALF_BLOCK,
                    gb.RIGHT_HALF_BLOCK + gb.QUADRANT_LOWER_RIGHT: gb.RIGHT_HALF_BLOCK,
                    gb.QUADRANT_LOWER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_RIGHT + gb.LOWER_HALF_BLOCK: gb.LOWER_HALF_BLOCK,
                    gb.LOWER_HALF_BLOCK + gb.QUADRANT_LOWER_RIGHT: gb.LOWER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_LOWER_LEFT + gb.LEFT_HALF_BLOCK: gb.LEFT_HALF_BLOCK,
                    gb.LEFT_HALF_BLOCK + gb.QUADRANT_LOWER_LEFT: gb.LEFT_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT + gb.LOWER_HALF_BLOCK: gb.LOWER_HALF_BLOCK,
                    gb.LOWER_HALF_BLOCK + gb.QUADRANT_LOWER_LEFT: gb.LOWER_HALF_BLOCK,
                    gb.QUADRANT_LOWER_LEFT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK + gb.LEFT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.LEFT_HALF_BLOCK + gb.RIGHT_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.RIGHT_HALF_BLOCK
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.RIGHT_HALF_BLOCK
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.RIGHT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.LEFT_HALF_BLOCK
                    + gb.LOWER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK
                    + gb.LEFT_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.LOWER_HALF_BLOCK + gb.UPPER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.UPPER_HALF_BLOCK + gb.LOWER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT: gb.FULL_BLOCK,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.UPPER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_LEFT_AND_LOWER_RIGHT
                    + gb.UPPER_HALF_BLOCK: gb.FULL_BLOCK,
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_LEFT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK + gb.QUADRANT_UPPER_RIGHT: gb.UPPER_HALF_BLOCK,
                    gb.QUADRANT_UPPER_RIGHT + gb.UPPER_HALF_BLOCK: gb.UPPER_HALF_BLOCK,
                    gb.UPPER_HALF_BLOCK + gb.QUADRANT_UPPER_LEFT: gb.UPPER_HALF_BLOCK,
                    gb.QUADRANT_UPPER_LEFT + gb.UPPER_HALF_BLOCK: gb.UPPER_HALF_BLOCK,
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.UPPER_HALF_BLOCK
                    + gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                    gb.QUADRANT_UPPER_LEFT_AND_LOWER_RIGHT
                    + gb.UPPER_HALF_BLOCK: gb.QUADRANT_UPPER_LEFT_AND_UPPER_RIGHT_AND_LOWER_RIGHT,  # noqa: E501
                }

    def update(self):
        super().update()
        f_row = self._initial_row + self.velocity.row
        f_column = self._initial_column + self.velocity.column
        if self.partition is not None:
            ivr = f_row - int(f_row)
            ivc = f_column - int(f_column)
            spx_c = 0
            spx_r = 0
            if ivr > 0.5:
                spx_r = 1
            if ivc > 0.5:
                spx_c = 1
            self.sprixel.model = self.partition[spx_r][spx_c]
            self._spx_row = spx_r
            self._spx_column = spx_c

    def render(self, sprixel: core.Sprixel = None):
        # If you override this method, it's your responsibility to return a copy of
        # yourself (or just use super().render(sprixel) as it already returns a copy).
        if isinstance(sprixel, ParticleSprixel):
            if self.sprixel.model + sprixel.model in self.partition_blending_table:
                sprixel.model = self.partition_blending_table[
                    self.sprixel.model + sprixel.model
                ]
                return sprixel
            # If we have no match we don't change the sprixel already rendered.
            # TODO: DEV
            # return None
            return sprixel
        elif isinstance(sprixel, core.Sprixel):
            # This sprixel might be modified later in the rendering cycle so we want to
            # make sure that the next particle will only overide the rendered sprixel,
            # not our live one. While preserving the
            # NOTE: on the other hand, the model is overwritten at each update... I need
            # to test to see if I could save the copy...
            ret = deepcopy(self.sprixel)
            ret.bg_color = sprixel.bg_color
            return ret
        else:
            # This sprixel might be modified later in the rendering cycle so we want to
            # make sure that the next particle will only overide the rendered sprixel,
            # not our live one.
            # NOTE: on the other hand, the model is overwritten at each update... I need
            # to test to see if I could save the copy...
            return deepcopy(self.sprixel)


class RandomColorParticle(Particle):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        sprixel: ParticleSprixel = None,
        color: core.Color = None,
    ) -> None:
        super().__init__(
            row=row,
            column=column,
            velocity=velocity,
            lifespan=lifespan,
            sprixel=sprixel,
        )
        self.partition = None
        if sprixel is None and color is None:
            self.sprixel = ParticleSprixel(
                graphics.GeometricShapes.BULLET,
                fg_color=core.Color(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
            )
        elif sprixel is None and color is not None:
            self.sprixel.fg_color = core.Color(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        else:
            self.sprixel.fg_color = color


class RandomColorPartitionParticle(PartitionParticle):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        partition: list = None,
        partition_blending_table: list = None,
        sprixel: ParticleSprixel = None,
        color: core.Color = None,
    ) -> None:
        super().__init__(
            row=row,
            column=column,
            velocity=velocity,
            lifespan=lifespan,
            partition=partition,
            partition_blending_table=partition_blending_table,
            sprixel=sprixel,
        )
        if sprixel is None and color is None:
            self.sprixel = ParticleSprixel(
                graphics.GeometricShapes.BULLET,
                fg_color=core.Color(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
            )
        elif sprixel is None and color is not None:
            self.sprixel.fg_color = core.Color(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        else:
            self.sprixel.fg_color = color


class ColorParticle(Particle):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        sprixel: ParticleSprixel = None,
        start_color: core.Color = None,
        stop_color: core.Color = None,
    ) -> None:
        super().__init__(
            row=row,
            column=column,
            velocity=velocity,
            lifespan=lifespan,
            sprixel=sprixel,
        )
        self.start_color = start_color
        if self.start_color is None:
            self.start_color = core.Color(255, 0, 0)
        self.stop_color = stop_color
        if self.stop_color is None and self.start_color is None:
            self.stop_color = core.Color(0, 0, 0)
        elif self.stop_color is None and self.start_color is not None:
            self.stop_color = self.start_color
        self.sprixel.fg_color = deepcopy(self.start_color)

    def update(self):
        super().update()
        lp = self.lifespan if self.lifespan >= 0 else 0
        self.sprixel.fg_color = self.start_color.blend(
            self.stop_color, 1 - (lp / self._initial_lifespan)
        )


class ColorPartitionParticle(PartitionParticle):
    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        velocity: base.Vector2D = None,
        lifespan: int = None,
        partition: list = None,
        partition_blending_table: list = None,
        sprixel: ParticleSprixel = None,
        start_color: core.Color = None,
        stop_color: core.Color = None,
    ) -> None:
        super().__init__(
            row=row,
            column=column,
            velocity=velocity,
            lifespan=lifespan,
            partition=partition,
            partition_blending_table=partition_blending_table,
            sprixel=sprixel,
        )
        self.start_color = start_color
        if self.start_color is None:
            self.start_color = core.Color(255, 0, 0)
        self.stop_color = stop_color
        if self.stop_color is None and self.start_color is None:
            self.stop_color = core.Color(0, 0, 0)
        elif self.stop_color is None and self.start_color is not None:
            self.stop_color = self.start_color
        self.sprixel.fg_color = deepcopy(self.start_color)

    def update(self):
        super().update()
        lp = self.lifespan if self.lifespan >= 0 else 0
        self.sprixel.fg_color = self.start_color.blend(
            self.stop_color, 1 - (lp / self._initial_lifespan)
        )


# Emitters


# Ideally that would be a @dataclass, but support for KW_ONLY is restricted to
# Python 3.10+. Too bad.
class EmitterProperties:
    """
    EmitterProperties is a class that hold configuration variables for a particle
    emitter. The idea is that it's easier to carry around for multiple emitters with the
    same configuration than multiple values in the emitter's constructor.

    It holds all possible parmeters for all types of emitters. Emitters uses only the
    ones that they really need.

    .. Important:: In most cases these values are copied by the emitter's constructor.
       So changing the values during an emitter's alive cycle is not going to do
       anything.

    .. Note:: This class should be a @dataclass. However, support for keyword only
       data classes is specific to python 3.10+. So for now, it is a regular class.
    """

    def __init__(
        self,
        row: int = 0,
        column: int = 0,
        variance: float = 2.0,
        emit_number: int = 1,
        emit_rate: float = 0.1,
        lifespan=200,
        parent: board_items.BoardItem = None,
        particle_velocity=None,
        particle_acceleration=None,
        particle_lifespan=5.0,
        radius=1.0,
        particle: Particle = Particle,
    ) -> None:
        """

        :param row: The row where the emitter is. It is only important for the first
           rendering cycle. After that, the emitter will know its position on screen.
        :type row: int
        :param column: The row where the emitter is. It is only important for the first
           rendering cycle. After that, the emitter will know its position on screen.
        :type column: int
        :param variance: The variance is the amount of randomness that is allowed when
           emitting a particle. The exact use of this parameter is specific to each
           emitter.
        :type variance: float
        :param emit_number: The number of particle emitted at each timer tick.
        :type emit_number: int
        :param emit_rate: The rate of emission in seconds. This value needs to be
           understood as "the emitter will emit **emit_number** particles every
           **emit_rate** seconds".
        :type emit_rate: float
        :param lifespan: The lifespan of the emitter in number of emission cycle. If
           lifespan is set to 1 for example, the emitter will only emit one burst of
           particles.
        :type lifespan: int
        :param parent: A parent board item. If you do that manually, you will probably
           want to set it specifically for each emitter.
        :type parent: :class:`~pygamelib.board_items.BoardItem`
        :param particle_velocity: The initial particle velocity. Please read the
           documentation of each emitter for the specific use of particle velocity.
        :type particle_velocity: :class:`~pygamelib.base.Vector2D`
        :param particle_acceleration: The initial particle acceleration. Please read the
           documentation of each emitter for the specific use of particle acceleration.
        :type particle_acceleration: :class:`~pygamelib.base.Vector2D`
        :param particle_lifespan: The lifespan of the particle in number of cycles.
        :type particle_lifespan: int
        :param radius: For emitter that supports it (like the CircleEmitter), sets the
           radius of emission (which translate into a velocity vector for each particle).
        :type radius: float
        :param particle: The particle that the emitter will emit. This can be a class
           reference or a fully instanciated particle. Emitters will copy it in the
           particle pool.
        :type particle: :class:`Particle`

        Example::

            method()
        """
        self.row = row
        self.column = column
        self.variance = variance
        self.emit_number = emit_number
        self.emit_rate = emit_rate
        self.lifespan = lifespan
        self.parent = parent
        self.particle_velocity = particle_velocity
        self.particle_acceleration = particle_acceleration
        self.particle_lifespan = particle_lifespan
        self.radius = radius
        self.particle = particle


class ParticlePool:
    def __init__(
        self, size: int = None, emitter_properties: EmitterProperties = None
    ) -> None:

        if size is None:
            self.size = (
                emitter_properties.emit_number * emitter_properties.particle_lifespan
            )
        elif type(size) is int:
            self.size = size
        elif type(size) is float:
            self.size = int(size)
        else:
            self.size = 100
        if self.size % emitter_properties.emit_number != 0:
            self.size += emitter_properties.emit_number - (
                self.size % emitter_properties.emit_number
            )
        self.emitter_properties = None
        if isinstance(emitter_properties, EmitterProperties):
            self.emitter_properties = emitter_properties
        else:
            self.emitter_properties = EmitterProperties()
        self.current_idx = 0

        # Init the particle pool. Beware: it's a tuple, therefore it's immutable.
        self.__particle_pool = ()
        # Here we don't care about the particles configuration (position, velocity,
        # variance, etc.) because the emitter will reset it when it actually emit it.
        if callable(self.emitter_properties.particle):
            self.__particle_pool = tuple(
                self.emitter_properties.particle() for _ in range(self.size)
            )
        else:
            self.__particle_pool = tuple(
                deepcopy(self.emitter_properties.particle) for _ in range(self.size)
            )
        # Finally, we make sure that all are terminated.
        for p in self.__particle_pool:
            p.terminate()

    @property
    def pool(self) -> tuple:
        """
        A read-only property that returns the particle pool tuple.
        """
        return self.__particle_pool

    def get_particles(self, amount):
        if amount is None:
            amount = self.emitter_properties.emit_number
        lp = self.size
        # We cannot return more particles than there is in the pool
        if amount > lp:
            amount = lp - 1

        idx = self.current_idx

        # If there's still enough unused particles in the pool we return them.
        if idx + amount < lp:
            self.current_idx += amount
            return self.pool[idx : idx + amount - 1]
        # If not, but there's enough dead particle at the beginning of the pool we
        # return these.
        elif self.pool[amount - 1].finished():
            self.current_idx = amount
            return self.pool[idx : (idx + amount)]
        # Else we return what we have left and reset the index. It is highly probable
        # that we have not enough particle left...
        else:
            self.current_idx = 0
            return self.pool[idx:]

    def count_active_particles(self) -> int:
        """Returns the number of active particle (i.e not finished) in the pool.

        .. Important:: The only way to know the amount of alive particles is to go
           through the entire pool. Be aware of the performance impact on large particle
           pools.

        :returns: the number of active particles.
        :rtype: int

        Example::

            if emitter.particles.count_active_particles() > 0:
                emitter.apply_force(gravity)
        """
        np = 0
        for p in self.__particle_pool:
            if not p.finished():
                np += 1
        return np

    def resize(self, new_size: int):
        if new_size is not None:
            if new_size > self.size:
                new_pool = ()
                tmpl = self.emitter_properties.particle
                if callable(tmpl):
                    new_pool = tuple(tmpl() for _ in range(new_size - self.size))
                else:
                    new_pool = tuple(
                        deepcopy(tmpl) for _ in range(new_size - self.size)
                    )
                for p in new_pool:
                    p.terminate()
                self.__particle_pool = self.__particle_pool + new_pool
            elif new_size < self.size:
                self.__particle_pool = self.__particle_pool[0:new_size]
                if self.current_idx >= new_size - 1:
                    self.current_idx = 0


class ParticleEmitter(base.PglBaseObject):
    def __init__(self, emitter_properties=None) -> None:
        super().__init__()
        if emitter_properties is None:
            emitter_properties = EmitterProperties()
        self.__pos_x = emitter_properties.column
        self.__pos_y = emitter_properties.row
        self.variance = emitter_properties.variance
        self.emit_number = emitter_properties.emit_number
        self.emit_rate = emitter_properties.emit_rate
        self.lifespan = emitter_properties.lifespan
        self.parent = emitter_properties.parent
        self.particle_velocity = emitter_properties.particle_velocity
        self.particle = emitter_properties.particle
        self.particle_lifespan = emitter_properties.particle_lifespan
        self.particle_acceleration = emitter_properties.particle_acceleration

        # if particle is not callable it is an instance of a particle. So we adjust its
        # values.
        if not callable(self.particle):
            if self.particle_velocity is not None:
                self.particle.velocity = self.particle_velocity
            self.particle.lifespan = self.particle_lifespan
            self.particle._initial_lifespan = self.particle_lifespan

        self.__particle_pool = ParticlePool(
            size=self.emit_number * self.particle_lifespan,
            emitter_properties=emitter_properties,
        )

        self.__last_emit = time.time()
        self.__active = True

    @property
    def particle_pool(self):
        # return self.__particles
        return self.__particle_pool

    @property
    def x(self):
        return self.__pos_x

    @x.setter
    def x(self, value: int):
        if type(value) is int:
            self.__pos_x = value

    @property
    def column(self):
        return self.__pos_x

    @column.setter
    def column(self, value: int):
        if type(value) is int:
            self.__pos_x = value

    @property
    def y(self):
        return self.__pos_y

    @y.setter
    def y(self, value: int):
        if type(value) is int:
            self.__pos_y = value

    @property
    def row(self):
        return self.__pos_y

    @row.setter
    def row(self, value: int):
        if type(value) is int:
            self.__pos_y = value

    @property
    def active(self):
        return self.__active

    @active.setter
    def active(self, state: bool):
        if type(state) is bool:
            self.__active = state
        else:
            raise base.PglInvalidTypeException(
                "ParticleEmitter.active = state: state needs to be a boolean not a "
                f"{type(state)}."
            )

    def resize_pool(self, new_size: int = None):
        if new_size is None:
            # If no size is specified we only resize up. Never down.
            new_size = self.emit_number * self.particle_lifespan
            if self.__particle_pool.size < new_size:
                self.__particle_pool.resize(new_size)
        else:
            # if new_size is set, we consider that the programer knows what he is doing
            # and we let him set whatever size he wants.
            self.__particle_pool.resize(new_size)

    def toggle_active(self):
        self.__active = not self.__active

    def emit(self, amount: int = None):
        if (
            self.__active
            and (self.lifespan is not None and self.lifespan > 0)
            and time.time() - self.__last_emit >= self.emit_rate
        ):
            if amount is None:
                amount = self.emit_number
            # Poor attempt at optimization: test outside the loop.
            if callable(self.particle):
                for p in self.__particle_pool.get_particles(amount):
                    p.reset(
                        row=self.row,
                        column=self.column,
                        velocity=self.particle_velocity,
                        lifespan=self.particle_lifespan,
                    )
                    dv = random.uniform(-self.variance, self.variance)
                    p.velocity.row *= dv
                    p.velocity.column *= 2 * dv
            else:
                for p in self.__particle_pool.get_particles(amount):
                    p.reset(
                        row=self.row,
                        column=self.column,
                        velocity=base.Vector2D(
                            random.uniform(-1, 1), random.uniform(-2, 2)
                        ),
                        lifespan=self.particle_lifespan,
                    )
                    p.velocity *= random.uniform(-self.variance, self.variance)

            # dbg_idx = 0
            # if callable(self.particle):
            #     for _ in range(amount):
            #         self.particles.append(
            #             self.particle(
            #                 row=self.row,
            #                 column=self.column,
            #                 velocity=self.particle_velocity,
            #                 lifespan=self.particle_lifespan,
            #             )
            #         )
            #         dv = random.uniform(-self.variance, self.variance)
            #         self.particles[-1].velocity.row *= dv
            #         self.particles[-1].velocity.column *= 2 * dv
            # else:
            #     for _ in range(amount):
            #         p = deepcopy(self.particle)
            #         p.row = p._initial_row = self.row
            #         p.column = p._initial_column = self.column
            #         p.reset_lifespan(self.particle_lifespan)
            #         p.velocity = base.Vector2D(
            #             random.uniform(-1, 1), random.uniform(-2, 2)
            #         )
            #         p.velocity *= random.uniform(-self.variance, self.variance)
            #         self.particles.append(p)
            if self.lifespan is not None:
                self.lifespan -= 1
            self.__last_emit = time.time()

    def apply_force(self, force: base.Vector2D):
        for p in self.particle_pool.pool:
            p.apply_force(force)

    def update(self):
        particles = self.particle_pool
        # for p in particles:
        #     p.apply_force(self.particle_acceleration)
        #     p.update()

        for i in range(particles.size - 1, -1, -1):
            p = particles.pool[i]
            if not p.finished():
                p.apply_force(self.particle_acceleration)
                p.update()
            # if p.finished():
            #     del particles[i]

    def finished(self):
        return self.lifespan <= 0 and self.particle_pool.count_active_particles() == 0

    def render_to_buffer(self, buffer, row, column, buffer_height, buffer_width):
        """Render all the particles of that emitter in the display buffer.

        This method is automatically called by :func:`pygamelib.engine.Screen.render`.

        :param buffer: A screen buffer to render the item into.
        :type buffer: numpy.array
        :param row: The row to render in.
        :type row: int
        :param column: The column to render in.
        :type column: int
        :param height: The total height of the display buffer.
        :type height: int
        :param width: The total width of the display buffer.
        :type width: int

        """
        # In real life the emitter will be associated to a BoardItem most of the time.
        # So, it needs to maintain a coherent screen coordinate.
        self.row = row
        self.column = column
        # g = engine.Game.instance()
        for p in self.particle_pool.pool:
            if (
                not p.finished()
                and p.row < buffer_height
                and p.column < buffer_width
                and p.row >= 0
                and p.column >= 0
            ):
                buffer[p.row][p.column] = p.render(buffer[p.row][p.column])
            else:
                p.terminate()


class CircleEmitter(ParticleEmitter):
    def __init__(
        self,
        emitter_properties: EmitterProperties = None,
    ) -> None:
        if emitter_properties is None:
            emitter_properties = EmitterProperties()
        super().__init__(emitter_properties)
        self.radius = emitter_properties.radius
        self.__last_emit = time.time()
        # self.__active = True

    def emit(self, amount: int = None):
        if (
            self.active
            and (self.lifespan is not None and self.lifespan > 0)
            and time.time() - self.__last_emit >= self.emit_rate
        ):
            if amount is None:
                amount = self.emit_number
            # Poor attempt at optimization: test outside the loop.
            # dbg_idx = 0

            # TODO: Finir la fonction emit (transformer le code pour utiliser le pool)
            if callable(self.particle):
                i = 0
                for p in self.particle_pool.get_particles(amount):
                    theta = 2.0 * 3.1415926 * i / amount
                    x = self.x + self.radius * 2 * math.cos(theta)
                    y = self.y + self.radius * math.sin(theta)
                    p.reset(
                        row=y,
                        column=x,
                        velocity=base.Vector2D(y - self.y, x - self.x),
                        lifespan=self.particle_lifespan,
                    )
                    i += 1
            else:
                i = 0
                for p in self.particle_pool.get_particles(amount):
                    # NG
                    theta = 2.0 * math.pi * i / amount
                    # the 2 coefficient is to account for console's characters being
                    # twice higher than larger.
                    x = self.x + self.radius * 2 * math.cos(theta)
                    y = self.y + self.radius * math.sin(theta)
                    p.reset(
                        row=y,
                        column=x,
                        velocity=base.Vector2D(y - self.y, x - self.x),
                        lifespan=self.particle_lifespan,
                    )
                    if self.variance > 0.0:
                        p.velocity *= random.uniform(0.1, self.variance)
                    i += 1

            # if callable(self.particle):
            #     for i in range(amount):
            #         theta = 2.0 * 3.1415926 * i / amount
            #         x = self.x + self.radius * 2 * math.cos(theta)
            #         y = self.y + self.radius * math.sin(theta)
            #         self.particles.append(
            #             self.particle(
            #                 row=y,
            #                 column=x,
            #                 velocity=base.Vector2D(y - self.y, x - self.x),
            #                 lifespan=self.particle_lifespan,
            #             )
            #         )
            # else:
            #     for i in range(amount):
            #         p = deepcopy(self.particle)
            #         theta = 2.0 * math.pi * i / amount
            #         # the 2 coefficient is to account for console's characters being
            #         # twice higher than larger.
            #         x = self.x + self.radius * 2 * math.cos(theta)
            #         y = self.y + self.radius * math.sin(theta)
            #         p.row = p._initial_row = y
            #         p.column = p._initial_column = x
            #         # Set the velocity to get away from the center (Find the vector that
            #         # goes from the center to a point on the circle)
            #         p.velocity = base.Vector2D(y - self.y, x - self.x)
            #         # print(
            #         #     f"\t{dbg_idx} Emitter.emit() particle INITIAL velocity: {p.velocity}"
            #         # )
            #         if self.variance > 0:
            #             p.velocity *= random.uniform(0.1, self.variance)
            #         # print(
            #         #     f"\t{dbg_idx} Emitter.emit() particle VARIATED velocity: {p.velocity}"
            #         # )
            #         self.particles.append(p)
            #         # dbg_idx += 1
            if self.lifespan is not None:
                self.lifespan -= 1
            self.__last_emit = time.time()


# NOTE: OUTDATED DO NOT USE!!!
class BaseParticle(board_items.Movable):
    """
    Particles are not ready. This is only an early early test.
    *you should not use it*. If you do, don't complain. And if you really want to help,
    interact on Github or Discord.
    Thank you ;)
    """

    def __init__(
        self,
        model=None,
        bg_color=None,
        fg_color=None,
        acceleration=None,
        velocity=None,
        lifespan=None,
        directions=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # NOTE: this cannot be done anymore for BoardItems
        # self.size = [1, 1]
        self.name = str(uuid.uuid4())
        self.type = "base_particle"
        self.sprixel = core.Sprixel(graphics.GeometricShapes.BULLET)
        if bg_color is not None and isinstance(bg_color, core.Color):
            self.sprixel.bg_color = bg_color
        if fg_color is not None and isinstance(fg_color, core.Color):
            self.sprixel.fg_color = fg_color
        if model is not None:
            self.sprixel.model = model
        self.directions = [
            base.Vector2D.from_direction(constants.UP, 1),
            base.Vector2D.from_direction(constants.DLUP, 1),
            base.Vector2D.from_direction(constants.DRUP, 1),
        ]
        self.lifespan = 5
        if velocity is not None and isinstance(velocity, base.Vector2D):
            self.velocity = velocity
        else:
            self.velocity = base.Vector2D()
        if acceleration is not None and isinstance(acceleration, base.Vector2D):
            self.acceleration = acceleration
        else:
            self.acceleration = base.Vector2D()
        if lifespan is not None:
            self.lifespan = lifespan
        if directions is not None and type(directions) is list:
            self.directions = directions
        # for item in ["lifespan", "sprixel", "name", "type", "directions"]:
        #     if item in kwargs:
        #         setattr(self, item, kwargs[item])

    def direction(self):
        return random.choice(self.directions)

    def pickable(self):
        """
        A particle is not pickable by default. So that method returns False.
        """
        return False

    def overlappable(self):
        """
        Overlapable always return true. As by definition a particle is overlapable.
        """
        return True
