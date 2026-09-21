"""A small, well-documented utility module used to demo good readability."""


def celsius_to_fahrenheit(celsius):
    """Convert a Celsius temperature to Fahrenheit."""
    # Standard conversion formula
    return (celsius * 9 / 5) + 32


def average(numbers):
    """Return the arithmetic mean of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


class TemperatureLog:
    """Stores a series of temperature readings and reports basic stats."""

    def __init__(self):
        # readings are stored in Celsius internally
        self.readings = []

    def add_reading(self, celsius):
        """Record a new temperature reading."""
        self.readings.append(celsius)

    def average_fahrenheit(self):
        """Return the average reading converted to Fahrenheit."""
        avg_c = average(self.readings)
        return celsius_to_fahrenheit(avg_c)
