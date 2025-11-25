from typing import TypedDict, cast
from asgiref.sync import sync_to_async

from pycrdt import Doc, Map, create_sync_message
from pycrdt.websocket.django_channels_consumer import YjsConsumer as BaseYjsConsumer

from backend.utils import get_current_site

from . import models


# -----------------------------------------------------------------------------
# The followin types define the expected structure of the scope dictionary passed by
# Django Channels' URLRouter. The url_route.kwargs.study_design_id corresponds
# to the <str:study_design_id> parameter in websocket_urlpatterns (backend/urls.py).

class UrlRouteKwargs(TypedDict):
    study_design_id: str


class UrlRoute(TypedDict):
    kwargs: UrlRouteKwargs


class WebSocketScope(TypedDict):
    url_route: UrlRoute


# -----------------------------------------------------------------------------
# Shared room state: all consumers in the same process share these docs
# Key: room_name, Value: (ydoc, connection_count)

_room_docs: dict[str, tuple[Doc, int]] = {}


def is_member_of_the_current_site(scope) -> bool:
    if not hasattr(scope.get('user'), 'person'):
        return False

    return scope['user'].person.sites.filter(id=get_current_site(scope).id).exists()  # type: ignore


class YjsConsumer(BaseYjsConsumer):
    """
    WebSocket consumer for Y.js document synchronization.

    Persistence strategy: Single shared ydoc per room with save on last disconnect.
    All consumers in the same room share one ydoc instance, eliminating race
    conditions. Document is persisted only when the last connection leaves.

    IMPORTANT: This requires running a single Daphne worker to ensure all
    connections share the same process memory.
    """

    def __init__(self):
        super().__init__()
        self.study_design = None

    def make_room_name(self) -> str:
        scope = cast(WebSocketScope, self.scope)
        return f'study-design-map-{scope["url_route"]["kwargs"]["study_design_id"]}'

    async def make_ydoc(self) -> Doc:
        ydoc = Doc()
        if self.study_design is not None:
            doc = await sync_to_async(self.study_design.to_ydoc)()
            nodes = ydoc.get('nodes', type=Map)
            edges = ydoc.get('edges', type=Map)
            with ydoc.transaction():
                for key, value in doc['nodes'].items():
                    nodes[key] = value
                for key, value in doc['edges'].items():
                    edges[key] = value
        return ydoc

    async def connect(self):
        if not await sync_to_async(is_member_of_the_current_site)(self.scope):
            await self.close()
        else:
            try:
                scope = cast(WebSocketScope, self.scope)
                self.study_design = await models.StudyDesign.objects.aget(pk=scope['url_route']['kwargs']['study_design_id'])

                # Set up room name before checking shared docs
                self.room_name = self.make_room_name()

                # Use shared ydoc if room already exists, otherwise create new one
                if self.room_name in _room_docs:
                    self.ydoc, count = _room_docs[self.room_name]
                    _room_docs[self.room_name] = (self.ydoc, count + 1)
                else:
                    self.ydoc = await self.make_ydoc()
                    _room_docs[self.room_name] = (self.ydoc, 1)

                # Replicate base class connect() logic WITHOUT overwriting self.ydoc
                # Base class does: self.ydoc = await self.make_ydoc() - we skip that
                self._websocket_shim = self._make_websocket_shim(self.scope["path"])
                await self.channel_layer.group_add(self.room_name, self.channel_name)
                await self.accept()

                # Send sync step 1 to the new client
                sync_message = create_sync_message(self.ydoc)
                await self._websocket_shim.send(sync_message)

            except models.StudyDesign.DoesNotExist:
                await self.close()

    async def disconnect(self, code) -> None:
        if self.room_name is not None:
            if not await sync_to_async(is_member_of_the_current_site)(self.scope):
                pass  # Don't save for unauthorized users
            elif self.room_name in _room_docs:
                ydoc, count = _room_docs[self.room_name]

                if count <= 1:
                    # Last connection - save to DB and clean up
                    if self.study_design is not None:
                        nodes = ydoc.get('nodes', type=Map)
                        edges = ydoc.get('edges', type=Map)
                        doc = {
                            'nodes': dict(nodes.items()),
                            'edges': dict(edges.items()),
                        }
                        await sync_to_async(self.study_design.update_from_ydoc)(self.scope, doc)
                    del _room_docs[self.room_name]
                else:
                    # Other connections remain - just decrement count
                    _room_docs[self.room_name] = (ydoc, count - 1)

            self.ydoc = None
            await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        if not await sync_to_async(is_member_of_the_current_site)(self.scope):
            await self.close()
        else:
            await super().receive(text_data, bytes_data)
