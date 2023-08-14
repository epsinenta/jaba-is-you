from typing import List

from classes.objects import Object
from elements.global_classes import palette_manager
from settings import DEBUG


def parse_file(level_name: str, path_to_level: str) -> List[List[List[Object]]]:
    """
    Преобразует записанную в файле уровня информацию в матрицу

    :param level_name: Название желаемого уровня
    :param path_to_level: Путь к желаемому уровню
    :return: Возвращает преобразованную из файла матрицу
    """
    level_file = open(file=f'./{str(path_to_level)}/{str(level_name)}.omegapog_map_file_type_MLG_1337_228_100500_69_420',
                      mode='r', encoding='utf-8')

    level_text = level_file.read()

    level_file.close()

    lines = level_text.split('\n')
    meta = lines[0].split()

    if len(meta) > 3:
        new_file = open(file=f'./levels/{str(level_name)}.omegapog_map_file_type_MLG_1337_228_100500_69_420',
                        mode='w', encoding='utf-8')
        new_file.write('default 32 18\n' + level_text)
        new_file.close()
        return parse_file(level_name)
    if len(meta) == 1:
        new_file = open(file=f'./levels/{str(level_name)}.omegapog_map_file_type_MLG_1337_228_100500_69_420',
                        mode='w', encoding='utf-8')
        new_file.write(level_text.replace(
            lines[0], lines[0] + ' 32 18'))
        new_file.close()
        return parse_file(level_name)
    try:
        palette = palette_manager.get_palette(meta[0])
        resolution = (int(meta[1]), int(meta[2]))
    except IndexError:
        return parse_file(level_name)

    lines.pop(0)

    matrix: List[List[List[Object]]] = [[[]
                                         for _ in range(32)] for _ in range(18)]

    for line in lines:
        if DEBUG:
            print('\033[K', 'parsing ', line, end='\r')
        parameters = line.strip().split(' ')
        if len(parameters) > 1:
            matrix[int(parameters[1])][int(parameters[0])].append(Object(
                int(parameters[0]),
                int(parameters[1]),
                int(parameters[2]),
                parameters[3],
                False if parameters[4] == 'False' else True,
                palette,
                level_size=resolution,
            ))
    if DEBUG:
        print(
            f'>>>>>>>>>>>>>\nLoaded level {level_name}\nResolution: {resolution}\n' +
            f'Palette: {meta[0]}\n{len(lines)-1} objects\n>>>>>>>>>>>>>')
    return palette, resolution, matrix
