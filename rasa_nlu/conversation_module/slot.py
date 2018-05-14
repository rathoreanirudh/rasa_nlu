class Slots:
    def __init__(self, slot_structure_json):
        self.slots = {}
        self.slots = self.get_slots(slot_structure_json)

    def fill_slots(self, parsed_json):
        for it in range(0, len(parsed_json['entities'])):
            key = parsed_json['entities'][it]['entity']
            value = parsed_json['entities'][it]['value']
            self.slots[key] = value

    def fill_prev_slots(self, add_slots):
        print('adding slots')
        for key in add_slots:
            if add_slots[key] != '' and self.slots[key] == '':
                self.slots[key] = add_slots[key]

    def match_slots(self):
        missing_entities = []
        attainment_flag = False
        for value in self.slots:
            if self.slots[value] == '':
                missing_entities.append(value)
        if len(missing_entities) == 0:
            attainment_flag = True
        return attainment_flag, missing_entities

    @staticmethod
    def get_slots(slot_structure_json):
        """getting the slot structure for an intent"""
        slots = {}
        for it in range(0, len(slot_structure_json)):
            key = slot_structure_json[it]['name']
            slots[key] = ''
        return slots
