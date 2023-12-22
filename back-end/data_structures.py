import time

EXPIRATION = 24 * 3600

class RecentAlbumInMemoryCache:
    def __init__(self):
        self.data = {}

    def add(self, value):
        """Adds a value to the data structure with the current timestamp."""
        self.data[value] = time.time()

    def exists(self, value):
        """Checks if a value exists and is not older than 24 hours."""
        current_time = time.time()
        if value in self.data:
            if current_time - self.data[value] <= EXPIRATION:
                return True
            else:
                del self.data[value]
        return False