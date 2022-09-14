import json
import logging
import math
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class _SettingsNamespace:
    """A simple namespace for working with a group of key-value settings."""

    def __init__(self, name: str, /, **kwargs):
        # Use `__dict__` directly since `__getattr__` is implemented on this class.
        self.__dict__["name"] = name
        self.__dict__["_settings"]: Dict[str, Any] = {**kwargs}

    def __contains__(self, key: str) -> bool:
        """Return True if the namespace contains an attribute for the provided key."""
        return key in self._settings

    def __getattr__(self, name: str) -> Any:
        """Return the setting value for the provided name."""
        return self._settings[name]

    def __getitem__(self, name: str) -> Any:
        """Return the setting value for the provided name."""
        return self._settings[name]

    def __setattr__(self, name: str, value: Any) -> None:
        """Set the setting value for the provided name."""
        self._settings[name] = value

    def __setitem__(self, name: str, value: Any) -> None:
        """Set the setting value for the provided name."""
        self._settings[name] = value

    def asdict(self) -> Dict[str, Any]:
        """Return the settings in the namespace as a dictionary."""
        return self._settings

    def update(self, dictionary: Dict[str, Any]) -> None:
        """Update the settings namespace with the provided key-value pairs."""
        self._settings.update(dictionary)


class Settings:
    """A centralized store for library settings with file persistence functions."""

    # The file name used to store settings on disk.
    SETTINGS_FILE_NAME = "settings.json"

    def __init__(self, namespaces: List[_SettingsNamespace]) -> None:
        # Directory where the settings file(s) are stored.
        self._directory: str = None

        # A dictionary of setting namespaces keyed by their names.
        self._namespaces: Dict[str, _SettingsNamespace] = {
            namespace.name: namespace for namespace in namespaces
        }

    def __getattr__(self, name: str) -> _SettingsNamespace:
        """Access the namespace with the provided name."""
        return self._namespaces[name]

    @property
    def directory(self) -> str:
        """Return the settings directory path."""
        return self._directory

    @directory.setter
    def directory(self, path: str) -> None:
        """Setup a settings directory at the provided path.

        This method will create the directory if it does not exist.
        """
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

        self._directory = path

        logger.debug("Using '%s' for settings", self._directory)

        self.load()

    @property
    def file_path(self) -> str:
        """Return the settings file path."""
        return os.path.join(self._directory, Settings.SETTINGS_FILE_NAME)

    def load(self) -> None:
        """Load the settings file from the disk and into the instance, if one exists.

        If the directory is not set or the settings file does not exist, this method does not do
        anything.
        """
        if not self._directory:
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for name, dictionary in json.load(file).items():
                    # Ignore keys in the settings file that are not namespaces.
                    if name in self._namespaces:
                        self._namespaces[name].update(dictionary)
        except FileNotFoundError:
            return

    def write(self) -> None:
        """Write the current settings to a file in the settings directory.

        If the settings directory is not set, this function does nothing.
        """
        if not self._directory:
            return

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self._asdict(), indent=4))
        except FileNotFoundError:
            return

    def _asdict(self) -> Dict[str, Any]:
        """Return a dictionary containing the settings from all namespaces keyed by namespace."""
        dictionary = {}

        for name, _settings in self._namespaces.items():
            dictionary[name] = _settings.asdict()

        return dictionary


# Settings instance used by the library at runtime. Initial namespaces are filled with default
# values used if there is no settings file to use.
# If there is a need to add structure to the namespaces, one could inherit from SettingsNamespace
# and define the keys and types explicitly.
settings = Settings(
    [
        _SettingsNamespace(
            "window",
            **{
                # Window width in pixels.
                "width": 1000,
                # Window height in pixels.
                "height": 1000,
            },
        ),
        _SettingsNamespace(
            "camera",
            **{
                "orbit_speed": 2.0,
                "orbit_step": math.radians(5),
                "roll_speed": 2.0,
                "roll_step": math.radians(5),
                "scale_in": 1,
                "scale_speed": 75,
                "scale_step": 15,
                "track_step": 20,
                "vertical_fov": math.radians(60),
            },
        ),
        _SettingsNamespace(
            "bindings",
            **{
                "camera.fit": "f",
                "camera.normal_to": "v",
                "camera.orbit": "button_middle",
                "camera.orbit.down": "down",
                "camera.orbit.left": "left",
                "camera.orbit.right": "right",
                "camera.orbit.toggle": "o",
                "camera.orbit.up": "up",
                "camera.projection.toggle": "p",
                "camera.roll": "alt+button_middle",
                "camera.roll.cw": "alt+right",
                "camera.roll.ccw": "alt+left",
                "camera.scale": "shift+button_middle",
                "camera.scale.in": "z",
                "camera.scale.out": "shift+z",
                "camera.track": "ctrl+button_middle",
                "camera.track.down": "ctrl+down",
                "camera.track.left": "ctrl+left",
                "camera.track.right": "ctrl+right",
                "camera.track.up": "ctrl+up",
                "camera.view.back": "ctrl+2",
                "camera.view.bottom": "ctrl+6",
                "camera.view.front": "ctrl+1",
                "camera.view.iso": "ctrl+7",
                "camera.view.left": "ctrl+4",
                "camera.view.right": "ctrl+3",
                "camera.view.top": "ctrl+5",
            },
        ),
    ]
)
