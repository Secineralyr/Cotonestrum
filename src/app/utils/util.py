import flet.canvas as cv


class SizeAwareControl(cv.Canvas):
    def __init__(self, content=None, resize_interval=1000, on_resize=None, **kwargs):
        super().__init__(**kwargs)
        
        self.content = content
        self.resize_interval = resize_interval
        self.resize_callback = on_resize

        self.control_width = 0
        self.control_height = 0

        def resize(e):
            self.control_width = e.width
            self.control_height = e.height
            if self.resize_callback:
                self.resize_callback(e)
        self.on_resize = resize


