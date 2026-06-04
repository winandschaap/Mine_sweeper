from ui.pygame_ui import PygameUI


def main() -> None:
    game = PygameUI(6, 6, 8, no_check=False)
    game.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
