import time


RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"


def clear_screen():
    print("\033[2J\033[H", end="")


def type_text(text, color=RESET, speed=0.04):
    print(color, end="")

    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)

    print(RESET, end="")


def welcome():

    clear_screen()

    print(f"{CYAN}")

    print("╔══════════════════════════════════════╗")
    print("║                                      ║")
    print("║              WELCOME                 ║")
    print("║                 TO                   ║")
    print("║           S H E R O N  A I          ║")
    print("║                                      ║")
    print("╚══════════════════════════════════════╝")

    print(RESET)

    time.sleep(0.5)

    type_text(
        "\n        Initializing Sheron AI...\n",
        YELLOW,
        0.04
    )

    for i in range(21):

        bar = "█" * i
        empty = "░" * (20 - i)

        print(
            f"\r{BLUE}        "
            f"[{bar}{empty}] "
            f"{i * 5}%{RESET}",
            end="",
            flush=True
        )

        time.sleep(0.05)

    print("\n")

    type_text(
        "        🧠 AI Core ........ OK\n",
        GREEN,
        0.02
    )

    type_text(
        "        💾 Memory ........ OK\n",
        GREEN,
        0.02
    )

    type_text(
        "        📚 Knowledge ..... OK\n",
        GREEN,
        0.02
    )

    print()

    type_text(
        "        Welcome, bro! 🔥\n",
        CYAN,
        0.05
    )

    time.sleep(1)


if __name__ == "__main__":
      welcome()
