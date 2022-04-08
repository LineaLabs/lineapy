from lineapy.data.types import LineaID
from lineapy.db.db import RelationalLineaDB
from lineapy.utils.analytics.event_schemas import (
    ExceptionEvent,
    LibInfo,
    LibInfoEvent,
)
from lineapy.utils.analytics.usage_tracking import do_not_track, track

__all__ = ["track", "ExceptionEvent"]


def send_lib_info_from_db(db: RelationalLineaDB, session_id: LineaID):
    if do_not_track():
        # checking earlier to avoid doing extra DB query work
        return
    import_nodes = db.get_libraries_for_session(session_id)
    libs = [LibInfo(str(n.name), str(n.version)) for n in import_nodes]
    track(LibInfoEvent(libs))
