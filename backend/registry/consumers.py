import y_py as Y
from asgiref.sync import sync_to_async
import ypy_websocket.django_channels_consumer

from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

from . import models


async def is_member_of_the_current_site(scope) -> bool:
    if not await sync_to_async(hasattr)(scope.get('user'), 'person'):
        return False

    current_site = await sync_to_async(get_current_site)(scope)
    return await sync_to_async(
        lambda: scope['user'].person.sites.filter(id=current_site.id).exists()  # type: ignore
    )()


class YjsConsumer(ypy_websocket.django_channels_consumer.YjsConsumer):

    def __init__(self):
        super().__init__()
        self.study_design = None
        self.last_updated_time = timezone.now()
        self.last_updated_value = None
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
        if not await is_member_of_the_current_site(self.scope):
            await self.close()
        else:
            try:
                self.study_design = await models.StudyDesign.objects.aget(pk=self.scope['url_route']['kwargs']['study_design_id'])
                await super().connect()
            except models.StudyDesign.DoesNotExist:
                await self.close()

    async def disconnect(self, code) -> None:
        if self.room_name is not None:
            await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        await super().receive(text_data, bytes_data)

        if self.ydoc is not None and self.study_design is not None:
            if timezone.now() - self.last_updated_time > timezone.timedelta(milliseconds=self.debounce_time):
                doc = {
                    'nodes': dict(self.ydoc.get_map('nodes').items()),
                    'edges': dict(self.ydoc.get_map('edges').items()),
                }
                if self.last_updated_value != doc:
                    await sync_to_async(self.study_design.update_from_ydoc)(doc)
                    self.last_updated_value = doc
                    self.last_updated_time = timezone.now()
