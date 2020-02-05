from abc import ABC

from backend.src.main.game.values import DungeonCardValues
from backend.src.main.room.room import AbstractRoomCard
from backend.src.main.room.waypoint_pojo import WaypointPOJO
from backend.src.main.tile.shift_tile import ShiftTile
from backend.src.main.tile.tile import Tile
from backend.src.main.tile.tile_geometry_util import TileGeometryUtility


class TileGeometry(ABC):
    def __init__(self, entrance_tile, exit_tile):
        self.entrance_tile = entrance_tile
        self.exit_tile = exit_tile
        self.max_rotations = 6
        self.waypoint_pojo = WaypointPOJO(entrance_tile, exit_tile)

    def overlay_room_a_on_room_b(self, room_a, room_b):
        current_room_b = room_b
        for _ in range(self.max_rotations):
            new_room_b = self.center_room_a_on_room_b_by_waypoint(room_a, current_room_b)
            new_room_b = self.remove_entrance(new_room_b)
            if not self.do_rooms_overlap(room_a, new_room_b):
                return new_room_b
            current_room_b = current_room_b.rotate()
        raise AssertionError("TileGeometry algorithm failed")

    def remove_entrance(self, room):
        return TileGeometryUtility.remove_tile_by_type(room, self.entrance_tile)

    @staticmethod
    def do_rooms_overlap(room_a: AbstractRoomCard, room_b: AbstractRoomCard) -> bool:
        for tile_a in room_a.get_tiles():
            for tile_b in room_b.get_tiles():
                if tile_a.has_same_coordinates(tile_b):
                    return True
        return False

    def center_room_a_on_room_b_by_waypoint(self, room_a, room_b):
        intermediate_room_b = self.center_on_entrance(room_b)
        room_a_exit = self.waypoint_pojo.get_exit(room_a)
        new_room_b = ShiftTile.shift_room_on_tile(intermediate_room_b, room_a_exit)
        return new_room_b

    def center_on_entrance(self, room):
        return self.center_room_on_tile_type(room, self.entrance_tile)

    def center_room_on_tile_type(self, room, card_type):
        tile_to_recenter_around = TileGeometryUtility.get_tile_by_type(room, card_type)
        if not tile_to_recenter_around:
            raise ValueError("Room {} does not have tile with type {}".format(room, card_type))
        return self.center_room_on_tile(room, tile_to_recenter_around)

    def center_room_on_tile(self, room, tile_to_center_around):
        room_tiles = room.get_tiles()
        new_tiles = self.recenter_tile_list(room_tiles, tile_to_center_around)

        new_room = room.clone()
        new_room.set_tiles(new_tiles)

        return new_room

    def recenter_tile_list(self, tile_list, tile_to_recenter_around):
        return [self.recenter_tile(tile, tile_to_recenter_around) for tile in tile_list]

    @staticmethod
    def recenter_tile(tile_to_move, tile_to_center_around):
        new_x = tile_to_move.get_x() - tile_to_center_around.get_x()
        new_y = tile_to_move.get_y() - tile_to_center_around.get_y()
        character_number = tile_to_move.get_character_number()
        return Tile(new_x, new_y, character_number)


class WaypointATileGeometry(TileGeometry):
    def __init__(self):
        super(WaypointATileGeometry, self).__init__(
            DungeonCardValues.ENTRANCE_A,
            DungeonCardValues.EXIT_A
        )


class WaypointBTileGeometry(TileGeometry):
    def __init__(self):
        super(WaypointBTileGeometry, self).__init__(
            DungeonCardValues.ENTRANCE_B,
            DungeonCardValues.EXIT_B
        )
