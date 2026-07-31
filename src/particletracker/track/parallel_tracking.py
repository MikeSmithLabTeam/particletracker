
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

from . import tracking_methods as tm

# Populated once per worker process by _init_worker, not per task.
_worker_cap = None
_worker_ip = None
_worker_parameters = None
_worker_method = None
_worker_use_preprocessor = True


def _init_worker(video_filename, parameters, use_preprocessor):
    """Runs once when each worker process starts.

    use_preprocessor mirrors ParticleTracker.analyse_frame's
    `if self.ip is None` check -- when False, no Preprocessor is built
    and _track_one_frame skips process()/apply_mask() entirely, so
    results match the serial path exactly whether or not a
    preprocessor is in use.
    """
    global _worker_cap, _worker_ip, _worker_parameters, _worker_method, _worker_use_preprocessor

    # Imported lazily inside the worker to avoid pulling Qt-dependent
    # modules into the parent process import graph unnecessarily.
    from ..crop import ReadCropVideo
    from .. import preprocess

    _worker_parameters = parameters
    _worker_use_preprocessor = use_preprocessor
    _worker_cap = ReadCropVideo(parameters=parameters, filename=video_filename)
    _worker_ip = preprocess.Preprocessor(parameters) if use_preprocessor else None
    _worker_method = parameters['track']['track_method'][0]


def _track_one_frame(f):
    """Runs in a worker process. Reads, preprocesses and tracks frame f.

    Mirrors ParticleTracker.analyse_frame exactly:
    - if no preprocessor: track directly on the raw frame
    - else: preprocess, apply mask, then track

    Returns
    -------
    (int, pd.DataFrame)
        Frame index and the resulting tracking dataframe, so the main
        process can write results back out in the correct order.
    """
    frame = _worker_cap.read_frame(n=f)

    if _worker_ip is None:
        preprocessed_frame = frame
    else:
        preprocessed_frame = _worker_ip.process(frame)
        preprocessed_frame = _worker_cap.apply_mask(preprocessed_frame)

    df_frame = getattr(tm, _worker_method)(
        preprocessed_frame, frame, _worker_parameters, section='track')

    if df_frame.empty:
        for column in df_frame.columns:
            df_frame[column] = [np.nan]

    return f, df_frame


def track_frames_parallel(video_filename, parameters, frame_indices,
                           use_preprocessor=True, on_result=None,
                           max_workers=None, chunksize=None):

    frame_indices = list(frame_indices)
    if not frame_indices:
        return []

    if max_workers is None:
        max_workers = max(1, (os.cpu_count() or 1) - 1)
        max_workers = min(max_workers, len(frame_indices))
    if chunksize is None:
        chunksize = max(1, len(frame_indices) // (max_workers * 4))

    results = []
    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_init_worker,
        initargs=(video_filename, parameters, use_preprocessor),
    ) as executor:
        # map() (not submit()/as_completed()) so results come back in
        # frame_indices order despite workers finishing at different
        # times -- store.write_data / track_progress.emit downstream
        # rely on strictly increasing frame order, same as the serial loop.
        for f, df_frame in executor.map(_track_one_frame, frame_indices, chunksize=chunksize):
            if on_result is not None:
                on_result(f, df_frame)
            results.append((f, df_frame))

    return results