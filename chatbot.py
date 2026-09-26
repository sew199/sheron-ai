import sys
import time

from core.brain import generate_response
from core.memory import load_memory, clear_history


# ==============================
# COLORS
# ==============================

RESET = "\033[0m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RED = "\033[91m"


# ==============================
# ANIMATION SETTINGS
# ==============================

ANIMATION_SPEED = 0.03


def clear_screen():
    print("\033[2J\033[H", end="")


def type_text(text, color=RESET, speed=ANIMATION_SPEED):
    print(color, end="")

    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)

    print(RESET, end="")


def loading_bar():

    print()

    total = 25

    for i in range(total + 1):

        filled = "█" * i
        empty = "░" * (total - i)

        percent = int((i / total) * 100)

        print(
            f"\r{CYAN}[{filled}{empty}] "
            f"{percent}%{RESET}",
            end="",
            flush=True
        )

        time.sleep(0.04)

    print("\n")


def startup_animation():

    clear_screen()

    frames = [
        "S",
        "SH",
        "SHE",
        "SHER",
        "SHERO",
        "SHERON",
        "SHERON AI"
    ]

    for frame in frames:

        print(
            f"\r{CYAN}🧠 {frame}{RESET}",
            end="",
            flush=True
        )

        time.sleep(0.12)

    print("\n")

    loading_bar()

    clear_screen()

    print(f"{CYAN}")
    print("╔══════════════════════════════════════╗")
    print("║                                      ║")
    print("║          🧠  SHERON AI               ║")
    print("║                                      ║")
    print("║      Your Personal AI Assistant      ║")
    print("║                                      ║")
    print("╚══════════════════════════════════════╝")
    print(f"{RESET}")

    time.sleep(0.4)

    type_text(
        "System initialized successfully. ✓\n",
        GREEN,
        0.02
    )

    type_text(
        "Memory system loaded. ✓\n",
        GREEN,
        0.02
    )

    type_text(
        "Knowledge system loaded. ✓\n",
        GREEN,
        0.02
    )

    print()


# ==============================
# HELP
# ==============================

def show_help():

    print(f"""
{CYAN}================ SHERON AI ================{RESET}

{YELLOW}Commands:{RESET}

/help       Show this help
/memory     Show saved memory
/clear      Clear conversation history
/exit       Exit Sheron AI

Just type your question to chat.

{CYAN}============================================{RESET}
""")


# ==============================
# MEMORY
# ==============================

def show_memory():

    memory = load_memory()

    print(f"\n{MAGENTA}--- MEMORY ---{RESET}")

    profile = memory.get("profile", {})

    name = profile.get("name")

    if name:
        print(f"{GREEN}Name:{RESET} {name}")
    else:
        print(
            f"{GREEN}Name:{RESET} Not saved"
        )

    history = memory.get("history", [])

    print(
        f"{GREEN}Conversation history:{RESET} "
        f"{len(history)} messages"
    )

    print(f"{MAGENTA}--------------{RESET}\n")


# ==============================
# MAIN
# ==============================

def main():

    startup_animation()

    print(
        f"{WHITE}Type {YELLOW}/help{WHITE} "
        f"for commands.{RESET}"
    )

    print(
        f"{WHITE}Type {YELLOW}/exit{WHITE} "
        f"to quit.{RESET}\n"
    )

    while True:

        try:

            message = input(
                f"{GREEN}You:{RESET} "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print(
                f"\n{BLUE}Sheron AI:{RESET} "
                f"Bye bro! 👋"
            )

            break

        if not message:
            continue

        command = message.lower()

        # ==========================
        # EXIT
        # ==========================

        if command == "/exit":

            print(
                f"{BLUE}Sheron AI:{RESET} "
                f"Bye bro! 👋"
            )

            break

        # ==========================
        # HELP
        # ==========================

        elif command == "/help":

            show_help()

        # ==========================
        # MEMORY
        # ==========================

        elif command == "/memory":

            show_memory()

        # ==========================
        # CLEAR
        # ==========================

        elif command == "/clear":

            clear_history()

            print(
                f"{BLUE}Sheron AI:{RESET} "
                f"Conversation history cleared. 🧹"
            )

        # ==========================
        # CHAT
        # ==========================

        else:

            response = generate_response(
                message
            )

            print(
                f"\n{BLUE}Sheron AI:{RESET} ",
                end=""
            )

            type_text(
                response,
                WHITE,
                0.008
            )

            print()


# ==============================
# START
# ==============================

if __name__ == "__main__":
    main()
