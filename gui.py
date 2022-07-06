import pygame as pg
import json
import os
import spotify


def font(size):
    return pg.font.SysFont('Bahnschrift', size)


class Button:
    def __init__(self, surface, image, position, surface_position):
        self.surface = surface
        self.image = image
        self.position = position
        self.surface_position = surface_position

        self.active = True

    def render(self):
        self.surface.blit(self.image, self.position)

    def detect_click(self, mouse_position):
        left = self.surface_position[0] + self.position[0]
        top = self.surface_position[1] + self.position[1]
        width = self.image.get_rect()[2]
        height = self.image.get_rect()[3]
        hit_box = pg.Rect(left, top, width, height)

        if hit_box.collidepoint(mouse_position):
            print('hit')


class Toggle:
    def __init__(self, surface, image_inactive, image_active, position, surface_position, command):
        self.surface = surface
        self.image_inactive = image_inactive
        self.image_active = image_active
        self.position = position
        self.surface_position = surface_position

        self.command = command
        self.active = False
        self.current_image = self.image_inactive

    def render(self):
        self.surface.blit(self.current_image, self.position)

    def force_switch(self, active):
        self.active = active

        if active:
            self.current_image = self.image_active
        else:
            self.current_image = self.image_inactive

    def detect_click(self, mouse_position):
        left = self.surface_position[0] + self.position[0]
        top = self.surface_position[1] + self.position[1]
        width = self.current_image.get_rect()[2]
        height = self.current_image.get_rect()[3]
        hit_box = pg.Rect(left, top, width, height)

        if hit_box.collidepoint(mouse_position):
            self.active = not self.active
            if self.current_image == self.image_inactive:
                self.current_image = self.image_active

            else:
                self.current_image = self.image_inactive

            return True
        else:
            return False


class ProgressBar:
    def __init__(self, surface, max_value, current_value, position, width, height, colour_scheme):
        self.surface = surface
        self.current_value = current_value
        self.position = position
        self.width = width
        self.height = height

        if max_value > 0:
            self.max_value = max_value
        else:
            self.max_value = 1

        self.colour_scheme = colour_scheme

    def render(self):
        background_rect = pg.Rect(self.position[0], self.position[1], self.width, self.height)
        pg.draw.rect(self.surface, self.colour_scheme['accent2'], background_rect)

        bar_rect = pg.Rect(self.position[0], self.position[1], self.current_value * (self.width / self.max_value), self.height)
        pg.draw.rect(self.surface, self.colour_scheme['accent1'], bar_rect)


class Screen:
    def __init__(self):
        pg.init()
        pg.font.init()

        self.resolution = (1920, 1080)
        self.main_window = pg.display.set_mode(self.resolution, pg.RESIZABLE)

        self.running = True

        self.images = {}
        self.buttons = {}
        self.progress_bars = {}

        # Connections
        self.spotify = spotify.SpotifyPlayer()

        # Surfaces
        self.surface_locations = {"spotify_surface": (1200, 40), "header_surface": (0, 0), "currently_playing_surface": (1200, 1000)}
        self.spotify_surface = pg.Surface((720, 1040))
        self.header_surface = pg.Surface((1920, 40))
        self.currently_playing_surface = pg.Surface((720, 80))

        # Get colour scheme
        with open('gui_elements/colour_scheme.json', 'r') as file:
            self.colour_scheme = json.load(file)

    def start_stop_spotify(self):
        self.spotify.start_pause()

    def check_spotify_status(self):
        self.spotify.update()
        self.buttons['play_pause_button'].force_switch(self.spotify.current_track_playing_status)
        self.progress_bars['music_progression'].current_value = self.spotify.current_track_progress
        self.progress_bars['music_progression'].max_value = self.spotify.current_track_length

    def load_images(self, directory="./gui_elements/images"):
        for filename in os.listdir(directory):
            self.images[str(filename).replace(".png", "")] = (pg.image.load(f"./gui_elements/images/{filename}"))

    def create_objects(self):
        self.create_buttons()
        self.create_progress_bars()

    def create_buttons(self):
        self.buttons['play_pause_button'] = Toggle(self.currently_playing_surface, self.images['play_button'], self.images['pause_button'],
                                                   (335, 12), self.surface_locations["currently_playing_surface"], "start_stop_spotify")

    def create_progress_bars(self):
        self.progress_bars['music_progression'] = ProgressBar(self.currently_playing_surface, 0, 0, (0, 70), 720, 10, self.colour_scheme)

    def update_currently_playing(self):
        self.currently_playing_surface.fill(self.colour_scheme["text-background-dark2"])

        # Current song
        song = self.spotify.current_track_name
        txt = font(16).render(song, True, self.colour_scheme["text-background-light1"])
        self.currently_playing_surface.blit(txt, (15, 5))

        # Current artists
        artists = self.spotify.current_track_artists

        artist_text = ""
        for i, artist in enumerate(artists):
            if i == 0:
                artist_text = artist
            else:
                artist_text += f", {artist}"

        txt = font(12).render(artist_text, True, self.colour_scheme["text-background-light1"])
        self.currently_playing_surface.blit(txt, (15, 30))

    def update_spotify(self):
        self.spotify_surface.fill(self.colour_scheme["spotify-background"])

        txt = font(60).render('Spotify', True, self.colour_scheme["text-background-light1"])
        self.spotify_surface.blit(txt, (15, 5))

    def update_header(self):
        self.header_surface.fill(self.colour_scheme["text-background-dark1"])

        txt = font(30).render('Project Neo', True, self.colour_scheme["text-background-light1"])
        self.header_surface.blit(txt, (15, 2))

    def update_surfaces(self):
        self.update_header()
        self.update_spotify()
        self.update_currently_playing()

    def render_buttons(self):
        for button_name, button in self.buttons.items():
            button.render()

    def render_progress_bars(self):
        for progress_bar_name, progress_bar in self.progress_bars.items():
            progress_bar.render()

    def main(self):
        self.load_images()
        self.create_objects()

        while self.running:

            # Spotify status
            self.check_spotify_status()

            # Check all events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    for button_name, button in self.buttons.items():
                        if button.detect_click((x, y)):
                            self.__getattribute__(button.command)()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        pg.display.iconify()
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

            # Create main background
            self.main_window.fill(self.colour_scheme["text-background-dark3"])
            self.update_surfaces()

            self.render_buttons()
            self.render_progress_bars()

            # Construct final surface
            self.main_window.blit(self.spotify_surface, self.surface_locations["spotify_surface"])
            self.main_window.blit(self.currently_playing_surface, self.surface_locations["currently_playing_surface"])
            self.main_window.blit(self.header_surface, self.surface_locations["header_surface"])

            pg.display.flip()

        pg.quit()


if __name__ == "__main__":
    screen = Screen()
    screen.main()
    print("Finished")
