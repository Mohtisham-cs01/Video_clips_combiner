# Video Combiner

A simple desktop application for combining video clips.

## Features

- **Add Clips:** Select multiple video files to add to the combination list.
- **Sort by Title:** Clips are automatically sorted by title upon adding.
- **Drag-and-Drop Reordering:** Easily change the order of the clips by dragging and dropping them in the list.
- **Remove Clips:** Select one or more clips and remove them from the list.
- **Remove All:** Remove all clips from the list at once.
- **Combine:** Merge the clips in the specified order into a single video file.

## Requirements

- Python 3
- `moviepy` library
- `ffmpeg` cli tool

## Installation

1.  Make sure you have Python 3 installed on your system.
2.  Install the `moviepy` library using pip:

    ```bash
    pip install moviepy tkinter
    ```

## How to Run

1.  Save the Python script as `VideoCombiner.py`.
2.  Run the application from your terminal:

    ```bash
    python VideoCombiner.py
    ```

3.  Use the application to add, reorder, and combine your video clips.
