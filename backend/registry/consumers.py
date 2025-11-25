from typing import TypedDict, cast
from asgiref.sync import sync_to_async

from pycrdt import Doc, Map
from pycrdt.websocket.django_channels_consumer import YjsConsumer as BaseYjsConsumer

from django.utils import timezone

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


def is_member_of_the_current_site(scope) -> bool:
    if not hasattr(scope.get('user'), 'person'):
        return False

    return scope['user'].person.sites.filter(id=get_current_site(scope).id).exists()  # type: ignore


class YjsConsumer(BaseYjsConsumer):

    def __init__(self):
        super().__init__()
        self.study_design = None
        self.last_updated_time = timezone.now()
        self.debounce_time = 1000

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
                await super().connect()
            except models.StudyDesign.DoesNotExist:
                await self.close()

    async def disconnect(self, code) -> None:
        if self.room_name is not None:
            if not await sync_to_async(is_member_of_the_current_site)(self.scope):
                self.ydoc = None
            elif hasattr(self, 'ydoc') and self.ydoc is not None:
                if self.study_design is not None:
                    nodes = self.ydoc.get('nodes', type=Map)
                    edges = self.ydoc.get('edges', type=Map)
                    doc = {
                        'nodes': dict(nodes.items()),
                        'edges': dict(edges.items()),
                    }
                    await sync_to_async(self.study_design.update_from_ydoc)(self.scope, doc)
                self.ydoc = None

            await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        if not await sync_to_async(is_member_of_the_current_site)(self.scope):
            await self.close()
        else:
            await super().receive(text_data, bytes_data)

            if self.ydoc is not None and self.study_design is not None:
                if bytes_data and len(bytes_data) > 0:
                    message_type = bytes_data[0]
                    # Skip cursor-only awareness updates
                    if message_type == 0:  # Code for document messages (awareness code is 1)
                        if timezone.now() - self.last_updated_time > timezone.timedelta(milliseconds=self.debounce_time):
                            nodes = self.ydoc.get('nodes', type=Map)
                            edges = self.ydoc.get('edges', type=Map)
                            doc = {
                                'nodes': dict(nodes.items()),
                                'edges': dict(edges.items()),
                            }
                            self.last_updated_time = timezone.now()
                            await sync_to_async(self.study_design.update_from_ydoc)(self.scope, doc)
