from configparser import RawConfigParser


def patch_config(root, name, patch_cb):
    # treat comment line as values, to have them back in output
    config = RawConfigParser(comment_prefixes=None, empty_lines_in_values=False, allow_no_value=True)

    config.optionxform = lambda option: option
    filename = '{}/resources/config-{}.properties'.format(root, name)
    config.read(filename)

    patch_cb(config)

    with open(filename, 'wt') as output_file:
        config.write(output_file)
