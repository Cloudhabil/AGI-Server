import json
import os
from pathlib import Path
import tempfile
import tkinter as tk
from typing import List, Callable

from plugins.profile.badges import badge_paths, frame_paths


class PixelAvatarEditor(tk.Tk):
    """Simple pixel editor with configurable grid and basic palette."""

    def __init__(self, user_id: str, size: int = 32, pixel_size: int = 16) -> None:
        super().__init__()
        self.title(f"Pixel Avatar - {user_id}")
        self.user_id = user_id
        self.board_size = size
        self.pixel_size = pixel_size
        self.palette = [
            "#000000",
            "#ffffff",
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#ffff00",
            "#00ffff",
            "#ff00ff",
        ]
        self.selected = 0
        self.pixels = self._load_pixels()
        self.rects = [[0] * self.board_size for _ in range(self.board_size)]

        self.canvas = tk.Canvas(
            self,
            width=self.board_size * pixel_size,
            height=self.board_size * pixel_size,
            bg="white",
        )
        self.canvas.grid(row=0, column=0, columnspan=len(self.palette))
        self.reward_images: List[tk.PhotoImage] = []
        for idx, path in enumerate(frame_paths(user_id)):
            if Path(path).exists():
                img = tk.PhotoImage(file=path)
                self.reward_images.append(img)
                self.canvas.create_image(0, 0, anchor="nw", image=img)
        for idx, path in enumerate(badge_paths(user_id)):
            if Path(path).exists():
                img = tk.PhotoImage(file=path)
                self.reward_images.append(img)
                self.canvas.create_image(5 + idx * 20, 5, anchor="nw", image=img)
        for y in range(self.board_size):
            for x in range(self.board_size):
                x0 = x * pixel_size
                y0 = y * pixel_size
                rect_id = self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + pixel_size,
                    y0 + pixel_size,
                    outline="gray",
                    fill=self.palette[self.pixels[y][x]],
                )
                self.canvas.tag_bind(rect_id, "<Button-1>", self._make_paint_handler(x, y))
                self.rects[y][x] = rect_id

        palette_frame = tk.Frame(self)
        palette_frame.grid(row=1, column=0, columnspan=len(self.palette))
        for idx, color in enumerate(self.palette):
            tk.Button(
                palette_frame,
                bg=color,
                width=2,
                command=self._make_set_color_handler(idx),
            ).grid(row=0, column=idx)

        tk.Button(self, text="Save", command=self._save).grid(
            row=2, column=0, columnspan=len(self.palette)
        )

    def _load_pixels(self) -> List[List[int]]:
        base = Path(__file__).resolve().parent.parent / "plugins" / "profile" / "avatars"
        path = base / f"{self.user_id}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(
                        "pixels",
                        [[0 for _ in range(self.board_size)] for _ in range(self.board_size)],
                    )
            except Exception:
                pass
        return [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

    def _set_color(self, idx: int) -> None:
        self.selected = idx

    def _paint(self, x: int, y: int) -> None:
        self.pixels[y][x] = self.selected
        self.canvas.itemconfig(self.rects[y][x], fill=self.palette[self.selected])

    def _make_paint_handler(self, x: int, y: int) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event) -> None:
            self._paint(x, y)

        return handler

    def _make_set_color_handler(self, idx: int) -> Callable[[], None]:
        def handler() -> None:
            self._set_color(idx)

        return handler

    def _save(self) -> None:
        base = Path(__file__).resolve().parent.parent / "plugins" / "profile" / "avatars"
        base.mkdir(parents=True, exist_ok=True)
        path = base / f"{self.user_id}.json"
        with tempfile.NamedTemporaryFile("w", dir=base, delete=False, encoding="utf-8") as tmp:
            json.dump({"palette": self.palette, "pixels": self.pixels}, tmp)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)


def edit_avatar(user_id: str, size: int = 32) -> None:
    try:
        editor = PixelAvatarEditor(user_id, size)
    except tk.TclError as e:
        print(f"Failed to start GUI: {e}. Ensure a display is available.")
        return
    editor.mainloop()
