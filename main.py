from ui.pygame_ui import PygameUI, get_ui_sizes


def main() -> None:
    cell_size, top_bar_height = get_ui_sizes()
    game = PygameUI(
        16,
        10,
        32,
        no_check=False,
        cell_size=cell_size,
        top_bar_height=top_bar_height,
    )
    game.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
