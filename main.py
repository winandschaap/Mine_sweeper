from ui.pygame_ui import PygameUI


def main() -> None:
    game = PygameUI(
        15,
        8,
        24  ,
        no_check=False,
        fullscreen=False,
        window_scale=0.75,
        resizable=True,
    )
    game.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
