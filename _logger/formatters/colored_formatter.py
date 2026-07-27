import logging


class ColoredFormatter(logging.Formatter):
    """Форматтер, который добавляет ANSI-цвета для уровней логирования."""

    # ANSI escape-коды для цветов
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    CRITICAL_EFFECT = "\033[1;30;5;41m"

    def __init__(
        self,
        fmt="[%(asctime)s] %(levelname)-8s [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ):
        super().__init__(fmt, datefmt)

        # Настраиваем цвета для каждого уровня
        self.LEVEL_COLORS = {
            logging.INFO: self.GREEN,
            logging.WARNING: self.YELLOW,
            logging.ERROR: self.RED,
            logging.CRITICAL: self.CRITICAL_EFFECT,
        }

    def format(self, record):
        # Сохраняем оригинальные значения, чтобы не испортить их для других хендлеров (например, Loki)
        orig_levelname = record.levelname
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        orig_name = record.name
        # Красим имя уровня (например, INFO становится зеленым)
        record.levelname = f"{color}{orig_levelname}{self.RESET}"

        # Дополнительно подсвечиваем время серым цветом для эстетики
        # (Опционально, можно убрать, если любите стандартный белый)
        record.asctime = (
            f"{self.GRAY}{self.formatTime(record, self.datefmt)}{self.RESET}"
        )
        record.name = f"{self.CYAN}{orig_name}{self.RESET}"
        # Вызываем базовый форматтер
        if record.levelno == logging.CRITICAL:
            record.msg = f"\033[1;31m{record.msg}{self.RESET}"
        result = super().format(record)

        # Возвращаем всё назад, чтобы не сломать сериализацию
        record.levelname = orig_levelname
        record.name = orig_name
        return result
