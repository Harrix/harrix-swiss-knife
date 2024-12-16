from harrix_swiss_knife import functions


class on_images_optimize:
    title = "Optimize images"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_images_optimize.__call__

        commands = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        f.add_line(result_output)
