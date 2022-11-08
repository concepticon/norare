from pathlib import Path

from clld.web.assets import environment

import norare


environment.append_path(
    Path(norare.__file__).parent.joinpath('static').as_posix(),
    url='/norare:static/')
environment.load_path = list(reversed(environment.load_path))
