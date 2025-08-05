iclass EIP7928(Scene):
    def construct(self):
        # EIP identifier title
        eip_title = Text("EIP-7928: Block Access Lists", font_size=36, weight=BOLD)
        eip_title.to_edge(UP)

        # Titles: common static and dynamic part with extra gap below subtitle
        common_text = Text("I/O and Execution: ", font_size=30)
        dynamic_text = Text("today", font_size=30)
        title_group = VGroup(common_text, dynamic_text).arrange(RIGHT, buff=0.1)
        title_group.next_to(eip_title, DOWN, aligned_edge=LEFT, buff=0.6)

        # Bar parameters
        n = 4  # number of transactions
        orange_len = 3
        red_len = 2
        bar_height = 0.4
        y_start = 2
        y_gap = 1.2
        gap_between = 1  # horizontal gap between serial bars
        offsets = [i * (orange_len + red_len + gap_between) for i in range(n)]

        # Compute left margin to span full canvas
        margin = 1.5
        axis_x = -config.frame_width / 2 + margin
        axis_y_top = y_start + bar_height / 2 + 0.5
        axis_y_bottom = y_start - (n - 1) * y_gap - bar_height / 2 - 0.5

        # Draw axes (Y-axis & X-axis arrow)
        axis_vert = Line(
            start=[axis_x, axis_y_top, 0],
            end=[axis_x, axis_y_bottom, 0],
            stroke_width=3
        )
        axis_horiz = Arrow(
            start=[axis_x, axis_y_bottom, 0],
            end=[axis_x + offsets[-1] + orange_len + red_len + gap_between, axis_y_bottom, 0],
            buff=0,
            stroke_width=3
        )
        self.add(axis_vert, axis_horiz)

        # Create bars and Y-axis labels
        bars = VGroup()
        labels = VGroup()
        for i in range(n):
            y = y_start - i * y_gap
            base_x = axis_x + offsets[i]
            # Orange segment
            orange = Rectangle(
                width=orange_len,
                height=bar_height,
                fill_color=ORANGE,
                fill_opacity=1,
                stroke_width=0
            ).move_to([base_x + orange_len / 2, y, 0])
            # Red segment
            red = Rectangle(
                width=red_len,
                height=bar_height,
                fill_color=RED,
                fill_opacity=1,
                stroke_width=0
            ).next_to(orange, RIGHT, buff=0)

            bar = VGroup(orange, red)
            bars.add(bar)

            # Y-axis label placed next to each bar
            label = Text(f"Tx {i+1}", font_size=24)
            label.next_to(bar, LEFT, buff=0.3)
            labels.add(label)

        # Add EIP title, main title, bars, and labels
        self.add(eip_title, title_group, bars, labels)
        self.wait(1)

        # Prepare the "tomorrow" dynamic text, positioned exactly over "today"
        tomorrow_text = Text("tomorrow", font_size=30).set_color(ORANGE)
        tomorrow_text.move_to(dynamic_text.get_center())

        # Animate bars sliding to parallel and morph only the dynamic word
        anims = [bar.animate.shift(LEFT * offsets[i]) for i, bar in enumerate(bars)]
        self.play(
            *anims,
            Transform(dynamic_text, tomorrow_text),
            run_time=2,
        )
        self.wait(1)
