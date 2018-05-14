import simplejson
import requests
import logging
from bson import ObjectId
from rasa_nlu.context import Context
from rasa_nlu.utility import create_response

logger = logging.getLogger(__name__)


def parse(query, project):
    data = {"q": query, "project": project}
    r = requests.get(url='http://localhost:5000/parse', params=data)
    parsed_json = simplejson.loads(r.text)
    return parsed_json


class Conversation:
    def __init__(self, parsed_json, slot_structure_json, action):
        self.context_lock = True
        self.context = Context(parsed_json, slot_structure_json, action)

    def to_json(self, slot_structure_json):
        return {"context_lock": self.context_lock, "entry_parameters": self.context.slots.slots,
                "prev_entity": self.context.prev_entity, "prev_utterance": self.context.utterance,
                "slot_structure_json": slot_structure_json}


def call_converse(request_params, rasa):
    query = request_params['q']
    conversation_id = request_params['conv_id']
    project = request_params['project']
    parsed_json = parse(query, project)
    # parsed_json = intent_entity_collection_json
    intent = parsed_json['intent']['name']
    slot_structure_json = rasa.db_connector.get_record_by_custom_filter("name", intent,
                                                                        rasa.config["slot_structure_collection"])

    action = slot_structure_json['actions']
    slot_structure_json = slot_structure_json['parameters']
    if conversation_id is not None:

        object_json = rasa.db_connector.get_record(ObjectId(conversation_id),
                                                   rasa.config["conversation_object_collection"])

        conversation = Conversation(parsed_json, object_json['slot_structure_json'], action)
        conversation.context.prev_entity = object_json["prev_entity"]
        conversation.context.utterance = object_json["prev_utterance"]
        conversation.context.slots.fill_prev_slots(object_json['entry_parameters'])
    else:
        conversation = Conversation(parsed_json, slot_structure_json, action)

    if not conversation.context_lock:
        conversation.context = Context(parsed_json, slot_structure_json, action)

    msg = conversation.context.next_action(parsed_json)
    if conversation.context.attainment:
        conversation.context_lock = False
        rasa.db_connector.delete_record(ObjectId(conversation_id), rasa.config["conversation_object_collection"])
    entry = conversation.to_json(slot_structure_json)

    if conversation_id is None:
        conversation_id = rasa.db_connector.insert_record(entry, rasa.config["conversation_object_collection"])
    else:
        rasa.db_connector.update_record(ObjectId(conversation_id), entry, rasa.config["conversation_object_collection"])

    return simplejson.dumps(create_response(query, conversation, msg, slot_structure_json, conversation_id))
