import { Doc } from 'yjs'
import { Server } from "@hocuspocus/server";
import { Transformer } from "@hocuspocus/transformer";
import { Webhook, Events } from "@hocuspocus/extension-webhook";

let webhookUrl: string, webhookSecret: string;

if (process.env.NODE_ENV === 'development') {
    webhookUrl = "http://localhost:8000/api/study-designs/map/";
    webhookSecret = "some-secret";
} else {
    webhookUrl = process.env.WEBHOOK_URL;
    webhookSecret = process.env.WEBHOOK_SECRET;
}

class WebhookTransformer implements Transformer {
    fromYdoc(ydoc: Doc): any {
        return {
            nodes: ydoc.getMap('nodes'),
            edges: ydoc.getMap('edges'),
            cursors: ydoc.getMap('cursors'),
        }
    }

    toYdoc(document: any, fieldName: string): Doc {
        const doc = new Doc();
        const map = doc.getMap(fieldName);
        Object.entries(document).forEach(([key, value]) => map.set(key, value));
        return doc;
    }
}

const server = Server.configure({
    port: 1234,
    debounce: 500,
    maxDebounce: 2000,
    extensions: [
        new Webhook({
            url: webhookUrl,
            secret: "secret",
            transformer: new WebhookTransformer(),
            events: [Events.onCreate, Events.onChange],
            debounce: 1000, // defaults to 2000
            debounceMaxWait: 5000, // defaults to 10000
        }),
    ],
});

server.listen();
