"""OLED status facade. A verified SSD1306/SH1106 driver can be injected."""
import config

class StatusDisplay:
    def __init__(self, driver=None):
        self.driver = driver
        self.last_refresh = 0
        self.lines = ["READY"]

    def show(self, *lines):
        self.lines = [str(x) for x in lines[:8]]
        try:
            import time
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_refresh) < config.OLED_REFRESH_MS:
                return
            self.last_refresh = now
            if self.driver is not None:
                self.driver.fill(0)
                for i, line in enumerate(self.lines[:4]):
                    self.driver.text(line[:21], 0, i * 16)
                self.driver.show()
        except Exception:
            # Display failure must not prevent motor safety logic.
            pass
