import time

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
            # Check if the value is older than 24 hours
            if current_time - self.data[value] <= 24 * 3600:
                return True
            else:
                # Remove the value if it's older than 24 hours
                del self.data[value]
        return False

    def clean_up(self):
        """Removes values that are older than 24 hours."""
        current_time = time.time()
        keys_to_remove = [key for key, timestamp in self.data.items() if current_time - timestamp > 24 * 3600]
        for key in keys_to_remove:
            del self.data[key]