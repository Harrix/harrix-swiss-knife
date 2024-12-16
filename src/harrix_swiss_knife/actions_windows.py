from harrix_swiss_knife import functions


class on_block_disks:
    title = "Block disks"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_block_disks.__call__

        commands = """
            manage-bde -lock E: -ForceDismount
            manage-bde -lock F: -ForceDismount
            """

        result_output = functions.run_powershell_script_as_admin(commands)
        f.add_line(result_output)
