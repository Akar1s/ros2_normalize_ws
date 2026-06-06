# ROS 2 — Нормализация чисел (MinMaxScaler)

Учебный проект для **Ubuntu 24.04 + ROS 2 Jazzy + VS Code (WSL)**.

## Что внутри

Два пакета в `src/`:

| Пакет | Тип | Назначение |
|-------|-----|------------|
| `number_interfaces` | C++ (`ament_cmake`) | Описание интерфейсов: `Normalize.action`, `GetCount.srv` |
| `number_normalizer` | Python (`ament_python`) | Узлы: сервер действия, клиент действия + тесты |

### Логика (ТЗ HW4)
- **Клиент** (`normalize_client`) отправляет на сервер **массив целых чисел**.
- **Сервер** (`normalize_server`) нормализует числа по формуле MinMaxScaler
  `x_norm = (x - min) / (max - min)` и **каждое** нормализованное число шлёт в `feedback`.
- В **result** возвращается массив всех нормализованных чисел.

### Дополнительно для тестов (HW «ROS2 tests»)
Чтобы было что тестировать по всем трём механизмам, сервер также:
- публикует итоговый массив в **топик** `/normalized_numbers` (`std_msgs/Float64MultiArray`);
- предоставляет **сервис** `/get_count` (`number_interfaces/srv/GetCount`) со статистикой.

Интеграционный тест `test/test_normalize.py` (на `launch_testing`) проверяет **action, service и topic**.

---

## 1. Открытие проекта в VS Code (WSL)

1. Скопируйте папку `ros2_normalize_ws` в свою файловую систему **внутри WSL** (например `~/ros2_normalize_ws`), а не в `/mnt/c/...` — так сборка идёт быстрее и без проблем с правами.
2. В VS Code: нажмите `F1` → **WSL: Connect to WSL**, затем **File → Open Folder** → выберите `~/ros2_normalize_ws`.
3. Установите расширения **C/C++**, **Python**, **ROS** (от Microsoft), если их нет.
4. Откройте встроенный терминал (`Ctrl+` `` ` ``) — он уже будет в WSL.

---

## 2. Сборка

В терминале (из корня workspace):

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_normalize_ws
colcon build
```

> Если `number_normalizer` не видит интерфейсы — соберите интерфейсы первыми:
> `colcon build --packages-select number_interfaces` затем `colcon build`.

После каждой сборки в **новом** терминале нужно подключить overlay:

```bash
source ~/ros2_normalize_ws/install/setup.bash
```

---

## 3. Запуск и демонстрация (для видео №1, HW4)

Нужно **2 терминала** (в обоих сначала `source` overlay).

**Терминал 1 — сервер:**
```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_normalize_ws/install/setup.bash
ros2 run number_normalizer normalize_server
```

**Терминал 2 — клиент** (числа передаются аргументами; без них берётся `2 4 6 8 10`):
```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_normalize_ws/install/setup.bash
ros2 run number_normalizer normalize_client 10 20 30 40 50
```

Вы увидите, как клиент получает `Feedback [i] = ...` по каждому числу и в конце `Result (normalized): [...]`.

Полезно показать в видео и «ручную» проверку:
```bash
ros2 action list
ros2 topic echo /normalized_numbers      # в отдельном терминале до запуска клиента
ros2 service call /get_count number_interfaces/srv/GetCount
```

---

## 4. Запуск тестов (для видео №2, HW tests)

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_normalize_ws/install/setup.bash

# запустить тесты
colcon test --packages-select number_normalizer --event-handlers console_direct+

# красивый отчёт (вернёт ненулевой код, если есть падения)
colcon test-result --all --verbose
```

В выводе должны пройти три проверки: `test_action`, `test_service`, `test_topic`.
Именно вывод этих команд и записывается во второе видео.

> Альтернативно один файл напрямую:
> `python3 -m pytest src/number_normalizer/test/test_normalize.py -v`

---

## 5. Git и GitHub

```bash
cd ~/ros2_normalize_ws
git init
git add .
git commit -m "HW4: ROS2 action server/client for MinMaxScaler normalization"

# создайте пустой репозиторий на GitHub, затем:
git remote add origin https://github.com/<ваш_логин>/ros2_normalize_ws.git
git branch -M main
git push -u origin main
```

После добавления тестов (HW tests) — отдельный коммит:
```bash
git add .
git commit -m "HW tests: launch_testing tests for action, service and topic"
git push
```

---

## 6. Отправка по email

К письму приложите/вставьте: **ссылку на видео** и **ссылку на GitHub-репозиторий**.
Тему письма оформите по шаблону, принятому в вашем курсе. Пример:

```
[ROS2][HW4] Имя Фамилия, группа — action server/client (MinMaxScaler)
[ROS2][Tests] Имя Фамилия, группа — tests for topics/services/actions
```

> Уточните точный формат темы у преподавателя — «correct title» обычно означает
> конкретный шаблон курса.

---

## Запись видео в WSL

ROS 2 GUI здесь не нужен — всё в терминалах, поэтому проще всего записать экран Windows:
**Win + Alt + R** (Xbox Game Bar) или **OBS Studio**. Покажите запуск узлов / тестов и их вывод.

---

## Структура файлов

```
ros2_normalize_ws/
├── .gitignore
├── README.md
└── src/
    ├── number_interfaces/            # C++ / ament_cmake
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── action/Normalize.action
    │   └── srv/GetCount.srv
    └── number_normalizer/            # Python / ament_python
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/number_normalizer
        ├── number_normalizer/
        │   ├── __init__.py
        │   ├── normalize_server.py
        │   └── normalize_client.py
        └── test/
            └── test_normalize.py
```
