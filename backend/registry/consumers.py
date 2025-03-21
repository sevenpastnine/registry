import y_py as Y
from asgiref.sync import sync_to_async
import ypy_websocket.django_channels_consumer

from django.utils import timezone

from backend.utils import get_current_site

from . import models


def is_member_of_the_current_site(scope) -> bool:
    if not hasattr(scope.get('user'), 'person'):
        return False

    return scope['user'].person.sites.filter(id=get_current_site(scope).id).exists()  # type: ignore


class YjsConsumer(ypy_websocket.django_channels_consumer.YjsConsumer):

    def __init__(self):
        super().__init__()
        self.study_design = None
        self.last_updated_time = timezone.now()
        self.debounce_time = 1000

    def make_room_name(self) -> str:
        return f'study-design-map-{self.scope["url_route"]["kwargs"]["study_design_id"]}'

    async def make_ydoc(self) -> Y.YDoc:
        ydoc = Y.YDoc()
        if self.study_design is not None:
            doc = await sync_to_async(self.study_design.to_ydoc)()
            txn = ydoc.begin_transaction()
            try:
                ydoc.get_map('nodes').update(txn, doc['nodes'].items())
                ydoc.get_map('edges').update(txn, doc['edges'].items())
            finally:
                txn.commit()
        return ydoc

    async def connect(self):
        if not await sync_to_async(is_member_of_the_current_site)(self.scope):
            await self.close()
        else:
            try:
                self.study_design = await models.StudyDesign.objects.aget(pk=self.scope['url_route']['kwargs']['study_design_id'])
                await super().connect()
            except models.StudyDesign.DoesNotExist:
                await self.close()

    async def disconnect(self, code) -> None:
        if self.room_name is not None:
            if not await sync_to_async(is_member_of_the_current_site)(self.scope):
                # Check permission on disconnect as well to be consistent
                # No need to save changes if the user isn't authorized
                self.ydoc = None
            elif hasattr(self, 'ydoc') and self.ydoc is not None:
                # Ensure the YDoc is properly cleaned up on the same thread
                # Save any pending changes before disconnecting
                if self.study_design is not None:
                    doc = {
                        'nodes': dict(self.ydoc.get_map('nodes').items()),
                        'edges': dict(self.ydoc.get_map('edges').items()),
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
                    if message_type == 0:  # Code for document messages (awarness code is 1)
                        if timezone.now() - self.last_updated_time > timezone.timedelta(milliseconds=self.debounce_time):
                            doc = {
                                'nodes': dict(self.ydoc.get_map('nodes').items()),
                                'edges': dict(self.ydoc.get_map('edges').items()),
                            }
                            self.last_updated_time = timezone.now()
                            await sync_to_async(self.study_design.update_from_ydoc)(self.scope, doc)
