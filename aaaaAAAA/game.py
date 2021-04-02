from random import choice
from typing import Optional

import arcade
from arcade_curtains import BaseScene, Curtains

from aaaaAAAA import _sprites, constants


class DuckScene(BaseScene):
    """Scene showing Ducks moving down the river to the pondhouse."""

    def __init__(self, debug: Optional[bool] = False):
        self.debug = debug
        super().__init__()

    def setup(self) -> None:
        """Setup the scene assets."""
        self.background = arcade.load_texture("assets/overworld/overworld placeholder.png")
        self.pond = arcade.load_texture("assets/overworld/ponds/png/Blue Pond.png")
        self.pondhouse = _sprites.PondHouse()
        self.pondhouse.position = (constants.SCREEN_WIDTH * .67, constants.SCREEN_HEIGHT * .78)
        self.events.hover(self.pondhouse, self.pondhouse.see_through)
        self.events.out(self.pondhouse, self.pondhouse.opaque)
        self.ducks = arcade.SpriteList()
        self.pondhouse_ducks = arcade.SpriteList()
        self.leader = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.075)
        self.ducks.append(self.leader)
        self.seq = self.leader.path_seq

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Add a ducky to the scene, register some events and start animating."""
        if not constants.POINTS_HINT:
            return
        ducky = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.05)
        self.events.hover(ducky, ducky.expand)
        self.events.out(ducky, ducky.shrink)
        self.ducks.append(ducky)
        seq = ducky.path_seq
        seq.add_callback(seq.total_time, lambda: self.enter_pondhouse(ducky))
        self.animations.fire(ducky, seq)
        if len(self.ducks) >= constants.DUCKS:
            arcade.unschedule(self.add_a_ducky)

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Start adding duckies on entering the scene."""
        if not self.debug:
            self.animations.fire(self.leader, self.seq)
            arcade.schedule(self.add_a_ducky, len(constants.POINTS_HINT)*10/constants.DUCKS)

    def draw(self) -> None:
        """Draw the background environment."""
        if len(self.pondhouse_ducks) > 20:
            self.background = arcade.load_texture("assets/overworld/overworld scorched earth placeholder.png")
            self.pond = arcade.load_texture("assets/overworld/ponds/png/Black Pond.png")
        elif len(self.pondhouse_ducks) > 15:
            self.pond = arcade.load_texture("assets/overworld/ponds/png/Purple Pond.png")
        elif len(self.pondhouse_ducks) > 10:
            self.background = arcade.load_texture("assets/overworld/overworld dirt placeholder.png")
            self.pond = arcade.load_texture("assets/overworld/ponds/png/Yellow Pond.png")
        elif len(self.pondhouse_ducks) > 5:
            self.pond = arcade.load_texture("assets/overworld/ponds/png/Green Pond.png")
        else:
            self.pond = arcade.load_texture("assets/overworld/ponds/png/Blue Pond.png")
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )
        arcade.draw_scaled_texture_rectangle(constants.SCREEN_WIDTH/2,
                                             constants.SCREEN_HEIGHT * .8,
                                             self.pond,
                                             constants.SCREEN_WIDTH/self.pond.image.width)
        super().draw()
        self.pondhouse.draw()

    def enter_pondhouse(self, ducky: _sprites.Ducky) -> None:
        """Duckies that are circling outside the pondhouse waiting to be processed."""
        self.pondhouse_ducks.append(ducky)
        self.animations.fire(ducky, ducky.pondhouse_seq)

    def enter_pond(self, ducky: Optional[_sprites.Ducky] = None) -> None:
        """Grant a ducky entry into the pond."""
        if self.pondhouse_ducks:
            duck = ducky or choice(self.pondhouse_ducks)
            self.pondhouse_ducks.remove(duck)
            self.animations.fire(duck, duck.pond_seq)

    def grant_entry(self) -> None:
        """Generic method to grant entry."""
        self.enter_pond()


class GameView(arcade.View):
    """Main application class."""

    def __init__(self, debug: Optional[bool] = False):
        super().__init__()
        self.debug = debug
        if self.debug:
            constants.POINTS_HINT.clear()
        self.curtains = Curtains(self)
        self.curtains.add_scene('swimming_scene', DuckScene(self.debug))
        self.curtains.set_scene('swimming_scene')
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """
        For use only when debug=True.

        'a' to add a duck
        'p' to print the generated points_hint list
        'x' to clear the points
        'g' grant random duck entry
        """
        if not self.debug:
            return
        if symbol == ord('a'):
            if self.curtains.current_scene == self.curtains.scenes['swimming_scene']:
                self.curtains.current_scene.add_a_ducky()
        elif symbol == ord('p'):
            print(constants.POINTS_HINT)
        elif symbol == ord('x'):
            constants.POINTS_HINT.clear()
        elif symbol == ord('g'):
            if self.curtains.current_scene == self.curtains.scenes['swimming_scene']:
                self.curtains.current_scene.grant_entry()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Add clicked point to points_hint as % of width/height."""
        constants.POINTS_HINT.append((round(x/self.window.width, 3), round(y/self.window.height, 3)))


def main() -> None:
    """
    Main function.

    Can be run for a GameView in debug mode
    """
    window = arcade.Window(title=constants.SCREEN_TITLE, width=constants.SCREEN_WIDTH, height=constants.SCREEN_HEIGHT)
    arcade.set_window(window)
    game = GameView(debug=True)
    window.show_view(game)
    arcade.run()


if __name__ == '__main__':
    main()
