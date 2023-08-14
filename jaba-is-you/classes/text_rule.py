import pygame.key


class TextRule:
    def __init__(self, text, objects, prefix, infix):
        self.text_rule = text
        self.objects_in_rule = objects
        self.prefix = [prefix]
        self.infix = [infix]

    def __copy__(self):
        copied_rule = TextRule(
            text=self.text_rule,
            objects=self.objects_in_rule,
            prefix=self.prefix,
            infix=self.infix
        )
        return copied_rule

    def check_fix(self, rule_object,  matrix, level_rules):
        status_prefix = False
        status_infix = False
        if self.prefix is None:
            status_prefix = True
        else:
            for pref in self.prefix:
                if pref == 'lonely':
                    if len(matrix[rule_object.y][rule_object.x]) == 1:
                        status_prefix = True

                if pref == 'idle':
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        status_prefix = True

                if pref == 'powered':
                    if rule_object.is_power:
                        status_prefix = True

        if self.infix is None:
            status_infix = True
        else:
            for inf in self.infix:

                if inf[0] == 'on':
                    for level_object in matrix[rule_object.y][rule_object.x]:
                        if level_object.name == inf[1] and not level_object.is_text:
                            status_infix = True

                if inf[0] == 'near':
                    delta_x = 1
                    delta_y = 0
                    for i in range(9):
                        if rule_object.check_valid_range(delta_x, delta_y):
                            for level_object in matrix[rule_object.y + delta_y][rule_object.x + delta_x]:
                                if level_object.name == inf[1] and not level_object.is_text:
                                    status_infix = True
                        new_delta = self.get_new_delta(delta_x, delta_y, True)
                        delta_x = new_delta[0]
                        delta_y = new_delta[1]

                if inf[0] == 'nextto':
                    delta_x = 1
                    delta_y = 0
                    for i in range(4):
                        if rule_object.check_valid_range(delta_x, delta_y):
                            for level_object in matrix[rule_object.y + delta_y][rule_object.x + delta_x]:
                                if level_object.name == inf[1] and not level_object.is_text:
                                    status_infix = True
                        new_delta = self.get_new_delta(delta_x, delta_y, False)
                        delta_x = new_delta[0]
                        delta_y = new_delta[1]

                if inf[0] == 'facing':
                    delta_y = 0
                    delta_x = 0
                    if rule_object.direction == 1:
                        delta_x = 1
                    elif rule_object.direction == 2:
                        delta_y = 1
                    elif rule_object.direction == 3:
                        delta_x = -1
                    elif rule_object.direction == 0:
                        delta_y = -1
                    start_delta_x = delta_x
                    start_delta_y = delta_y
                    while rule_object.check_valid_range(delta_x, delta_y):
                        for level_object in matrix[rule_object.y + delta_y][rule_object.x + delta_x]:
                            if level_object.name == inf[1] and not level_object.is_text:
                                status_infix = True
                        delta_y += start_delta_y
                        delta_x += start_delta_x

                if inf[0] == 'seeing':
                    delta_y = 0
                    delta_x = 0
                    if rule_object.direction == 1:
                        delta_x = 1
                    elif rule_object.direction == 2:
                        delta_y = 1
                    elif rule_object.direction == 3:
                        delta_x = -1
                    elif rule_object.direction == 0:
                        delta_y = -1
                    start_delta_x = delta_x
                    start_delta_y = delta_y
                    status_find = True
                    while rule_object.check_valid_range(delta_x, delta_y):
                        if not status_find:
                            break
                        for level_object in matrix[rule_object.y + delta_y][rule_object.x + delta_x]:
                            if level_object.name != inf[1] and rule_object.can_interact(level_object, level_rules):
                                status_find = False
                                break
                            if level_object.name == inf[1] and not level_object.is_text:
                                status_infix = True
                        delta_y += start_delta_y
                        delta_x += start_delta_x

                if inf[0] == 'without':
                    count_objects = 0
                    for i in matrix:
                        for j in i:
                            for level_object in j:
                                if level_object.name == inf[1] and not level_object.is_text:
                                    count_objects += 1
                    if count_objects == 0:
                        status_infix = True
                    else:
                        status_infix = False

                if inf[0] == 'above':
                    for level_object in matrix[rule_object.y][rule_object.x]:
                        if level_object.name == inf[1] and not level_object.is_text:
                            if level_object.get_index(matrix) < rule_object.get_index(matrix):
                                status_infix = True

                if inf[0] == 'below':
                    for level_object in matrix[rule_object.y][rule_object.x]:
                        if level_object.name == inf[1] and not level_object.is_text:
                            if level_object.get_index(matrix) > rule_object.get_index(matrix):
                                status_infix = True

        return status_infix and status_prefix

    @staticmethod
    def get_new_delta(delta_x, delta_y, with_diagonally):
        if delta_x == 1 and delta_y == 0:
            if with_diagonally:
                delta_y = 1
            else:
                delta_x = 0
                delta_y = 1
        elif delta_x == 1 and delta_y == 1:
            delta_x = 0
        elif delta_x == 0 and delta_y == 1:
            if with_diagonally:
                delta_x = -1
            else:
                delta_x = -1
                delta_y = 0
        elif delta_x == -1 and delta_y == 1:
            delta_y = 0
        elif delta_x == -1 and delta_y == 0:
            if with_diagonally:
                delta_y = -1
            else:
                delta_y = -1
                delta_x = 0
        elif delta_x == -1 and delta_y == -1:
            delta_x = 0
        elif delta_x == 0 and delta_y == -1:
            if with_diagonally:
                delta_x = 1
            else:
                delta_x = 0
                delta_y = 0
        elif delta_x == 1 and delta_y == -1:
            delta_x = 0
            delta_y = 0

        return [delta_x, delta_y]


