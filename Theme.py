class Theme:
    def __init__(self, light, dark):
        self.light = light
        self.dark = dark


class Formal(Theme):
    def __init__(self):
        super().__init__((235, 236, 208), (115, 149, 82))
        self.selected_light = (245, 246, 129)
        self.selected_dark = (185, 202, 66)
        self.move_light = (237, 126, 106)
        self.move_dark = (212, 108, 81)


class Brown(Theme):
    def __init__(self):
        super().__init__((245, 223, 203), (210, 156, 116))
        self.selected_light = (225, 188, 159)
        self.selected_dark = (193, 128, 84)
        self.move_light = (238, 126, 106)
        self.move_dark = (210, 105, 76)
